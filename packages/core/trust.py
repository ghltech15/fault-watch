"""
Trust Tier Verification Policy

Defines the three-tier trust system for data sources:
- Tier 1: Official sources (SEC, CFTC, OCC, FDIC, Fed, Courts) → Creates EVENTS (facts)
- Tier 2: Credible sources (Reuters, Bloomberg, WSJ, FT) → Creates EVENTS + optional CLAIMS
- Tier 3: Social sources (Reddit, Twitter, TikTok, Blogs) → Creates CLAIMS only (unverified)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
import hashlib
import json


class TrustTier(Enum):
    """Trust tier classification for data sources"""
    TIER_1_OFFICIAL = 1    # Regulators, courts, filings - Creates EVENTS
    TIER_2_CREDIBLE = 2    # Major financial press - Creates EVENTS + CLAIMS
    TIER_3_SOCIAL = 3      # Social media, blogs - Creates CLAIMS only

    @property
    def label(self) -> str:
        labels = {
            1: "Official",
            2: "Credible Press",
            3: "Social",
        }
        return labels[self.value]

    @property
    def creates_events(self) -> bool:
        """Whether this tier creates verified events"""
        return self.value <= 2

    @property
    def creates_claims(self) -> bool:
        """Whether this tier creates claims (for verification)"""
        return self.value >= 2


# Source classifications
TIER_1_SOURCES = {
    # SEC
    'SEC EDGAR',
    'SEC Enforcement',
    'SEC Whistleblower',
    # Other regulators
    'CFTC Enforcement',
    'OCC Enforcement',
    'FDIC Bank Failures',
    # Fed
    'Fed H.4.1',
    'FRED',
    # Market data
    'CME COMEX',
    # Court records
    'PACER',
    'CourtListener',
}

TIER_2_SOURCES = {
    # Wire services
    'Reuters',
    'Reuters Finance',
    'Bloomberg',
    'Bloomberg Markets',
    'Associated Press',
    # Major newspapers
    'Wall Street Journal',
    'Financial Times',
    'New York Times',
    'Washington Post',
    # Financial data providers
    'Finnhub',
    'Yahoo Finance',
    # Commodities
    'Kitco News',
    'Kitco',
    # Dealers (for pricing)
    'JM Bullion',
    'APMEX',
    'SD Bullion',
}

TIER_3_SOURCES = {
    # Reddit
    'Reddit WSS',
    'Reddit Silverbugs',
    'Reddit Gold',
    'Reddit WallStreetBets',
    # Alternative media
    'ZeroHedge',
    'SilverSeek',
    'GoldSeek',
    # Social platforms
    'Twitter',
    'X',
    'TikTok',
    # Blogs
    'TFMetals',
    'SilverDoctors',
}


def get_trust_tier(source_name: str) -> TrustTier:
    """Determine trust tier for a source by name"""
    if source_name in TIER_1_SOURCES:
        return TrustTier.TIER_1_OFFICIAL
    elif source_name in TIER_2_SOURCES:
        return TrustTier.TIER_2_CREDIBLE
    else:
        return TrustTier.TIER_3_SOCIAL


@dataclass
class Event:
    """
    A verified fact from a trusted source (Tier 1 or 2).
    Immutable once created - append-only event store.
    """
    event_type: str
    source_id: UUID
    payload: Dict[str, Any]
    entity_id: Optional[UUID] = None
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
    claim_text: str
    claim_type: str  # nationalization|investigation|liquidity|delivery|fraud
    source_id: UUID
    entity_id: Optional[UUID] = None
    url: Optional[str] = None
    author: Optional[str] = None
    engagement: int = 0
    credibility_score: int = 50
    credibility_factors: Dict[str, Any] = field(default_factory=dict)
    status: str = 'new'
    status_changed_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[UUID] = None


# Claim status lifecycle
class ClaimStatus(Enum):
    NEW = 'new'                    # Just captured, not yet triaged
    TRIAGE = 'triage'              # Being evaluated
    CORROBORATING = 'corroborating'  # Actively searching for Tier 1 confirmation
    CONFIRMED = 'confirmed'        # Corroborated by Tier 1 event
    DEBUNKED = 'debunked'          # Contradicted by Tier 1 evidence
    STALE = 'stale'                # No corroboration after timeout (7 days)


# Claim type classification
CLAIM_TYPES = {
    'nationalization': {
        'patterns': [
            r'nationalized?',
            r'government takeover',
            r'state control',
            r'bailout',
            r'bail[\s-]?out',
            r'rescue package',
        ],
        'severity': 'critical',
    },
    'investigation': {
        'patterns': [
            r'investigation',
            r'probe',
            r'subpoena',
            r'Wells notice',
            r'inquiry',
            r'examination',
            r'audit',
        ],
        'severity': 'high',
    },
    'liquidity': {
        'patterns': [
            r'bank run',
            r'liquidity crisis',
            r'withdrawal',
            r'deposit flight',
            r'insolvency',
            r'bankruptcy',
            r'default',
        ],
        'severity': 'critical',
    },
    'delivery': {
        'patterns': [
            r'delivery failure',
            r'can\'t deliver',
            r'no silver',
            r'no gold',
            r'empty vault',
            r'shortage',
            r'force majeure',
        ],
        'severity': 'high',
    },
    'fraud': {
        'patterns': [
            r'fraud',
            r'manipulation',
            r'spoofing',
            r'rigged',
            r'naked short',
            r'paper silver',
            r'paper gold',
        ],
        'severity': 'medium',
    },
    'insider': {
        'patterns': [
            r'insider',
            r'whistleblower',
            r'leaked',
            r'confidential',
            r'source says',
        ],
        'severity': 'medium',
    },
    'price_target': {
        'patterns': [
            r'will hit \$',
            r'target price',
            r'price prediction',
            r'going to \$',
            r'moon',
            r'squeeze',
        ],
        'severity': 'low',
    },
}


def process_source_data(
    source_name: str,
    source_id: UUID,
    data: Dict[str, Any],
    entity_id: Optional[UUID] = None,
) -> Union[Event, Claim, Tuple[Event, Claim]]:
    """
    Process data from a source according to its trust tier.

    Returns:
        - Event for Tier 1
        - Event + Claim for Tier 2
        - Claim for Tier 3
    """
    tier = get_trust_tier(source_name)

    if tier == TrustTier.TIER_1_OFFICIAL:
        # Tier 1: Create verified event
        return create_event_from_data(source_id, data, entity_id)

    elif tier == TrustTier.TIER_2_CREDIBLE:
        # Tier 2: Create event + claim for cross-verification
        event = create_event_from_data(source_id, data, entity_id)
        claim = create_claim_from_data(source_id, data, entity_id)
        return (event, claim)

    else:  # TIER_3_SOCIAL
        # Tier 3: Create claim only
        return create_claim_from_data(source_id, data, entity_id)


def create_event_from_data(
    source_id: UUID,
    data: Dict[str, Any],
    entity_id: Optional[UUID] = None,
) -> Event:
    """Create an Event from raw data"""
    event_type = data.get('event_type', 'custom')
    published_at = data.get('published_at')

    if isinstance(published_at, str):
        published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))

    return Event(
        event_type=event_type,
        source_id=source_id,
        payload=data.get('payload', data),
        entity_id=entity_id,
        published_at=published_at,
    )


def create_claim_from_data(
    source_id: UUID,
    data: Dict[str, Any],
    entity_id: Optional[UUID] = None,
) -> Claim:
    """Create a Claim from raw data"""
    import re

    # Extract text content
    text = data.get('text') or data.get('title') or data.get('content', '')

    # Detect claim type from patterns
    claim_type = 'other'
    for ctype, config in CLAIM_TYPES.items():
        for pattern in config['patterns']:
            if re.search(pattern, text, re.IGNORECASE):
                claim_type = ctype
                break
        if claim_type != 'other':
            break

    return Claim(
        claim_text=text[:500],  # Truncate for storage
        claim_type=claim_type,
        source_id=source_id,
        entity_id=entity_id,
        url=data.get('url'),
        author=data.get('author'),
        engagement=data.get('engagement', 0) or data.get('score', 0),
    )


def validate_tier_1_event(event: Event) -> List[str]:
    """
    Validate that a Tier 1 event meets quality requirements.
    Returns list of validation errors (empty if valid).
    """
    errors = []

    if not event.event_type:
        errors.append("Event type is required")

    if not event.source_id:
        errors.append("Source ID is required")

    if not event.payload:
        errors.append("Payload is required")

    # Check for required fields in payload based on event type
    required_fields = {
        'regulator_action': ['action_type', 'description'],
        'bank_failure': ['bank_name', 'failure_date'],
        'sec_filing': ['form_type', 'cik', 'accession_number'],
        'comex_inventory': ['metal', 'registered_oz', 'eligible_oz'],
    }

    event_required = required_fields.get(event.event_type, [])
    for field in event_required:
        if field not in event.payload:
            errors.append(f"Payload missing required field: {field}")

    return errors


def should_escalate_claim(claim: Claim) -> bool:
    """
    Determine if a claim should be escalated for urgent triage.

    Escalation criteria:
    - High credibility score (>80)
    - Critical claim type (nationalization, liquidity)
    - High engagement (>1000)
    """
    if claim.credibility_score >= 80:
        return True

    if claim.claim_type in ('nationalization', 'liquidity'):
        return True

    if claim.engagement >= 1000:
        return True

    return False


def calculate_claim_credibility(claim: Claim, factors: Dict[str, Any] = None) -> int:
    """
    Calculate credibility score for a claim (0-100).

    Factors:
    - Account age and history (+0-20)
    - Engagement level (+0-15)
    - Source reputation (+0-15)
    - Has supporting evidence (+0-20)
    - Cross-source corroboration (+0-20)
    - Language quality (+0-10)

    Penalties:
    - Absolute language ("guaranteed", "confirmed") without evidence (-30)
    - Known hoax patterns (-50)
    - New account (-10)
    """
    score = 50  # Base score
    factors = factors or {}

    # Engagement bonus
    if claim.engagement >= 1000:
        score += 15
    elif claim.engagement >= 500:
        score += 10
    elif claim.engagement >= 100:
        score += 5

    # Cross-source corroboration
    corroboration_count = factors.get('corroboration_count', 0)
    if corroboration_count >= 3:
        score += 20
    elif corroboration_count >= 2:
        score += 10

    # Has artifact (screenshot, document)
    if factors.get('has_artifact'):
        score += 15

    # Account history
    account_age_days = factors.get('account_age_days', 0)
    if account_age_days >= 365:
        score += 10
    elif account_age_days >= 90:
        score += 5
    elif account_age_days < 30:
        score -= 10  # New account penalty

    # Absolute language penalty
    absolute_patterns = [
        r'guaranteed',
        r'confirmed',
        r'100%',
        r'definitely',
        r'will happen',
        r'trust me',
    ]
    import re
    text = claim.claim_text.lower()
    for pattern in absolute_patterns:
        if re.search(pattern, text):
            score -= 15
            break

    # Clamp to 0-100
    return max(0, min(100, score))
