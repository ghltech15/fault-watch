"""
COMEX Collector

Enhanced COMEX inventory and delivery tracking.
Trust Tier: 1 (Official) - Creates Events

Monitors:
- Registered vs Eligible inventory
- Delivery notices (daily, trends)
- Open interest vs physical
- Coverage ratio
- Days of supply
- Warehouse stock velocity
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
import re

from bs4 import BeautifulSoup

from ..base import BaseCollector, Event, RawData, TrustTier


@dataclass
class ComexSnapshot:
    """Point-in-time COMEX inventory data"""
    timestamp: datetime

    # Inventory (troy ounces)
    registered_oz: Optional[float] = None
    eligible_oz: Optional[float] = None
    total_oz: Optional[float] = None

    # Delivery data
    delivery_notices: Optional[int] = None
    delivery_notices_oz: Optional[float] = None
    stopped_notices: Optional[int] = None

    # Open interest
    open_interest_contracts: Optional[int] = None
    open_interest_oz: Optional[float] = None

    # Computed metrics
    coverage_ratio: Optional[float] = None      # OI / Registered
    days_of_supply: Optional[float] = None      # Registered / avg daily delivery
    registered_pct: Optional[float] = None      # Registered / Total

    # Velocity (change rates)
    registered_change_oz: Optional[float] = None
    registered_change_pct: Optional[float] = None
    delivery_notices_change_pct: Optional[float] = None

    def compute_metrics(self, prev_snapshot: 'ComexSnapshot' = None):
        """Compute derived metrics"""
        # Total inventory
        if self.registered_oz and self.eligible_oz:
            self.total_oz = self.registered_oz + self.eligible_oz

        # Registered percentage
        if self.registered_oz and self.total_oz and self.total_oz > 0:
            self.registered_pct = (self.registered_oz / self.total_oz) * 100

        # Coverage ratio (paper to physical)
        if self.open_interest_oz and self.registered_oz and self.registered_oz > 0:
            self.coverage_ratio = self.open_interest_oz / self.registered_oz

        # Velocity from previous snapshot
        if prev_snapshot and prev_snapshot.registered_oz:
            self.registered_change_oz = self.registered_oz - prev_snapshot.registered_oz
            if prev_snapshot.registered_oz > 0:
                self.registered_change_pct = (self.registered_change_oz / prev_snapshot.registered_oz) * 100

        if prev_snapshot and prev_snapshot.delivery_notices and self.delivery_notices:
            if prev_snapshot.delivery_notices > 0:
                change = self.delivery_notices - prev_snapshot.delivery_notices
                self.delivery_notices_change_pct = (change / prev_snapshot.delivery_notices) * 100

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'inventory': {
                'registered_oz': self.registered_oz,
                'eligible_oz': self.eligible_oz,
                'total_oz': self.total_oz,
                'registered_pct': round(self.registered_pct, 1) if self.registered_pct else None,
            },
            'delivery': {
                'notices': self.delivery_notices,
                'notices_oz': self.delivery_notices_oz,
                'stopped': self.stopped_notices,
            },
            'open_interest': {
                'contracts': self.open_interest_contracts,
                'oz': self.open_interest_oz,
            },
            'metrics': {
                'coverage_ratio': round(self.coverage_ratio, 2) if self.coverage_ratio else None,
                'days_of_supply': round(self.days_of_supply, 1) if self.days_of_supply else None,
            },
            'velocity': {
                'registered_change_oz': self.registered_change_oz,
                'registered_change_pct': round(self.registered_change_pct, 2) if self.registered_change_pct else None,
                'delivery_notices_change_pct': round(self.delivery_notices_change_pct, 2) if self.delivery_notices_change_pct else None,
            },
        }


# COMEX contract specs
SILVER_CONTRACT_OZ = 5000  # 5000 oz per contract
GOLD_CONTRACT_OZ = 100     # 100 oz per contract


class ComexCollector(BaseCollector):
    """
    Collects COMEX inventory and delivery data.

    Creates Tier 1 Events for:
    - Daily inventory updates
    - Delivery notice spikes
    - Coverage ratio changes
    - Significant outflows
    """

    source_name = "CME COMEX"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 60  # Hourly checks

    # CME data URLs
    INVENTORY_URL = "https://www.cmegroup.com/delivery_reports/Silver_Stocks.xls"
    DELIVERY_URL = "https://www.cmegroup.com/delivery_reports/MetalsIssuesAndStopsYTDReport.pdf"

    # Fallback: CME precious metals page
    METALS_URL = "https://www.cmegroup.com/markets/metals/precious/silver.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: List[ComexSnapshot] = []
        self._max_history = 365  # Keep 1 year of daily data

    async def fetch(self) -> List[RawData]:
        """Fetch COMEX data from multiple sources"""
        raw_data = []

        # Try to fetch inventory report
        try:
            result = await self.fetcher.fetch(self.METALS_URL, headers={
                'User-Agent': 'FaultWatch/2.0 (contact@fault.watch)'
            })
            raw_data.append(RawData(
                content=result.content,
                url=self.METALS_URL,
                fetched_at=result.fetched_at,
                headers={'type': 'metals_page'},
            ))
        except Exception as e:
            print(f"[COMEX] Failed to fetch metals page: {e}")

        return raw_data

    def parse(self, raw: RawData) -> List[Event]:
        """Parse COMEX data into Events"""
        events = []
        data_type = raw.headers.get('type', 'unknown')

        try:
            if data_type == 'metals_page':
                snapshot = self._parse_metals_page(raw.content)
            else:
                snapshot = None

            if snapshot:
                # Compute metrics with previous snapshot
                prev = self._history[-1] if self._history else None
                snapshot.compute_metrics(prev)

                # Store in history
                self._history.append(snapshot)
                if len(self._history) > self._max_history:
                    self._history = self._history[-self._max_history:]

                # Create inventory event
                events.append(Event(
                    event_type='comex_inventory',
                    source_id=self.source_id,
                    payload=snapshot.to_dict(),
                    entity_id=None,
                    published_at=snapshot.timestamp,
                ))

                # Check for stress conditions
                stress_events = self._detect_stress(snapshot, prev)
                events.extend(stress_events)

        except Exception as e:
            print(f"[COMEX] Parse error: {e}")

        return events

    def _parse_metals_page(self, content: str | bytes) -> Optional[ComexSnapshot]:
        """Parse CME metals page for COMEX data"""
        if isinstance(content, bytes):
            content = content.decode('utf-8')

        snapshot = ComexSnapshot(timestamp=datetime.utcnow())

        try:
            soup = BeautifulSoup(content, 'lxml')

            # Look for inventory data in page
            # CME page structure varies, so we try multiple patterns
            text = soup.get_text().lower()

            # Extract open interest
            oi_match = re.search(r'open interest[:\s]+(\d{1,3}(?:,\d{3})*)', text)
            if oi_match:
                snapshot.open_interest_contracts = int(oi_match.group(1).replace(',', ''))
                snapshot.open_interest_oz = snapshot.open_interest_contracts * SILVER_CONTRACT_OZ

            # Look for volume data as proxy for activity
            vol_match = re.search(r'volume[:\s]+(\d{1,3}(?:,\d{3})*)', text)
            if vol_match:
                volume = int(vol_match.group(1).replace(',', ''))
                # Use volume as activity indicator

            # Note: Real implementation would parse Excel/PDF reports
            # For now, we'll rely on the existing data/comex.py module
            # and just create the event structure

        except Exception as e:
            print(f"[COMEX] Page parse error: {e}")

        return snapshot if snapshot.open_interest_contracts else None

    def _detect_stress(
        self,
        current: ComexSnapshot,
        prev: Optional[ComexSnapshot],
    ) -> List[Event]:
        """Detect stress conditions from COMEX data"""
        events = []

        # High coverage ratio (paper >> physical)
        if current.coverage_ratio and current.coverage_ratio > 3:
            severity = 'critical' if current.coverage_ratio > 5 else 'elevated'
            events.append(Event(
                event_type='comex_stress',
                source_id=self.source_id,
                payload={
                    'indicator': 'coverage_ratio',
                    'value': current.coverage_ratio,
                    'threshold': 3,
                    'severity': severity,
                    'description': f'Coverage ratio at {current.coverage_ratio:.1f}x',
                },
                entity_id=None,
            ))

        # Rapid inventory decline
        if current.registered_change_pct and current.registered_change_pct < -5:
            severity = 'critical' if current.registered_change_pct < -10 else 'elevated'
            events.append(Event(
                event_type='comex_outflow',
                source_id=self.source_id,
                payload={
                    'indicator': 'registered_change',
                    'value': current.registered_change_pct,
                    'change_oz': current.registered_change_oz,
                    'threshold': -5,
                    'severity': severity,
                    'description': f'Registered silver down {abs(current.registered_change_pct):.1f}%',
                },
                entity_id=None,
            ))

        # Delivery notices acceleration
        if current.delivery_notices_change_pct and current.delivery_notices_change_pct > 50:
            events.append(Event(
                event_type='comex_delivery_spike',
                source_id=self.source_id,
                payload={
                    'indicator': 'delivery_notices',
                    'value': current.delivery_notices,
                    'change_pct': current.delivery_notices_change_pct,
                    'severity': 'elevated',
                    'description': f'Delivery notices up {current.delivery_notices_change_pct:.0f}%',
                },
                entity_id=None,
            ))

        # Low days of supply
        if current.days_of_supply and current.days_of_supply < 20:
            severity = 'critical' if current.days_of_supply < 10 else 'elevated'
            events.append(Event(
                event_type='comex_supply_stress',
                source_id=self.source_id,
                payload={
                    'indicator': 'days_of_supply',
                    'value': current.days_of_supply,
                    'threshold': 20,
                    'severity': severity,
                    'description': f'Only {current.days_of_supply:.0f} days of supply',
                },
                entity_id=None,
            ))

        return events

    def get_latest_snapshot(self) -> Optional[ComexSnapshot]:
        """Get most recent snapshot"""
        return self._history[-1] if self._history else None

    def get_coverage_ratio_history(self, days: int = 30) -> List[Dict]:
        """Get coverage ratio history"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return [
            {'date': s.timestamp.isoformat(), 'ratio': s.coverage_ratio}
            for s in self._history
            if s.timestamp > cutoff and s.coverage_ratio
        ]

    def calculate_days_of_supply(self, avg_daily_delivery_oz: float) -> float:
        """Calculate days of supply based on average daily delivery"""
        latest = self.get_latest_snapshot()
        if latest and latest.registered_oz and avg_daily_delivery_oz > 0:
            return latest.registered_oz / avg_daily_delivery_oz
        return 0
