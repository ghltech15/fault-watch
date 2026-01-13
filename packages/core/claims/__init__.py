# Claims module
# Claim extraction, credibility scoring, graduation engine

from .extract import (
    ClaimExtractor,
    ExtractedClaim,
    SocialPost,
    extract_claims_from_post,
    extract_claims_batch,
    CLAIM_PATTERNS,
)

from .credibility import (
    CredibilityFactors,
    CredibilityScore,
    calculate_credibility,
    quick_credibility_check,
    should_escalate,
)

from .graduation import (
    ClaimStatus,
    StoredClaim,
    StoredEvent,
    CorroborationMatch,
    ClaimGraduationEngine,
    get_claim_display_info,
    format_claim_for_display,
)

__all__ = [
    # Extract
    'ClaimExtractor',
    'ExtractedClaim',
    'SocialPost',
    'extract_claims_from_post',
    'extract_claims_batch',
    'CLAIM_PATTERNS',
    # Credibility
    'CredibilityFactors',
    'CredibilityScore',
    'calculate_credibility',
    'quick_credibility_check',
    'should_escalate',
    # Graduation
    'ClaimStatus',
    'StoredClaim',
    'StoredEvent',
    'CorroborationMatch',
    'ClaimGraduationEngine',
    'get_claim_display_info',
    'format_claim_for_display',
]
