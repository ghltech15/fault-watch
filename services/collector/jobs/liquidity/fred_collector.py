"""
FRED Data Collector

Fetches Federal Reserve Economic Data for funding stress indicators.
Trust Tier: 1 (Official) - Creates Events

Key Series:
- SOFR: Secured Overnight Financing Rate
- EFFR: Effective Federal Funds Rate
- IORB: Interest on Reserve Balances
- TED Spread: 3-month LIBOR - 3-month T-Bill
- High Yield Spread: ICE BofA US High Yield Index OAS
- Credit Spreads: Investment grade vs Treasury
- Bank Deposits: Commercial bank deposits
- Reverse Repo: ON RRP usage
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..base import BaseCollector, Event, RawData, TrustTier


# FRED series we monitor
FRED_SERIES = {
    # Overnight rates
    'SOFR': {
        'name': 'Secured Overnight Financing Rate',
        'category': 'rates',
        'critical_threshold': None,  # Compare to EFFR
    },
    'EFFR': {
        'name': 'Effective Federal Funds Rate',
        'category': 'rates',
        'critical_threshold': None,
    },
    'IORB': {
        'name': 'Interest on Reserve Balances',
        'category': 'rates',
        'critical_threshold': None,
    },
    # Spreads
    'TEDRATE': {
        'name': 'TED Spread',
        'category': 'spreads',
        'critical_threshold': 0.5,  # 50 bps is elevated
        'crisis_threshold': 1.0,    # 100 bps is crisis level
    },
    'BAMLH0A0HYM2': {
        'name': 'ICE BofA US High Yield Index Option-Adjusted Spread',
        'category': 'spreads',
        'critical_threshold': 500,  # 500 bps elevated
        'crisis_threshold': 800,    # 800 bps crisis
    },
    'BAMLC0A0CM': {
        'name': 'ICE BofA US Corporate Index Option-Adjusted Spread',
        'category': 'spreads',
        'critical_threshold': 150,
        'crisis_threshold': 250,
    },
    # Liquidity
    'RRPONTSYD': {
        'name': 'Overnight Reverse Repurchase Agreements',
        'category': 'liquidity',
        'critical_threshold': None,  # Monitor for changes
    },
    'WRBWFRBL': {
        'name': 'Reserve Balances with Federal Reserve Banks',
        'category': 'liquidity',
        'critical_threshold': None,
    },
    # Bank health
    'DPSACBW027SBOG': {
        'name': 'Deposits, All Commercial Banks',
        'category': 'deposits',
        'critical_threshold': None,  # Monitor for outflows
    },
    'H8B1058NCBCMG': {
        'name': 'Large Time Deposits at Commercial Banks',
        'category': 'deposits',
        'critical_threshold': None,
    },
    # Stress indicators
    'STLFSI4': {
        'name': 'St. Louis Fed Financial Stress Index',
        'category': 'stress',
        'critical_threshold': 0,     # Above 0 = above average stress
        'crisis_threshold': 1.5,     # 1.5 std above average
    },
    'NFCI': {
        'name': 'Chicago Fed National Financial Conditions Index',
        'category': 'stress',
        'critical_threshold': 0,
        'crisis_threshold': 0.5,
    },
}


@dataclass
class FREDIndicators:
    """Container for FRED indicator values"""
    sofr: Optional[float] = None
    effr: Optional[float] = None
    iorb: Optional[float] = None
    ted_spread: Optional[float] = None
    hy_spread: Optional[float] = None
    ig_spread: Optional[float] = None
    reverse_repo: Optional[float] = None
    reserve_balances: Optional[float] = None
    bank_deposits: Optional[float] = None
    stlfsi: Optional[float] = None
    nfci: Optional[float] = None
    timestamp: datetime = None

    # Computed spreads
    sofr_effr_spread: Optional[float] = None
    sofr_iorb_spread: Optional[float] = None

    def compute_spreads(self):
        """Compute rate spreads"""
        if self.sofr is not None and self.effr is not None:
            self.sofr_effr_spread = self.sofr - self.effr
        if self.sofr is not None and self.iorb is not None:
            self.sofr_iorb_spread = self.sofr - self.iorb

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'sofr': self.sofr,
            'effr': self.effr,
            'iorb': self.iorb,
            'ted_spread': self.ted_spread,
            'hy_spread': self.hy_spread,
            'ig_spread': self.ig_spread,
            'reverse_repo': self.reverse_repo,
            'reserve_balances': self.reserve_balances,
            'bank_deposits': self.bank_deposits,
            'stlfsi': self.stlfsi,
            'nfci': self.nfci,
            'sofr_effr_spread': self.sofr_effr_spread,
            'sofr_iorb_spread': self.sofr_iorb_spread,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class FREDCollector(BaseCollector):
    """
    Collects data from FRED API.

    Creates Tier 1 Events for:
    - Rate changes
    - Spread movements
    - Liquidity changes
    - Stress indicator updates
    """

    source_name = "FRED"
    trust_tier = TrustTier.TIER_1_OFFICIAL
    frequency_minutes = 60  # Hourly updates

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = os.getenv('FRED_API_KEY', '')
        self._last_values: Dict[str, float] = {}

    async def fetch(self) -> List[RawData]:
        """Fetch latest values for all monitored series"""
        raw_data = []

        if not self.api_key:
            print("[FRED] No API key configured, using fallback data")
            return raw_data

        for series_id in FRED_SERIES.keys():
            try:
                url = (
                    f"{self.BASE_URL}?"
                    f"series_id={series_id}&"
                    f"api_key={self.api_key}&"
                    f"file_type=json&"
                    f"sort_order=desc&"
                    f"limit=5"  # Get last 5 observations
                )

                result = await self.fetcher.fetch(url)
                raw_data.append(RawData(
                    content=result.content,
                    url=url,
                    fetched_at=result.fetched_at,
                    headers={'series_id': series_id},
                ))

            except Exception as e:
                print(f"[FRED] Failed to fetch {series_id}: {e}")

        return raw_data

    def parse(self, raw: RawData) -> List[Event]:
        """Parse FRED response into Events"""
        events = []
        series_id = raw.headers.get('series_id', 'unknown')

        try:
            import json
            content = raw.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            data = json.loads(content)
            observations = data.get('observations', [])

            if not observations:
                return events

            # Get latest non-null observation
            latest = None
            for obs in observations:
                value = obs.get('value', '.')
                if value != '.':
                    latest = obs
                    break

            if not latest:
                return events

            value = float(latest['value'])
            date = latest['date']

            series_info = FRED_SERIES.get(series_id, {})

            # Check for significant changes
            prev_value = self._last_values.get(series_id)
            self._last_values[series_id] = value

            # Create event for the observation
            payload = {
                'series_id': series_id,
                'series_name': series_info.get('name', series_id),
                'category': series_info.get('category', 'unknown'),
                'value': value,
                'date': date,
                'previous_value': prev_value,
            }

            # Check thresholds
            critical = series_info.get('critical_threshold')
            crisis = series_info.get('crisis_threshold')

            if crisis and value >= crisis:
                payload['alert_level'] = 'crisis'
                payload['threshold_breached'] = crisis
            elif critical and value >= critical:
                payload['alert_level'] = 'elevated'
                payload['threshold_breached'] = critical

            # Detect significant changes (>10% move)
            if prev_value and prev_value != 0:
                change_pct = ((value - prev_value) / abs(prev_value)) * 100
                payload['change_pct'] = round(change_pct, 2)

                if abs(change_pct) > 10:
                    payload['significant_change'] = True

            events.append(Event(
                event_type='fed_indicator',
                source_id=self.source_id,
                payload=payload,
                entity_id=None,
                published_at=datetime.strptime(date, '%Y-%m-%d') if date else None,
            ))

        except Exception as e:
            print(f"[FRED] Parse error for {series_id}: {e}")

        return events

    def get_current_indicators(self) -> FREDIndicators:
        """Get current indicator values from cache"""
        indicators = FREDIndicators(timestamp=datetime.utcnow())

        # Map series to indicator fields
        mapping = {
            'SOFR': 'sofr',
            'EFFR': 'effr',
            'IORB': 'iorb',
            'TEDRATE': 'ted_spread',
            'BAMLH0A0HYM2': 'hy_spread',
            'BAMLC0A0CM': 'ig_spread',
            'RRPONTSYD': 'reverse_repo',
            'WRBWFRBL': 'reserve_balances',
            'DPSACBW027SBOG': 'bank_deposits',
            'STLFSI4': 'stlfsi',
            'NFCI': 'nfci',
        }

        for series_id, field in mapping.items():
            if series_id in self._last_values:
                setattr(indicators, field, self._last_values[series_id])

        indicators.compute_spreads()
        return indicators
