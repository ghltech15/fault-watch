# Regulatory collectors - Tier 1 Official Sources
# SEC, CFTC, OCC, FDIC, Fed

from .sec_enforcement import SECEnforcementCollector, SECWhistleblowerCollector
from .cftc import CFTCEnforcementCollector, CFTCCOTCollector
from .occ import OCCEnforcementCollector
from .fdic import FDICBankFailuresCollector, FDICEnforcementCollector
from .fed import FedH41Collector, FedPressCollector

__all__ = [
    # SEC
    'SECEnforcementCollector',
    'SECWhistleblowerCollector',
    # CFTC
    'CFTCEnforcementCollector',
    'CFTCCOTCollector',
    # OCC
    'OCCEnforcementCollector',
    # FDIC
    'FDICBankFailuresCollector',
    'FDICEnforcementCollector',
    # Fed
    'FedH41Collector',
    'FedPressCollector',
]

# Collector registry for easy registration
REGULATORY_COLLECTORS = [
    # High frequency (critical for early warning)
    (SECEnforcementCollector, 60),      # Hourly
    (FedPressCollector, 30),            # Every 30 min (FOMC critical)
    (FedH41Collector, 60),              # Hourly (weekly release)
    # Medium frequency
    (CFTCEnforcementCollector, 120),    # Every 2 hours
    (OCCEnforcementCollector, 120),     # Every 2 hours
    # Lower frequency
    (SECWhistleblowerCollector, 240),   # Every 4 hours
    (FDICBankFailuresCollector, 240),   # Every 4 hours
    (FDICEnforcementCollector, 240),    # Every 4 hours
    (CFTCCOTCollector, 1440),           # Daily (weekly release)
]
