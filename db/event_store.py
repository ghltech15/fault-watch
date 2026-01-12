"""
Event Store - PostgreSQL interface for the event-sourcing architecture.
"""

import os
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from uuid import UUID
import asyncio
import json

try:
    import asyncpg
except ImportError:
    asyncpg = None


class EventStore:
    """
    PostgreSQL-based event store for fault.watch.

    Handles:
    - Entity CRUD and resolution
    - Event storage with deduplication
    - Claim lifecycle management
    - Score computation and storage
    """

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://faultwatch:faultwatch_dev@localhost:5432/faultwatch_events'
        )
        self._pool: Optional['asyncpg.Pool'] = None

    async def connect(self):
        """Create connection pool"""
        if asyncpg is None:
            raise ImportError("asyncpg required: pip install asyncpg")

        self._pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10,
        )

    async def close(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()

    async def execute(self, query: str, *args) -> str:
        """Execute a query"""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict]:
        """Fetch multiple rows"""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetchrow(self, query: str, *args) -> Optional[Dict]:
        """Fetch single row"""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetchval(self, query: str, *args) -> Any:
        """Fetch single value"""
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    # ==================== Entities ====================

    async def get_entity_by_id(self, entity_id: UUID) -> Optional[Dict]:
        """Get entity by ID"""
        return await self.fetchrow(
            "SELECT * FROM entities WHERE id = $1",
            entity_id
        )

    async def get_entity_by_cik(self, cik: str) -> Optional[Dict]:
        """Get entity by SEC CIK"""
        return await self.fetchrow(
            "SELECT * FROM entities WHERE cik = $1",
            cik
        )

    async def get_entity_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get entity by ticker symbol"""
        return await self.fetchrow(
            "SELECT * FROM entities WHERE $1 = ANY(tickers)",
            ticker.upper()
        )

    async def get_entity_by_name(self, name: str) -> Optional[Dict]:
        """Get entity by name or alias"""
        return await self.fetchrow(
            """
            SELECT * FROM entities
            WHERE name ILIKE $1 OR $1 = ANY(aliases)
            """,
            name
        )

    async def resolve_entity(self, identifier: str) -> Optional[Dict]:
        """
        Resolve entity from any identifier (CIK, ticker, name, alias).
        Returns first match.
        """
        # Try CIK first (exact match)
        if identifier.isdigit() or identifier.startswith('000'):
            entity = await self.get_entity_by_cik(identifier)
            if entity:
                return entity

        # Try ticker (case-insensitive)
        entity = await self.get_entity_by_ticker(identifier.upper())
        if entity:
            return entity

        # Try name/alias
        return await self.get_entity_by_name(identifier)

    async def get_all_banks(self) -> List[Dict]:
        """Get all bank entities"""
        return await self.fetch(
            "SELECT * FROM entities WHERE entity_type = 'bank' ORDER BY name"
        )

    # ==================== Sources ====================

    async def get_source_by_name(self, name: str) -> Optional[Dict]:
        """Get source by name"""
        return await self.fetchrow(
            "SELECT * FROM sources WHERE name = $1",
            name
        )

    async def get_sources_by_tier(self, tier: int) -> List[Dict]:
        """Get all sources of a trust tier"""
        return await self.fetch(
            "SELECT * FROM sources WHERE trust_tier = $1::trust_tier AND active = true",
            str(tier)
        )

    async def update_source_status(self, source_id: UUID, success: bool):
        """Update source fetch status"""
        if success:
            await self.execute(
                """
                UPDATE sources
                SET last_successful_fetch = NOW(), consecutive_failures = 0
                WHERE id = $1
                """,
                source_id
            )
        else:
            await self.execute(
                """
                UPDATE sources
                SET consecutive_failures = consecutive_failures + 1
                WHERE id = $1
                """,
                source_id
            )

    # ==================== Events ====================

    async def store_event(
        self,
        event_type: str,
        source_id: UUID,
        payload: Dict,
        entity_id: UUID = None,
        published_at: datetime = None,
        event_hash: str = None,
    ) -> Optional[UUID]:
        """
        Store an event. Returns event ID if stored, None if duplicate.
        """
        try:
            result = await self.fetchval(
                """
                INSERT INTO events (event_type, entity_id, source_id, payload, published_at, hash)
                VALUES ($1::event_type, $2, $3, $4, $5, $6)
                ON CONFLICT (hash) DO NOTHING
                RETURNING id
                """,
                event_type,
                entity_id,
                source_id,
                json.dumps(payload),
                published_at,
                event_hash
            )
            return result
        except Exception as e:
            # Handle case where event_type doesn't exist in enum
            if 'invalid input value for enum event_type' in str(e):
                # Fall back to 'custom' type
                result = await self.fetchval(
                    """
                    INSERT INTO events (event_type, entity_id, source_id, payload, published_at, hash)
                    VALUES ('custom', $1, $2, $3, $4, $5)
                    ON CONFLICT (hash) DO NOTHING
                    RETURNING id
                    """,
                    entity_id,
                    source_id,
                    json.dumps(payload),
                    published_at,
                    event_hash
                )
                return result
            raise

    async def get_events(
        self,
        entity_id: UUID = None,
        event_type: str = None,
        since: datetime = None,
        until: datetime = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Query events with filters"""
        conditions = []
        params = []
        param_idx = 1

        if entity_id:
            conditions.append(f"entity_id = ${param_idx}")
            params.append(entity_id)
            param_idx += 1

        if event_type:
            conditions.append(f"event_type = ${param_idx}::event_type")
            params.append(event_type)
            param_idx += 1

        if since:
            conditions.append(f"observed_at >= ${param_idx}")
            params.append(since)
            param_idx += 1

        if until:
            conditions.append(f"observed_at <= ${param_idx}")
            params.append(until)
            param_idx += 1

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT e.*, ent.name as entity_name, s.name as source_name, s.trust_tier
            FROM events e
            LEFT JOIN entities ent ON e.entity_id = ent.id
            JOIN sources s ON e.source_id = s.id
            WHERE {where_clause}
            ORDER BY e.observed_at DESC
            LIMIT ${param_idx}
        """
        params.append(limit)

        return await self.fetch(query, *params)

    async def get_recent_events(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """Get events from last N days"""
        return await self.fetch(
            """
            SELECT * FROM recent_events
            LIMIT $1
            """,
            limit
        )

    # ==================== Claims ====================

    async def store_claim(
        self,
        entity_id: UUID,
        source_id: UUID,
        claim_text: str,
        claim_type: str,
        url: str = None,
        author: str = None,
        engagement: int = 0,
        credibility_score: int = None,
        credibility_factors: Dict = None,
    ) -> UUID:
        """Store a claim"""
        return await self.fetchval(
            """
            INSERT INTO claims (
                entity_id, source_id, claim_text, claim_type,
                url, author, engagement, credibility_score, credibility_factors
            )
            VALUES ($1, $2, $3, $4::claim_type, $5, $6, $7, $8, $9)
            RETURNING id
            """,
            entity_id,
            source_id,
            claim_text,
            claim_type,
            url,
            author,
            engagement,
            credibility_score,
            json.dumps(credibility_factors or {}),
        )

    async def update_claim_status(
        self,
        claim_id: UUID,
        status: str,
        reason: str = None
    ):
        """Update claim status"""
        await self.execute(
            """
            UPDATE claims
            SET status = $2::claim_status, status_reason = $3
            WHERE id = $1
            """,
            claim_id,
            status,
            reason
        )

    async def get_claims_for_triage(self, limit: int = 50) -> List[Dict]:
        """Get claims awaiting triage"""
        return await self.fetch(
            "SELECT * FROM claims_triage_queue LIMIT $1",
            limit
        )

    async def get_claims_by_entity(
        self,
        entity_id: UUID,
        status: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get claims for an entity"""
        if status:
            return await self.fetch(
                """
                SELECT * FROM claims
                WHERE entity_id = $1 AND status = $2::claim_status
                ORDER BY created_at DESC
                LIMIT $3
                """,
                entity_id, status, limit
            )
        return await self.fetch(
            """
            SELECT * FROM claims
            WHERE entity_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """,
            entity_id, limit
        )

    # ==================== Corroborations ====================

    async def create_corroboration(
        self,
        claim_id: UUID,
        event_id: UUID,
        confidence: float,
        reason: str = None,
        matched_by: str = 'auto'
    ) -> UUID:
        """Create a corroboration link"""
        return await self.fetchval(
            """
            INSERT INTO corroborations (claim_id, event_id, match_confidence, match_reason, matched_by)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (claim_id, event_id) DO UPDATE
            SET match_confidence = $3, match_reason = $4
            RETURNING id
            """,
            claim_id, event_id, confidence, reason, matched_by
        )

    async def get_corroborations_for_claim(self, claim_id: UUID) -> List[Dict]:
        """Get all corroborating events for a claim"""
        return await self.fetch(
            """
            SELECT cor.*, e.event_type, e.payload, e.observed_at
            FROM corroborations cor
            JOIN events e ON cor.event_id = e.id
            WHERE cor.claim_id = $1
            ORDER BY cor.match_confidence DESC
            """,
            claim_id
        )

    # ==================== Scores ====================

    async def store_daily_score(
        self,
        score_date: date,
        entity_id: UUID,
        funding_stress: float,
        enforcement_heat: float,
        deliverability_stress: float,
        composite_risk: float,
        cascade_triggered: bool,
        explain: Dict
    ):
        """Store or update daily score for an entity"""
        await self.execute(
            """
            INSERT INTO scores_daily (
                date, entity_id, funding_stress, enforcement_heat,
                deliverability_stress, composite_risk, cascade_triggered, explain_json
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (date, entity_id) DO UPDATE
            SET funding_stress = $3, enforcement_heat = $4,
                deliverability_stress = $5, composite_risk = $6,
                cascade_triggered = $7, explain_json = $8, computed_at = NOW()
            """,
            score_date,
            entity_id,
            funding_stress,
            enforcement_heat,
            deliverability_stress,
            composite_risk,
            cascade_triggered,
            json.dumps(explain),
        )

    async def store_market_score(
        self,
        score_date: date,
        overall_risk: float,
        funding_avg: float,
        enforcement_avg: float,
        deliverability_avg: float,
        banks_in_stress: int,
        banks_in_danger: int,
        banks_in_crisis: int,
        cascade_stage: int,
        cascade_description: str,
        indicators: Dict
    ):
        """Store or update market-wide score"""
        await self.execute(
            """
            INSERT INTO scores_market (
                date, overall_risk, funding_stress_avg, enforcement_heat_avg,
                deliverability_stress_avg, banks_in_stress, banks_in_danger,
                banks_in_crisis, cascade_stage, cascade_description, indicators
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (date) DO UPDATE
            SET overall_risk = $2, funding_stress_avg = $3, enforcement_heat_avg = $4,
                deliverability_stress_avg = $5, banks_in_stress = $6, banks_in_danger = $7,
                banks_in_crisis = $8, cascade_stage = $9, cascade_description = $10,
                indicators = $11, computed_at = NOW()
            """,
            score_date,
            overall_risk,
            funding_avg,
            enforcement_avg,
            deliverability_avg,
            banks_in_stress,
            banks_in_danger,
            banks_in_crisis,
            cascade_stage,
            cascade_description,
            json.dumps(indicators),
        )

    async def get_latest_entity_scores(self) -> List[Dict]:
        """Get latest scores for all entities"""
        return await self.fetch("SELECT * FROM latest_entity_scores")

    async def get_latest_market_score(self) -> Optional[Dict]:
        """Get latest market-wide score"""
        return await self.fetchrow("SELECT * FROM latest_market_score")

    async def get_entity_score_history(
        self,
        entity_id: UUID,
        days: int = 30
    ) -> List[Dict]:
        """Get score history for an entity"""
        return await self.fetch(
            """
            SELECT * FROM scores_daily
            WHERE entity_id = $1 AND date >= CURRENT_DATE - $2
            ORDER BY date DESC
            """,
            entity_id, days
        )


# Global instance
_event_store: Optional[EventStore] = None


async def get_event_store() -> EventStore:
    """Get or create event store instance"""
    global _event_store
    if _event_store is None:
        _event_store = EventStore()
        await _event_store.connect()
    return _event_store
