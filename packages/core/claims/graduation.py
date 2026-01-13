"""
Claim Graduation Engine

Manages claim lifecycle and attempts to corroborate claims with Tier-1 events.

Claim Lifecycle:
new → triage → corroborating → confirmed/debunked → stale
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID


class ClaimStatus(Enum):
    """Claim lifecycle status"""
    NEW = 'new'                      # Just captured
    TRIAGE = 'triage'                # Being evaluated
    CORROBORATING = 'corroborating'  # Searching for Tier-1 match
    CONFIRMED = 'confirmed'          # Matched to Tier-1 event
    DEBUNKED = 'debunked'            # Contradicted by evidence
    STALE = 'stale'                  # No match after timeout


@dataclass
class StoredClaim:
    """Claim as stored in database"""
    id: UUID
    entity_id: Optional[UUID]
    claim_text: str
    claim_type: str
    source_id: UUID
    url: Optional[str]
    author: Optional[str]
    engagement: int
    credibility_score: int
    status: ClaimStatus
    status_changed_at: datetime
    created_at: datetime
    status_reason: Optional[str] = None


@dataclass
class StoredEvent:
    """Event as stored in database"""
    id: UUID
    event_type: str
    entity_id: Optional[UUID]
    source_id: UUID
    payload: Dict[str, Any]
    observed_at: datetime


@dataclass
class CorroborationMatch:
    """A potential corroboration between claim and event"""
    claim_id: UUID
    event_id: UUID
    confidence: float  # 0-1
    match_reason: str
    matched_fields: List[str]


# Claim type to event type mapping for corroboration
CLAIM_EVENT_MAPPING = {
    'nationalization': ['bank_failure', 'regulator_action', 'fed_facility_usage'],
    'investigation': ['regulator_action', 'wells_notice', 'sec_filing'],
    'liquidity': ['bank_failure', 'fed_facility_usage', 'deposit_stress'],
    'delivery': ['comex_stress', 'comex_outflow', 'comex_delivery_spike'],
    'fraud': ['regulator_action', 'penalty', 'settlement'],
    'insider': ['sec_filing', 'regulator_action', 'covered_action'],
    'price_target': [],  # No corroboration possible
}


class ClaimGraduationEngine:
    """
    Manages claim graduation through lifecycle.

    Features:
    - Automatic triage based on credibility
    - Corroboration matching with Tier-1 events
    - Stale claim detection (7-day timeout)
    - Debunking when evidence contradicts
    """

    def __init__(
        self,
        db=None,
        corroboration_window_days: int = 7,
        stale_timeout_days: int = 7,
        min_credibility_for_triage: int = 40,
        min_credibility_for_corroboration: int = 60,
    ):
        self.db = db
        self.corroboration_window_days = corroboration_window_days
        self.stale_timeout_days = stale_timeout_days
        self.min_credibility_for_triage = min_credibility_for_triage
        self.min_credibility_for_corroboration = min_credibility_for_corroboration

    def process_new_claim(self, claim: StoredClaim) -> Tuple[ClaimStatus, str]:
        """
        Process a new claim and determine initial status.

        Returns: (new_status, reason)
        """
        # Low credibility stays in NEW
        if claim.credibility_score < self.min_credibility_for_triage:
            return ClaimStatus.NEW, "Low credibility, monitoring only"

        # Medium credibility goes to TRIAGE
        if claim.credibility_score < self.min_credibility_for_corroboration:
            return ClaimStatus.TRIAGE, "Medium credibility, awaiting review"

        # High credibility goes to CORROBORATING
        return ClaimStatus.CORROBORATING, "High credibility, searching for corroboration"

    def find_corroborating_events(
        self,
        claim: StoredClaim,
        events: List[StoredEvent],
    ) -> List[CorroborationMatch]:
        """
        Find events that might corroborate a claim.

        Matching criteria:
        1. Event type matches claim type mapping
        2. Entity matches (if both have entity)
        3. Timing within window
        """
        matches = []
        window_start = claim.created_at - timedelta(days=self.corroboration_window_days)

        # Get relevant event types for this claim type
        relevant_event_types = CLAIM_EVENT_MAPPING.get(claim.claim_type, [])
        if not relevant_event_types:
            return matches

        for event in events:
            # Check timing
            if event.observed_at < window_start:
                continue

            # Check event type
            if event.event_type not in relevant_event_types:
                continue

            # Calculate match confidence
            confidence, reason, matched_fields = self._calculate_match_confidence(
                claim, event
            )

            if confidence >= 0.5:  # Minimum threshold
                matches.append(CorroborationMatch(
                    claim_id=claim.id,
                    event_id=event.id,
                    confidence=confidence,
                    match_reason=reason,
                    matched_fields=matched_fields,
                ))

        # Sort by confidence
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches

    def _calculate_match_confidence(
        self,
        claim: StoredClaim,
        event: StoredEvent,
    ) -> Tuple[float, str, List[str]]:
        """Calculate confidence that event corroborates claim"""
        confidence = 0.5  # Base
        reasons = []
        matched_fields = []

        # Entity match (strong signal)
        if claim.entity_id and event.entity_id:
            if claim.entity_id == event.entity_id:
                confidence += 0.3
                reasons.append("Entity match")
                matched_fields.append("entity_id")
            else:
                confidence -= 0.2
                reasons.append("Entity mismatch")

        # Event type specificity
        event_type = event.event_type
        if event_type in ['regulator_action', 'bank_failure']:
            confidence += 0.1
            reasons.append(f"Strong event type: {event_type}")
            matched_fields.append("event_type")

        # Timing (closer is better)
        days_diff = abs((event.observed_at - claim.created_at).days)
        if days_diff <= 1:
            confidence += 0.1
            reasons.append("Same-day timing")
        elif days_diff <= 3:
            confidence += 0.05

        # Payload keywords (if claim text matches payload)
        claim_words = set(claim.claim_text.lower().split())
        payload_text = str(event.payload).lower()
        matching_words = sum(1 for w in claim_words if len(w) > 4 and w in payload_text)
        if matching_words >= 3:
            confidence += 0.1
            reasons.append("Keyword overlap")
            matched_fields.append("payload_keywords")

        reason = "; ".join(reasons) if reasons else "Pattern match"
        return min(confidence, 1.0), reason, matched_fields

    def graduate_claim(
        self,
        claim: StoredClaim,
        match: CorroborationMatch,
    ) -> Tuple[ClaimStatus, str]:
        """Graduate claim to CONFIRMED based on corroboration"""
        return (
            ClaimStatus.CONFIRMED,
            f"Corroborated by event {match.event_id} (confidence: {match.confidence:.0%})"
        )

    def check_stale_claims(
        self,
        claims: List[StoredClaim],
    ) -> List[Tuple[UUID, ClaimStatus, str]]:
        """
        Check for claims that should be marked stale.

        Returns list of (claim_id, new_status, reason)
        """
        updates = []
        now = datetime.utcnow()
        cutoff = now - timedelta(days=self.stale_timeout_days)

        for claim in claims:
            if claim.status in (ClaimStatus.NEW, ClaimStatus.TRIAGE, ClaimStatus.CORROBORATING):
                if claim.created_at < cutoff:
                    updates.append((
                        claim.id,
                        ClaimStatus.STALE,
                        f"No corroboration within {self.stale_timeout_days} days"
                    ))

        return updates

    def debunk_claim(
        self,
        claim: StoredClaim,
        contradicting_evidence: str,
    ) -> Tuple[ClaimStatus, str]:
        """Mark claim as debunked"""
        return (
            ClaimStatus.DEBUNKED,
            f"Contradicted by: {contradicting_evidence}"
        )


def get_claim_display_info(status: ClaimStatus) -> Dict[str, str]:
    """Get display info for claim status"""
    display_map = {
        ClaimStatus.NEW: {
            'label': 'UNVERIFIED',
            'color': 'gray',
            'icon': '○',
            'description': 'New claim, not yet evaluated',
        },
        ClaimStatus.TRIAGE: {
            'label': 'UNVERIFIED',
            'color': 'yellow',
            'icon': '⚠',
            'description': 'Under evaluation',
        },
        ClaimStatus.CORROBORATING: {
            'label': 'UNVERIFIED',
            'color': 'yellow',
            'icon': '⚠',
            'description': 'Searching for confirmation',
        },
        ClaimStatus.CONFIRMED: {
            'label': 'CONFIRMED',
            'color': 'green',
            'icon': '✓',
            'description': 'Corroborated by official source',
        },
        ClaimStatus.DEBUNKED: {
            'label': 'DEBUNKED',
            'color': 'red',
            'icon': '✗',
            'description': 'Contradicted by evidence',
        },
        ClaimStatus.STALE: {
            'label': 'STALE',
            'color': 'gray',
            'icon': '○',
            'description': 'No confirmation found',
        },
    }
    return display_map.get(status, display_map[ClaimStatus.NEW])


def format_claim_for_display(
    claim_text: str,
    status: ClaimStatus,
    credibility_score: int,
    source_name: str,
) -> Dict[str, Any]:
    """Format claim for frontend display"""
    info = get_claim_display_info(status)
    return {
        'text': claim_text,
        'label': info['label'],
        'badge_color': info['color'],
        'icon': info['icon'],
        'description': info['description'],
        'source': source_name,
        'credibility': credibility_score,
        'can_display_as_fact': status == ClaimStatus.CONFIRMED,
    }
