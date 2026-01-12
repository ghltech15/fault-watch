"""
COMEX Monitor
Tracks COMEX silver/gold inventory, deliveries, and open interest
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class ComexInventory:
    registered_oz: float
    eligible_oz: float
    total_oz: float
    registered_change: float
    eligible_change: float
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            'registered_oz': self.registered_oz,
            'eligible_oz': self.eligible_oz,
            'total_oz': self.total_oz,
            'registered_change': self.registered_change,
            'eligible_change': self.eligible_change,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class ComexData:
    inventory: ComexInventory
    open_interest_oz: float
    coverage_ratio: float
    days_of_supply: float
    delivery_notices: int
    status: str

    def to_dict(self) -> Dict:
        return {
            'inventory': self.inventory.to_dict(),
            'open_interest_oz': self.open_interest_oz,
            'coverage_ratio': self.coverage_ratio,
            'days_of_supply': self.days_of_supply,
            'delivery_notices': self.delivery_notices,
            'status': self.status,
        }


class ComexMonitor:
    """Monitor COMEX inventory and delivery data"""

    def __init__(self):
        self.cme_base = 'https://www.cmegroup.com'
        self.cache: Dict[str, any] = {}
        self.cache_ttl = 3600  # 1 hour
        self.last_fetch: Dict[str, datetime] = {}

        # Historical data for tracking changes
        self.inventory_history: List[ComexInventory] = []

        # Default values (updated from CME when available)
        self.current_data = {
            'registered_oz': 30_000_000,  # ~30M oz registered
            'eligible_oz': 270_000_000,   # ~270M oz eligible
            'open_interest_contracts': 150_000,  # ~150k contracts
            'oz_per_contract': 5000,      # 5000 oz per silver contract
        }

    def _fetch_inventory_report(self) -> Optional[str]:
        """Fetch COMEX inventory report (HTML/XLS)"""
        try:
            # CME publishes daily reports
            url = f"{self.cme_base}/delivery_reports/Silver_Stocks.xls"
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            logger.error(f"Error fetching COMEX inventory: {e}")
            return None

    def _parse_inventory_html(self, html: str) -> Optional[Dict]:
        """Parse inventory data from CME HTML/text"""
        try:
            # Look for registered and eligible totals
            # This is a simplified parser - actual CME format varies
            data = {}

            # Try to find numbers in common formats
            registered_match = re.search(
                r'registered[:\s]*([0-9,]+)',
                html,
                re.IGNORECASE
            )
            eligible_match = re.search(
                r'eligible[:\s]*([0-9,]+)',
                html,
                re.IGNORECASE
            )

            if registered_match:
                data['registered'] = int(registered_match.group(1).replace(',', ''))
            if eligible_match:
                data['eligible'] = int(eligible_match.group(1).replace(',', ''))

            return data if data else None
        except Exception as e:
            logger.error(f"Error parsing inventory data: {e}")
            return None

    def get_inventory(self, force_refresh: bool = False) -> ComexInventory:
        """Get current COMEX silver inventory"""
        cache_key = 'inventory'

        if not force_refresh and cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        # Try to fetch live data
        html = self._fetch_inventory_report()
        if html:
            parsed = self._parse_inventory_html(html)
            if parsed:
                self.current_data['registered_oz'] = parsed.get(
                    'registered', self.current_data['registered_oz']
                )
                self.current_data['eligible_oz'] = parsed.get(
                    'eligible', self.current_data['eligible_oz']
                )

        # Calculate changes from history
        registered_change = 0
        eligible_change = 0
        if self.inventory_history:
            last = self.inventory_history[-1]
            registered_change = (
                self.current_data['registered_oz'] - last.registered_oz
            )
            eligible_change = (
                self.current_data['eligible_oz'] - last.eligible_oz
            )

        inventory = ComexInventory(
            registered_oz=self.current_data['registered_oz'],
            eligible_oz=self.current_data['eligible_oz'],
            total_oz=(
                self.current_data['registered_oz'] +
                self.current_data['eligible_oz']
            ),
            registered_change=registered_change,
            eligible_change=eligible_change,
            timestamp=datetime.now(),
        )

        # Update cache and history
        self.cache[cache_key] = inventory
        self.last_fetch[cache_key] = datetime.now()
        self.inventory_history.append(inventory)

        # Keep only last 30 days
        if len(self.inventory_history) > 30:
            self.inventory_history = self.inventory_history[-30:]

        return inventory

    def get_open_interest(self) -> float:
        """Get open interest in ounces"""
        contracts = self.current_data['open_interest_contracts']
        oz_per = self.current_data['oz_per_contract']
        return contracts * oz_per

    def get_coverage_ratio(self) -> float:
        """Calculate paper to physical coverage ratio"""
        inventory = self.get_inventory()
        open_interest_oz = self.get_open_interest()

        if inventory.registered_oz > 0:
            return open_interest_oz / inventory.registered_oz
        return 0

    def get_days_of_supply(self) -> float:
        """Calculate days of supply based on average daily delivery"""
        inventory = self.get_inventory()
        # Assume average daily delivery of 1M oz
        avg_daily_delivery = 1_000_000
        if avg_daily_delivery > 0:
            return inventory.registered_oz / avg_daily_delivery
        return 0

    def get_status(self) -> str:
        """Determine COMEX status based on metrics"""
        coverage = self.get_coverage_ratio()
        days = self.get_days_of_supply()

        if coverage > 5 or days < 10:
            return 'critical'
        elif coverage > 3 or days < 20:
            return 'tight'
        elif coverage > 2 or days < 30:
            return 'elevated'
        return 'normal'

    def get_full_data(self) -> ComexData:
        """Get comprehensive COMEX data"""
        inventory = self.get_inventory()

        return ComexData(
            inventory=inventory,
            open_interest_oz=self.get_open_interest(),
            coverage_ratio=self.get_coverage_ratio(),
            days_of_supply=self.get_days_of_supply(),
            delivery_notices=0,  # Would need separate API
            status=self.get_status(),
        )

    def check_alerts(self, alert_manager) -> List:
        """Check COMEX data against alert thresholds"""
        alerts = []
        inventory = self.get_inventory()
        coverage = self.get_coverage_ratio()

        # Check for inventory drain
        if len(self.inventory_history) >= 2:
            prev = self.inventory_history[-2]
            alert = alert_manager.check_comex_alerts(
                inventory.registered_oz,
                prev.registered_oz,
                coverage
            )
            if alert:
                alerts.append(alert)

        return alerts

    def get_trend(self, days: int = 7) -> Dict:
        """Analyze inventory trend over time"""
        if len(self.inventory_history) < 2:
            return {'trend': 'unknown', 'change_pct': 0}

        history = self.inventory_history[-days:] if len(self.inventory_history) >= days else self.inventory_history

        oldest = history[0].registered_oz
        latest = history[-1].registered_oz

        if oldest == 0:
            return {'trend': 'unknown', 'change_pct': 0}

        change_pct = ((latest - oldest) / oldest) * 100

        if change_pct < -10:
            trend = 'draining_fast'
        elif change_pct < 0:
            trend = 'draining'
        elif change_pct > 10:
            trend = 'building_fast'
        elif change_pct > 0:
            trend = 'building'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'change_pct': change_pct,
            'latest_oz': latest,
            'oldest_oz': oldest,
            'period_days': len(history),
        }

    def get_summary(self) -> Dict:
        """Get COMEX summary for dashboard"""
        data = self.get_full_data()
        trend = self.get_trend()

        return {
            'registered_oz': data.inventory.registered_oz,
            'eligible_oz': data.inventory.eligible_oz,
            'total_oz': data.inventory.total_oz,
            'open_interest_oz': data.open_interest_oz,
            'coverage_ratio': data.coverage_ratio,
            'days_of_supply': data.days_of_supply,
            'status': data.status,
            'trend': trend,
            'last_updated': datetime.now().isoformat(),
        }

    def update_from_external(
        self,
        registered_oz: float = None,
        eligible_oz: float = None,
        open_interest_contracts: int = None
    ):
        """Update data from external source (manual or API)"""
        if registered_oz is not None:
            self.current_data['registered_oz'] = registered_oz
        if eligible_oz is not None:
            self.current_data['eligible_oz'] = eligible_oz
        if open_interest_contracts is not None:
            self.current_data['open_interest_contracts'] = open_interest_contracts

        # Clear cache to force refresh
        self.cache.clear()
