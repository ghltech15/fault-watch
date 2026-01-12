"""
Liquidity Monitor

Real-time monitoring of liquidity conditions and funding stress.
Aggregates data from multiple sources for unified view.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..base import BaseCollector, Event, RawData, TrustTier


@dataclass
class LiquiditySnapshot:
    """Point-in-time liquidity conditions"""
    timestamp: datetime

    # Rate spreads (basis points)
    sofr_effr_spread: Optional[float] = None
    sofr_iorb_spread: Optional[float] = None
    ted_spread: Optional[float] = None

    # Credit spreads (basis points)
    hy_spread: Optional[float] = None
    ig_spread: Optional[float] = None

    # Fed facilities (billions)
    reverse_repo: Optional[float] = None
    discount_window: Optional[float] = None
    btfp_usage: Optional[float] = None  # Bank Term Funding Program

    # Bank health
    deposit_change_pct: Optional[float] = None
    reserve_balances: Optional[float] = None

    # Stress indices
    stlfsi: Optional[float] = None
    nfci: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'rate_spreads': {
                'sofr_effr': self.sofr_effr_spread,
                'sofr_iorb': self.sofr_iorb_spread,
                'ted': self.ted_spread,
            },
            'credit_spreads': {
                'high_yield': self.hy_spread,
                'investment_grade': self.ig_spread,
            },
            'fed_facilities': {
                'reverse_repo': self.reverse_repo,
                'discount_window': self.discount_window,
                'btfp': self.btfp_usage,
            },
            'bank_health': {
                'deposit_change_pct': self.deposit_change_pct,
                'reserve_balances': self.reserve_balances,
            },
            'stress_indices': {
                'stlfsi': self.stlfsi,
                'nfci': self.nfci,
            },
        }


class LiquidityMonitor(BaseCollector):
    """
    Monitors overall liquidity conditions.

    Aggregates:
    - FRED indicators
    - Fed H.4.1 data
    - Market data
    """

    source_name = "Liquidity Monitor"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: List[LiquiditySnapshot] = []
        self._max_history = 1000  # Keep last 1000 snapshots

    async def fetch(self) -> List[RawData]:
        """
        Liquidity monitor doesn't fetch directly - it aggregates.
        This method creates a synthetic snapshot from available data.
        """
        # In production, this would pull from the event store
        # For now, return empty and let aggregation happen at API level
        return []

    def parse(self, raw: RawData) -> List[Event]:
        """No direct parsing - aggregation based"""
        return []

    def create_snapshot(
        self,
        indicators: Dict[str, Any],
        h41_data: Optional[Dict] = None,
    ) -> LiquiditySnapshot:
        """Create liquidity snapshot from available data"""
        snapshot = LiquiditySnapshot(timestamp=datetime.utcnow())

        # FRED indicators
        snapshot.sofr_effr_spread = indicators.get('sofr_effr_spread')
        snapshot.sofr_iorb_spread = indicators.get('sofr_iorb_spread')
        snapshot.ted_spread = indicators.get('ted_spread')
        snapshot.hy_spread = indicators.get('hy_spread')
        snapshot.ig_spread = indicators.get('ig_spread')
        snapshot.stlfsi = indicators.get('stlfsi')
        snapshot.nfci = indicators.get('nfci')

        # H.4.1 data
        if h41_data:
            snapshot.reverse_repo = h41_data.get('reverse_repo')
            snapshot.discount_window = h41_data.get('discount_window')
            snapshot.btfp_usage = h41_data.get('btfp_usage')
            snapshot.reserve_balances = h41_data.get('reserve_balances')

        # Deposit change (would need historical comparison)
        if 'bank_deposits' in indicators and 'prev_bank_deposits' in indicators:
            prev = indicators['prev_bank_deposits']
            curr = indicators['bank_deposits']
            if prev and prev > 0:
                snapshot.deposit_change_pct = ((curr - prev) / prev) * 100

        # Store in history
        self._history.append(snapshot)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        return snapshot

    def detect_stress_events(self, snapshot: LiquiditySnapshot) -> List[Event]:
        """Detect stress events from snapshot"""
        events = []

        # TED spread spike
        if snapshot.ted_spread and snapshot.ted_spread > 0.5:
            events.append(Event(
                event_type='liquidity_stress',
                source_id=self.source_id,
                payload={
                    'indicator': 'ted_spread',
                    'value': snapshot.ted_spread,
                    'threshold': 0.5,
                    'severity': 'elevated' if snapshot.ted_spread < 1.0 else 'crisis',
                    'description': f'TED spread at {snapshot.ted_spread:.2f}%',
                },
                entity_id=None,
            ))

        # High yield spread
        if snapshot.hy_spread and snapshot.hy_spread > 500:
            events.append(Event(
                event_type='credit_stress',
                source_id=self.source_id,
                payload={
                    'indicator': 'hy_spread',
                    'value': snapshot.hy_spread,
                    'threshold': 500,
                    'severity': 'elevated' if snapshot.hy_spread < 800 else 'crisis',
                    'description': f'High yield spread at {snapshot.hy_spread:.0f} bps',
                },
                entity_id=None,
            ))

        # Rate dislocation
        if snapshot.sofr_effr_spread and abs(snapshot.sofr_effr_spread) > 0.1:
            events.append(Event(
                event_type='rate_dislocation',
                source_id=self.source_id,
                payload={
                    'indicator': 'sofr_effr_spread',
                    'value': snapshot.sofr_effr_spread,
                    'threshold': 0.1,
                    'severity': 'elevated',
                    'description': f'SOFR-EFFR spread at {snapshot.sofr_effr_spread:.2f}%',
                },
                entity_id=None,
            ))

        # Deposit outflow
        if snapshot.deposit_change_pct and snapshot.deposit_change_pct < -2:
            events.append(Event(
                event_type='deposit_stress',
                source_id=self.source_id,
                payload={
                    'indicator': 'deposit_change',
                    'value': snapshot.deposit_change_pct,
                    'threshold': -2,
                    'severity': 'elevated' if snapshot.deposit_change_pct > -5 else 'crisis',
                    'description': f'Bank deposits down {abs(snapshot.deposit_change_pct):.1f}%',
                },
                entity_id=None,
            ))

        # Stress index breach
        if snapshot.stlfsi and snapshot.stlfsi > 0:
            severity = 'elevated' if snapshot.stlfsi < 1.5 else 'crisis'
            events.append(Event(
                event_type='stress_index_breach',
                source_id=self.source_id,
                payload={
                    'indicator': 'stlfsi',
                    'value': snapshot.stlfsi,
                    'threshold': 0,
                    'severity': severity,
                    'description': f'St. Louis Fed Stress Index at {snapshot.stlfsi:.2f}',
                },
                entity_id=None,
            ))

        return events

    def get_latest_snapshot(self) -> Optional[LiquiditySnapshot]:
        """Get most recent snapshot"""
        return self._history[-1] if self._history else None

    def get_snapshot_history(self, hours: int = 24) -> List[LiquiditySnapshot]:
        """Get snapshots from last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [s for s in self._history if s.timestamp > cutoff]
