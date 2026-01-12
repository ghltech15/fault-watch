# Data Pipeline Module
# Fetches and processes data from various sources

from .prices import PriceMonitor, PriceData
from .fed import FedMonitor, FedData, RepoData
from .comex import ComexMonitor, ComexData, ComexInventory
from .sec_monitor import SECMonitor, SECFiling
from .alerts import AlertManager, Alert, AlertSeverity, AlertType
from .credibility import CredibilityFilter
from .database import DatabaseClient, db
from .aggregator import DataAggregator, aggregator

__all__ = [
    'PriceMonitor',
    'PriceData',
    'FedMonitor',
    'FedData',
    'RepoData',
    'ComexMonitor',
    'ComexData',
    'ComexInventory',
    'SECMonitor',
    'SECFiling',
    'AlertManager',
    'Alert',
    'AlertSeverity',
    'AlertType',
    'CredibilityFilter',
    'DatabaseClient',
    'db',
    'DataAggregator',
    'aggregator',
]
