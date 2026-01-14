# Core package
# Entity resolution, trust tiers, scoring engines, and utilities

from .trust import TrustTier, process_source_data
from .entities import EntityResolver, Entity
from .verification import (
    VerificationStatus,
    SourceReference,
    VerificationMeta,
    PRICE_SOURCES,
    FRED_SOURCES,
    COMEX_SOURCES,
    SEC_SOURCES,
    calculate_verification_status,
    calculate_confidence,
    create_verification_meta,
)

__all__ = [
    'TrustTier',
    'process_source_data',
    'EntityResolver',
    'Entity',
    'VerificationStatus',
    'SourceReference',
    'VerificationMeta',
    'PRICE_SOURCES',
    'FRED_SOURCES',
    'COMEX_SOURCES',
    'SEC_SOURCES',
    'calculate_verification_status',
    'calculate_confidence',
    'create_verification_meta',
]
