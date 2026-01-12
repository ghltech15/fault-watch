# Deliverability collectors - COMEX and dealer monitoring
# Silver/gold physical market stress indicators

from .comex_collector import ComexCollector, ComexSnapshot
from .dealer_monitor import DealerMonitor, DealerSnapshot

__all__ = [
    'ComexCollector',
    'ComexSnapshot',
    'DealerMonitor',
    'DealerSnapshot',
]

# Collector registry
DELIVERABILITY_COLLECTORS = [
    (ComexCollector, 60),       # Hourly COMEX data
    (DealerMonitor, 240),       # Every 4 hours for dealer premiums
]
