# Liquidity collectors - Funding stress monitoring
# FRED data, rate spreads, facility usage

from .fred_collector import FREDCollector, FREDIndicators
from .liquidity_monitor import LiquidityMonitor

__all__ = [
    'FREDCollector',
    'FREDIndicators',
    'LiquidityMonitor',
]

# Collector registry
LIQUIDITY_COLLECTORS = [
    (FREDCollector, 60),        # Hourly FRED data refresh
    (LiquidityMonitor, 30),     # Every 30 min for critical indicators
]
