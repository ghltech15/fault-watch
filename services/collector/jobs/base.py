"""
Base collector class for all data collection jobs.
Defines the interface and common functionality for collectors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
import hashlib
import json


class TrustTier(Enum):
    """Trust tier for data sources"""
    TIER_1_OFFICIAL = 1    # Regulators, courts, filings
    TIER_2_CREDIBLE = 2    # Major financial press
    TIER_3_SOCIAL = 3      # Social media, blogs


@dataclass
class RawData:
    """Raw data fetched from a source before parsing"""
    content: str | bytes
    url: str
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    headers: Dict[str, str] = field(default_factory=dict)
    status_code: int = 200


@dataclass
class Event:
    """
    A verified fact from a trusted source (Tier 1 or 2).
    Immutable once created - append-only event store.
    """
    event_type: str
    entity_id: Optional[UUID]
    source_id: UUID
    payload: Dict[str, Any]
    published_at: Optional[datetime] = None
    observed_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[UUID] = None
    hash: Optional[str] = None

    def compute_hash(self) -> str:
        """Generate SHA256 hash for deduplication"""
        content = json.dumps({
            'event_type': self.event_type,
            'entity_id': str(self.entity_id) if self.entity_id else None,
            'source_id': str(self.source_id),
            'payload': self.payload,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class Claim:
    """
    An unverified assertion from a social/news source (Tier 3).
    Has lifecycle: new → triage → corroborating → confirmed/debunked → stale
    """
    entity_id: Optional[UUID]
    claim_text: str
    claim_type: str  # nationalization|investigation|liquidity|delivery|fraud
    source_id: UUID
    url: Optional[str] = None
    author: Optional[str] = None
    engagement: int = 0
    credibility_score: int = 50
    status: str = 'new'
    status_changed_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[UUID] = None


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.

    Each collector must:
    1. Define source_name and trust_tier
    2. Implement fetch() to retrieve raw data
    3. Implement parse() to convert raw data to Events or Claims
    """

    source_name: str = "Unknown"
    trust_tier: TrustTier = TrustTier.TIER_3_SOCIAL
    source_id: Optional[UUID] = None

    # Collection frequency (in minutes)
    frequency_minutes: int = 60

    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: int = 30

    def __init__(self, fetcher: 'Fetcher' = None, db: 'EventStore' = None):
        self.fetcher = fetcher
        self.db = db
        self._last_run: Optional[datetime] = None
        self._error_count: int = 0

    @abstractmethod
    async def fetch(self) -> List[RawData]:
        """
        Fetch raw data from the source.
        Returns list of RawData objects.
        """
        pass

    @abstractmethod
    def parse(self, raw: RawData) -> List[Event | Claim]:
        """
        Parse raw data into Events or Claims.
        Tier 1 sources → Events only
        Tier 2 sources → Events + optional Claims
        Tier 3 sources → Claims only
        """
        pass

    async def collect(self) -> Dict[str, int]:
        """
        Main collection workflow:
        1. Fetch raw data
        2. Parse into Events/Claims
        3. Store to database
        4. Return counts
        """
        results = {
            'events_created': 0,
            'claims_created': 0,
            'duplicates_skipped': 0,
            'errors': 0,
        }

        try:
            raw_data_list = await self.fetch()

            for raw in raw_data_list:
                try:
                    items = self.parse(raw)

                    for item in items:
                        if isinstance(item, Event):
                            # Compute hash for deduplication
                            item.hash = item.compute_hash()

                            # Store event (skip if hash exists)
                            if self.db:
                                stored = await self.db.store_event(item)
                                if stored:
                                    results['events_created'] += 1
                                else:
                                    results['duplicates_skipped'] += 1
                            else:
                                results['events_created'] += 1

                        elif isinstance(item, Claim):
                            if self.db:
                                await self.db.store_claim(item)
                            results['claims_created'] += 1

                except Exception as e:
                    results['errors'] += 1
                    print(f"[{self.source_name}] Parse error: {e}")

            self._last_run = datetime.utcnow()
            self._error_count = 0

        except Exception as e:
            results['errors'] += 1
            self._error_count += 1
            print(f"[{self.source_name}] Fetch error: {e}")

        return results

    def should_run(self) -> bool:
        """Check if collector should run based on frequency"""
        if self._last_run is None:
            return True

        elapsed = (datetime.utcnow() - self._last_run).total_seconds() / 60
        return elapsed >= self.frequency_minutes

    def get_status(self) -> Dict[str, Any]:
        """Return collector status for monitoring"""
        return {
            'source_name': self.source_name,
            'trust_tier': self.trust_tier.value,
            'frequency_minutes': self.frequency_minutes,
            'last_run': self._last_run.isoformat() if self._last_run else None,
            'error_count': self._error_count,
            'healthy': self._error_count < self.max_retries,
        }
