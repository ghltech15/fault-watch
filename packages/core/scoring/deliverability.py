"""
Deliverability Stress Scoring Engine

Calculates deliverability stress score (0-100) based on physical market indicators.

Components:
- COMEX coverage ratio
- Days of supply
- Delivery notices acceleration
- Dealer tightness (premiums, OOS rate)
- Inventory velocity

Price is used as a MULTIPLIER, not a primary driver.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ComexIndicators:
    """COMEX-related indicators"""
    # Coverage (paper to physical)
    coverage_ratio: Optional[float] = None      # Open interest / Registered

    # Supply
    days_of_supply: Optional[float] = None
    registered_oz: Optional[float] = None
    registered_change_pct: Optional[float] = None  # Week-over-week

    # Delivery
    delivery_notices: Optional[int] = None
    delivery_notices_acceleration: Optional[float] = None  # Week-over-week change %


@dataclass
class DealerIndicators:
    """Dealer market indicators"""
    # Premiums (percentage over spot)
    avg_premium_pct: float = 0
    min_premium_pct: float = 0
    max_premium_pct: float = 0

    # Availability
    out_of_stock_rate: float = 0        # Percentage of products OOS
    products_tracked: int = 0

    # Delays (days)
    avg_delivery_delay: Optional[float] = None


@dataclass
class DeliverabilityIndicators:
    """Combined deliverability indicators"""
    comex: ComexIndicators = field(default_factory=ComexIndicators)
    dealers: DealerIndicators = field(default_factory=DealerIndicators)

    # Current price (for multiplier only)
    silver_price: Optional[float] = None
    gold_price: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            'comex': {
                'coverage_ratio': self.comex.coverage_ratio,
                'days_of_supply': self.comex.days_of_supply,
                'registered_oz': self.comex.registered_oz,
                'registered_change_pct': self.comex.registered_change_pct,
                'delivery_notices': self.comex.delivery_notices,
                'delivery_notices_acceleration': self.comex.delivery_notices_acceleration,
            },
            'dealers': {
                'avg_premium_pct': self.dealers.avg_premium_pct,
                'min_premium_pct': self.dealers.min_premium_pct,
                'max_premium_pct': self.dealers.max_premium_pct,
                'out_of_stock_rate': self.dealers.out_of_stock_rate,
                'products_tracked': self.dealers.products_tracked,
                'avg_delivery_delay': self.dealers.avg_delivery_delay,
            },
            'prices': {
                'silver': self.silver_price,
                'gold': self.gold_price,
            },
        }


@dataclass
class DeliverabilityScore:
    """Result of deliverability stress calculation"""
    score: float                          # 0-100
    drivers: List[str]                    # Human-readable explanations
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    # Component scores (before price multiplier)
    coverage_ratio_score: float = 0       # From COMEX coverage
    days_of_supply_score: float = 0       # From supply days
    delivery_velocity_score: float = 0    # From delivery acceleration
    dealer_premium_score: float = 0       # From dealer premiums
    dealer_oos_score: float = 0           # From out-of-stock rate
    inventory_velocity_score: float = 0   # From registered changes

    # Base score (before price multiplier)
    base_score: float = 0

    # Price multiplier applied
    price_multiplier: float = 1.0

    # Raw indicators
    indicators: Optional[DeliverabilityIndicators] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'score': round(self.score, 1),
            'base_score': round(self.base_score, 1),
            'price_multiplier': round(self.price_multiplier, 2),
            'drivers': self.drivers,
            'calculated_at': self.calculated_at.isoformat(),
            'components': {
                'coverage_ratio': round(self.coverage_ratio_score, 1),
                'days_of_supply': round(self.days_of_supply_score, 1),
                'delivery_velocity': round(self.delivery_velocity_score, 1),
                'dealer_premium': round(self.dealer_premium_score, 1),
                'dealer_oos': round(self.dealer_oos_score, 1),
                'inventory_velocity': round(self.inventory_velocity_score, 1),
            },
            'indicators': self.indicators.to_dict() if self.indicators else None,
        }


def calculate_deliverability_stress(
    indicators: DeliverabilityIndicators,
) -> DeliverabilityScore:
    """
    Calculate deliverability stress score (0-100).

    Component weights (base score):
    - Coverage ratio: 0-30 points
    - Days of supply: 0-25 points
    - Delivery velocity: 0-15 points
    - Dealer premiums: 0-15 points
    - Dealer OOS rate: 0-10 points
    - Inventory velocity: 0-5 points

    Price multiplier:
    - Silver $50-80: 1.15x
    - Silver $80-100: 1.3x
    - Silver $100+: 1.5x

    Args:
        indicators: Current deliverability indicators

    Returns:
        DeliverabilityScore with score 0-100 and drivers
    """
    base_score = 0.0
    drivers = []
    result = DeliverabilityScore(score=0, drivers=[], indicators=indicators)
    comex = indicators.comex
    dealers = indicators.dealers

    # ==================== Component 1: Coverage Ratio (0-30) ====================
    if comex.coverage_ratio is not None:
        if comex.coverage_ratio >= 10:
            coverage_score = 30
            drivers.append(f"Coverage ratio extreme: {comex.coverage_ratio:.1f}x paper to physical")
        elif comex.coverage_ratio >= 7:
            coverage_score = 25
            drivers.append(f"Coverage ratio critical: {comex.coverage_ratio:.1f}x")
        elif comex.coverage_ratio >= 5:
            coverage_score = 20
            drivers.append(f"Coverage ratio elevated: {comex.coverage_ratio:.1f}x")
        elif comex.coverage_ratio >= 3:
            coverage_score = 12
        elif comex.coverage_ratio >= 2:
            coverage_score = 6
        else:
            coverage_score = 0

        result.coverage_ratio_score = coverage_score
        base_score += coverage_score

    # ==================== Component 2: Days of Supply (0-25) ====================
    if comex.days_of_supply is not None:
        if comex.days_of_supply <= 5:
            supply_score = 25
            drivers.append(f"Critical supply: only {comex.days_of_supply:.0f} days")
        elif comex.days_of_supply <= 10:
            supply_score = 20
            drivers.append(f"Low supply: {comex.days_of_supply:.0f} days")
        elif comex.days_of_supply <= 15:
            supply_score = 15
        elif comex.days_of_supply <= 20:
            supply_score = 10
        elif comex.days_of_supply <= 30:
            supply_score = 5
        else:
            supply_score = 0

        result.days_of_supply_score = supply_score
        base_score += supply_score

    # ==================== Component 3: Delivery Velocity (0-15) ====================
    if comex.delivery_notices_acceleration is not None:
        accel = comex.delivery_notices_acceleration
        if accel >= 100:  # Delivery notices doubled
            velocity_score = 15
            drivers.append(f"Delivery notices surging: +{accel:.0f}%")
        elif accel >= 50:
            velocity_score = 12
            drivers.append(f"Delivery notices accelerating: +{accel:.0f}%")
        elif accel >= 25:
            velocity_score = 8
        elif accel >= 10:
            velocity_score = 4
        else:
            velocity_score = 0

        result.delivery_velocity_score = velocity_score
        base_score += velocity_score

    # ==================== Component 4: Dealer Premiums (0-15) ====================
    if dealers.avg_premium_pct > 0:
        if dealers.avg_premium_pct >= 50:
            premium_score = 15
            drivers.append(f"Extreme dealer premium: {dealers.avg_premium_pct:.0f}%")
        elif dealers.avg_premium_pct >= 30:
            premium_score = 12
            drivers.append(f"High dealer premium: {dealers.avg_premium_pct:.0f}%")
        elif dealers.avg_premium_pct >= 20:
            premium_score = 8
        elif dealers.avg_premium_pct >= 15:
            premium_score = 5
        elif dealers.avg_premium_pct >= 10:
            premium_score = 2
        else:
            premium_score = 0

        result.dealer_premium_score = premium_score
        base_score += premium_score

    # ==================== Component 5: Dealer OOS Rate (0-10) ====================
    if dealers.out_of_stock_rate > 0:
        if dealers.out_of_stock_rate >= 70:
            oos_score = 10
            drivers.append(f"Severe shortage: {dealers.out_of_stock_rate:.0f}% OOS")
        elif dealers.out_of_stock_rate >= 50:
            oos_score = 8
            drivers.append(f"High shortage: {dealers.out_of_stock_rate:.0f}% OOS")
        elif dealers.out_of_stock_rate >= 30:
            oos_score = 5
        elif dealers.out_of_stock_rate >= 20:
            oos_score = 3
        else:
            oos_score = 0

        result.dealer_oos_score = oos_score
        base_score += oos_score

    # ==================== Component 6: Inventory Velocity (0-5) ====================
    if comex.registered_change_pct is not None:
        change = comex.registered_change_pct
        if change <= -10:  # 10%+ outflow
            inv_score = 5
            drivers.append(f"Rapid inventory drain: {change:.1f}%")
        elif change <= -5:
            inv_score = 3
        elif change <= -2:
            inv_score = 1
        else:
            inv_score = 0

        result.inventory_velocity_score = inv_score
        base_score += inv_score

    # ==================== Price Multiplier ====================
    # Price amplifies existing stress - it's not a primary driver
    multiplier = 1.0

    if indicators.silver_price:
        price = indicators.silver_price
        if price >= 100:
            multiplier = 1.5
        elif price >= 80:
            multiplier = 1.3
        elif price >= 50:
            multiplier = 1.15
        elif price >= 40:
            multiplier = 1.05

    result.base_score = min(base_score, 100)
    result.price_multiplier = multiplier

    # ==================== Final Score ====================
    final_score = base_score * multiplier
    result.score = min(final_score, 100)
    result.drivers = drivers[:5]  # Top 5 drivers

    return result


def get_deliverability_level(score: float) -> str:
    """Get human-readable level from score"""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "SEVERE"
    elif score >= 40:
        return "ELEVATED"
    elif score >= 20:
        return "MODERATE"
    else:
        return "NORMAL"


def get_deliverability_color(score: float) -> str:
    """Get color for score"""
    if score >= 80:
        return "darkred"
    elif score >= 60:
        return "red"
    elif score >= 40:
        return "orange"
    elif score >= 20:
        return "yellow"
    else:
        return "green"


# Convenience function for quick assessment
def quick_deliverability_assessment(
    coverage_ratio: float = None,
    days_of_supply: float = None,
    avg_premium_pct: float = None,
    oos_rate: float = None,
    silver_price: float = None,
) -> DeliverabilityScore:
    """Quick deliverability stress assessment with minimal inputs"""
    comex = ComexIndicators(
        coverage_ratio=coverage_ratio,
        days_of_supply=days_of_supply,
    )
    dealers = DealerIndicators(
        avg_premium_pct=avg_premium_pct or 0,
        out_of_stock_rate=oos_rate or 0,
    )
    indicators = DeliverabilityIndicators(
        comex=comex,
        dealers=dealers,
        silver_price=silver_price,
    )
    return calculate_deliverability_stress(indicators)
