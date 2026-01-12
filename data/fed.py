"""
Fed Monitor
Tracks Federal Reserve repo operations and monetary data
"""

import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

FRED_API_KEY = os.getenv('FRED_API_KEY', '')


@dataclass
class RepoData:
    date: datetime
    total_amount: float  # billions
    overnight_amount: float
    term_amount: float
    participants: int
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            'date': self.date.isoformat(),
            'total_amount': self.total_amount,
            'overnight_amount': self.overnight_amount,
            'term_amount': self.term_amount,
            'participants': self.participants,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class FedData:
    reverse_repo: float  # billions
    fed_funds_rate: float
    discount_rate: float
    balance_sheet: float  # trillions
    treasury_holdings: float  # trillions
    mbs_holdings: float  # trillions
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            'reverse_repo': self.reverse_repo,
            'fed_funds_rate': self.fed_funds_rate,
            'discount_rate': self.discount_rate,
            'balance_sheet': self.balance_sheet,
            'treasury_holdings': self.treasury_holdings,
            'mbs_holdings': self.mbs_holdings,
            'timestamp': self.timestamp.isoformat(),
        }


class FedMonitor:
    """Monitor Federal Reserve operations and data"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or FRED_API_KEY
        self.fred_base = 'https://api.stlouisfed.org/fred/series/observations'
        self.ny_fed_base = 'https://markets.newyorkfed.org/api'

        # FRED series IDs
        self.series = {
            'reverse_repo': 'RRPONTSYD',      # Overnight Reverse Repo
            'fed_funds': 'FEDFUNDS',           # Federal Funds Rate
            'discount_rate': 'DISCOUNT',       # Discount Rate
            'total_assets': 'WALCL',           # Fed Total Assets
            'treasuries': 'TREAST',            # Treasury Holdings
            'mbs': 'WSHOMCB',                  # MBS Holdings
            'ted_spread': 'TEDRATE',           # TED Spread
            'high_yield_spread': 'BAMLH0A0HYM2', # High Yield Spread
        }

        self.cache: Dict[str, any] = {}
        self.cache_ttl = 3600  # 1 hour
        self.last_fetch: Dict[str, datetime] = {}

        # Repo history for trend analysis
        self.repo_history: List[RepoData] = []

    def _fetch_fred_series(
        self,
        series_id: str,
        limit: int = 10
    ) -> Optional[List[Dict]]:
        """Fetch data from FRED API"""
        if not self.api_key:
            logger.warning("No FRED API key configured")
            return None

        try:
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': limit,
            }
            response = requests.get(self.fred_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('observations', [])
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            return None

    def get_latest_value(self, series_id: str) -> Optional[float]:
        """Get latest value for a FRED series"""
        observations = self._fetch_fred_series(series_id, limit=1)
        if observations and len(observations) > 0:
            value = observations[0].get('value')
            if value and value != '.':
                return float(value)
        return None

    def get_reverse_repo(self) -> Optional[float]:
        """Get latest reverse repo amount (billions)"""
        cache_key = 'reverse_repo'
        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        value = self.get_latest_value(self.series['reverse_repo'])
        if value:
            # Convert from millions to billions
            value_billions = value / 1000
            self.cache[cache_key] = value_billions
            self.last_fetch[cache_key] = datetime.now()
            return value_billions
        return self.cache.get(cache_key)

    def get_fed_funds_rate(self) -> Optional[float]:
        """Get current fed funds rate"""
        return self.get_latest_value(self.series['fed_funds'])

    def get_balance_sheet(self) -> Optional[float]:
        """Get Fed balance sheet total (trillions)"""
        value = self.get_latest_value(self.series['total_assets'])
        if value:
            # Convert from millions to trillions
            return value / 1e6
        return None

    def get_ted_spread(self) -> Optional[float]:
        """Get TED spread (credit stress indicator)"""
        return self.get_latest_value(self.series['ted_spread'])

    def get_high_yield_spread(self) -> Optional[float]:
        """Get high yield bond spread (basis points)"""
        return self.get_latest_value(self.series['high_yield_spread'])

    def get_repo_trend(self, days: int = 7) -> Dict:
        """Analyze repo operation trends"""
        observations = self._fetch_fred_series(self.series['reverse_repo'], limit=days)
        if not observations:
            return {'trend': 'unknown', 'change_pct': 0}

        values = []
        for obs in observations:
            if obs.get('value') and obs['value'] != '.':
                values.append(float(obs['value']))

        if len(values) < 2:
            return {'trend': 'unknown', 'change_pct': 0}

        # Latest is first (desc order)
        latest = values[0]
        oldest = values[-1]

        if oldest == 0:
            return {'trend': 'unknown', 'change_pct': 0}

        change_pct = ((latest - oldest) / oldest) * 100

        if change_pct > 10:
            trend = 'rising_fast'
        elif change_pct > 0:
            trend = 'rising'
        elif change_pct < -10:
            trend = 'falling_fast'
        elif change_pct < 0:
            trend = 'falling'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'change_pct': change_pct,
            'latest': latest / 1000,  # billions
            'oldest': oldest / 1000,
            'period_days': len(values),
        }

    def get_stress_indicators(self) -> Dict:
        """Get all credit stress indicators"""
        return {
            'ted_spread': self.get_ted_spread(),
            'high_yield_spread': self.get_high_yield_spread(),
            'reverse_repo': self.get_reverse_repo(),
            'fed_funds_rate': self.get_fed_funds_rate(),
            'timestamp': datetime.now().isoformat(),
        }

    def check_alerts(self, alert_manager) -> List:
        """Check Fed data against alert thresholds"""
        alerts = []

        # Check reverse repo
        repo = self.get_reverse_repo()
        if repo:
            alert = alert_manager.check_fed_repo_alerts(repo)
            if alert:
                alerts.append(alert)

        # Check TED spread for credit stress
        ted = self.get_ted_spread()
        if ted and ted > 0.5:  # 50 basis points
            from .alerts import Alert, AlertSeverity, AlertType
            severity = AlertSeverity.CRITICAL if ted > 1.0 else AlertSeverity.HIGH
            alert = Alert(
                severity=severity,
                alert_type=AlertType.CREDIT_STRESS,
                title=f"TED SPREAD ELEVATED: {ted:.2f}%",
                description=f"Credit stress indicator at {ted:.2f}%, indicates bank funding stress",
                source='FRED/Fed Monitor',
                data={'ted_spread': ted},
            )
            if alert_manager.add_alert(alert):
                alerts.append(alert)

        return alerts

    def get_summary(self) -> Dict:
        """Get Fed data summary for dashboard"""
        return {
            'reverse_repo_billion': self.get_reverse_repo(),
            'fed_funds_rate': self.get_fed_funds_rate(),
            'balance_sheet_trillion': self.get_balance_sheet(),
            'ted_spread': self.get_ted_spread(),
            'high_yield_spread': self.get_high_yield_spread(),
            'repo_trend': self.get_repo_trend(),
            'last_updated': datetime.now().isoformat(),
        }
