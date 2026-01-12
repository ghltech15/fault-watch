"""
Z-Score and Regime Shift Detection

Statistical tools for detecting unusual market conditions and regime changes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import math
from collections import deque


@dataclass
class RegimeAlert:
    """Alert for detected regime shift"""
    indicator: str
    current_value: float
    zscore: float
    percentile: float
    direction: str  # 'stress' or 'easing'
    lookback_days: int
    mean: float
    std: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'indicator': self.indicator,
            'current_value': self.current_value,
            'zscore': round(self.zscore, 2),
            'percentile': round(self.percentile, 1),
            'direction': self.direction,
            'lookback_days': self.lookback_days,
            'mean': round(self.mean, 4),
            'std': round(self.std, 4),
            'timestamp': self.timestamp.isoformat(),
        }

    @property
    def severity(self) -> str:
        """Get severity level from z-score"""
        abs_z = abs(self.zscore)
        if abs_z >= 3:
            return 'extreme'
        elif abs_z >= 2.5:
            return 'severe'
        elif abs_z >= 2:
            return 'elevated'
        elif abs_z >= 1.5:
            return 'moderate'
        else:
            return 'normal'


@dataclass
class TimeSeriesPoint:
    """Single point in a time series"""
    timestamp: datetime
    value: float


class ZScoreCalculator:
    """
    Calculate z-scores and detect regime shifts in time series data.

    Uses rolling statistics to identify when values deviate significantly
    from recent history.
    """

    def __init__(
        self,
        lookback_days: int = 90,
        zscore_threshold: float = 2.0,
        min_data_points: int = 20,
    ):
        self.lookback_days = lookback_days
        self.zscore_threshold = zscore_threshold
        self.min_data_points = min_data_points

    def calculate_zscore(
        self,
        current: float,
        history: List[float],
    ) -> Tuple[float, float, float]:
        """
        Calculate z-score for current value against history.

        Returns: (zscore, mean, std)
        """
        if len(history) < self.min_data_points:
            return 0.0, current, 0.0

        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std = math.sqrt(variance) if variance > 0 else 0.0001

        zscore = (current - mean) / std if std > 0 else 0.0

        return zscore, mean, std

    def detect_regime_shift(
        self,
        indicator: str,
        current: float,
        history: List[TimeSeriesPoint],
        higher_is_stress: bool = True,
    ) -> Optional[RegimeAlert]:
        """
        Detect if current value represents a regime shift.

        Args:
            indicator: Name of the indicator
            current: Current value
            history: Historical time series
            higher_is_stress: True if higher values indicate stress

        Returns:
            RegimeAlert if shift detected, None otherwise
        """
        # Filter history to lookback period
        cutoff = datetime.utcnow() - timedelta(days=self.lookback_days)
        recent = [p.value for p in history if p.timestamp > cutoff]

        if len(recent) < self.min_data_points:
            return None

        zscore, mean, std = self.calculate_zscore(current, recent)

        # Check if zscore exceeds threshold
        if abs(zscore) < self.zscore_threshold:
            return None

        # Determine direction
        if higher_is_stress:
            direction = 'stress' if zscore > 0 else 'easing'
        else:
            direction = 'easing' if zscore > 0 else 'stress'

        # Calculate percentile (using normal distribution approximation)
        percentile = self._zscore_to_percentile(zscore)

        return RegimeAlert(
            indicator=indicator,
            current_value=current,
            zscore=zscore,
            percentile=percentile,
            direction=direction,
            lookback_days=self.lookback_days,
            mean=mean,
            std=std,
        )

    def _zscore_to_percentile(self, zscore: float) -> float:
        """Convert z-score to percentile using approximation"""
        # Approximation of cumulative normal distribution
        # Uses Abramowitz and Stegun approximation
        t = 1.0 / (1.0 + 0.2316419 * abs(zscore))
        d = 0.3989423 * math.exp(-zscore * zscore / 2)
        p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))

        if zscore > 0:
            return (1 - p) * 100
        else:
            return p * 100


class RollingStatistics:
    """
    Maintain rolling statistics for real-time z-score calculation.

    Memory-efficient implementation using deque.
    """

    def __init__(self, window_size: int = 90):
        self.window_size = window_size
        self._values: deque = deque(maxlen=window_size)
        self._sum: float = 0.0
        self._sum_sq: float = 0.0

    def add(self, value: float):
        """Add new value and update statistics"""
        if len(self._values) == self.window_size:
            # Remove oldest value from sums
            old = self._values[0]
            self._sum -= old
            self._sum_sq -= old * old

        self._values.append(value)
        self._sum += value
        self._sum_sq += value * value

    @property
    def mean(self) -> float:
        """Current rolling mean"""
        n = len(self._values)
        return self._sum / n if n > 0 else 0.0

    @property
    def std(self) -> float:
        """Current rolling standard deviation"""
        n = len(self._values)
        if n < 2:
            return 0.0

        variance = (self._sum_sq / n) - (self.mean ** 2)
        return math.sqrt(max(variance, 0))

    def zscore(self, value: float) -> float:
        """Calculate z-score for a value"""
        std = self.std
        if std == 0:
            return 0.0
        return (value - self.mean) / std

    @property
    def count(self) -> int:
        """Number of values in window"""
        return len(self._values)


class MultiIndicatorRegimeDetector:
    """
    Detect regime shifts across multiple indicators.

    Provides unified view of market conditions.
    """

    # Indicator configurations
    INDICATORS = {
        'ted_spread': {
            'higher_is_stress': True,
            'lookback_days': 90,
            'zscore_threshold': 2.0,
        },
        'hy_spread': {
            'higher_is_stress': True,
            'lookback_days': 90,
            'zscore_threshold': 2.0,
        },
        'sofr_effr_spread': {
            'higher_is_stress': True,  # Positive spread = repo stress
            'lookback_days': 60,
            'zscore_threshold': 2.5,
        },
        'stlfsi': {
            'higher_is_stress': True,
            'lookback_days': 90,
            'zscore_threshold': 1.5,  # Lower threshold as it's already normalized
        },
        'nfci': {
            'higher_is_stress': True,
            'lookback_days': 90,
            'zscore_threshold': 1.5,
        },
        'deposit_change': {
            'higher_is_stress': False,  # Negative change = stress
            'lookback_days': 60,
            'zscore_threshold': 2.0,
        },
    }

    def __init__(self):
        self._calculators: Dict[str, ZScoreCalculator] = {}
        self._history: Dict[str, List[TimeSeriesPoint]] = {}

        # Initialize calculators
        for indicator, config in self.INDICATORS.items():
            self._calculators[indicator] = ZScoreCalculator(
                lookback_days=config['lookback_days'],
                zscore_threshold=config['zscore_threshold'],
            )
            self._history[indicator] = []

    def add_observation(
        self,
        indicator: str,
        value: float,
        timestamp: datetime = None,
    ):
        """Add observation for an indicator"""
        if indicator not in self._history:
            return

        timestamp = timestamp or datetime.utcnow()
        self._history[indicator].append(TimeSeriesPoint(timestamp, value))

        # Trim old history (keep 2x lookback)
        config = self.INDICATORS.get(indicator, {})
        max_days = config.get('lookback_days', 90) * 2
        cutoff = datetime.utcnow() - timedelta(days=max_days)
        self._history[indicator] = [
            p for p in self._history[indicator]
            if p.timestamp > cutoff
        ]

    def detect_all(
        self,
        current_values: Dict[str, float],
    ) -> List[RegimeAlert]:
        """Detect regime shifts across all indicators"""
        alerts = []

        for indicator, value in current_values.items():
            if indicator not in self.INDICATORS:
                continue

            config = self.INDICATORS[indicator]
            calculator = self._calculators[indicator]
            history = self._history.get(indicator, [])

            alert = calculator.detect_regime_shift(
                indicator=indicator,
                current=value,
                history=history,
                higher_is_stress=config['higher_is_stress'],
            )

            if alert:
                alerts.append(alert)

        return alerts

    def get_regime_summary(
        self,
        current_values: Dict[str, float],
    ) -> Dict[str, Any]:
        """Get summary of current regime status"""
        alerts = self.detect_all(current_values)

        stress_alerts = [a for a in alerts if a.direction == 'stress']
        easing_alerts = [a for a in alerts if a.direction == 'easing']

        # Determine overall regime
        if len(stress_alerts) >= 3:
            regime = 'crisis'
        elif len(stress_alerts) >= 2:
            regime = 'stress'
        elif len(stress_alerts) >= 1:
            regime = 'elevated'
        elif len(easing_alerts) >= 2:
            regime = 'calm'
        else:
            regime = 'normal'

        return {
            'regime': regime,
            'stress_indicators': len(stress_alerts),
            'easing_indicators': len(easing_alerts),
            'alerts': [a.to_dict() for a in alerts],
            'timestamp': datetime.utcnow().isoformat(),
        }
