"""
Verification Status System
===========================
Tracks source verification and truth tiers for displayed data.
"""

from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class VerificationStatus(Enum):
    """Verification status levels based on source count and quality."""
    VERIFIED = "verified"           # 3-5+ sources confirm (Tier 1-2)
    PARTIALLY_VERIFIED = "partial"  # 2-3 sources, needs more
    WORKING_THEORY = "theory"       # Hypothesis based on patterns
    UNVERIFIED = "unverified"       # Single source or speculation


class TrustTier(Enum):
    """Source trust levels."""
    TIER_1_OFFICIAL = 1    # SEC, FRED, CFTC, CME - official data
    TIER_2_CREDIBLE = 2    # Reuters, Bloomberg, Yahoo Finance
    TIER_3_SOCIAL = 3      # Reddit, Twitter, blogs


class SourceReference(BaseModel):
    """Reference to a data source."""
    name: str               # "SEC Filing", "FRED", "Reuters", "Finnhub"
    url: Optional[str] = None  # Link to source if available
    tier: int               # 1=Official, 2=Credible, 3=Social
    retrieved_at: Optional[str] = None  # ISO timestamp


class VerificationMeta(BaseModel):
    """Verification metadata for any data point."""
    status: str  # verified|partial|theory|unverified
    source_count: int
    sources: List[SourceReference] = []
    confidence: float = 0.0   # 0-100 based on source quality
    last_verified: Optional[str] = None  # ISO timestamp


# Default sources for common data feeds
PRICE_SOURCES = [
    SourceReference(name="Finnhub", tier=1),
    SourceReference(name="Yahoo Finance", tier=2),
]

FRED_SOURCES = [
    SourceReference(name="FRED (Federal Reserve)", tier=1),
]

COMEX_SOURCES = [
    SourceReference(name="CME Group", tier=1),
]

SEC_SOURCES = [
    SourceReference(name="SEC EDGAR", tier=1),
]


def calculate_verification_status(sources: List[SourceReference]) -> str:
    """
    Determine verification status based on source count and quality.

    - 3+ Tier 1-2 sources = verified
    - 2-3 sources = partial
    - 1 source = unverified
    """
    if not sources:
        return VerificationStatus.UNVERIFIED.value

    # Count high-quality sources (Tier 1-2)
    quality_sources = [s for s in sources if s.tier <= 2]

    if len(quality_sources) >= 3:
        return VerificationStatus.VERIFIED.value
    elif len(quality_sources) >= 2 or len(sources) >= 2:
        return VerificationStatus.PARTIALLY_VERIFIED.value
    else:
        return VerificationStatus.UNVERIFIED.value


def calculate_confidence(sources: List[SourceReference]) -> float:
    """
    Calculate confidence score (0-100) based on source quality.

    Tier 1 sources add 30 each, Tier 2 add 20, Tier 3 add 10.
    Max 100.
    """
    if not sources:
        return 0.0

    tier_scores = {1: 30, 2: 20, 3: 10}
    total = sum(tier_scores.get(s.tier, 5) for s in sources)
    return min(total, 100.0)


def create_verification_meta(sources: List[SourceReference]) -> VerificationMeta:
    """Create verification metadata from a list of sources."""
    return VerificationMeta(
        status=calculate_verification_status(sources),
        source_count=len(sources),
        sources=sources,
        confidence=calculate_confidence(sources),
        last_verified=datetime.now().isoformat()
    )
