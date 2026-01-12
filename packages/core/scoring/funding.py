"""
Funding Stress Scoring Engine

Calculates funding stress score (0-100) based on liquidity indicators.

Components:
- Credit spreads (HY, IG)
- TED spread
- Rate dislocations (SOFR-EFFR, SOFR-IORB)
- Fed facility usage
- Deposit trends
- Stress indices
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class FundingIndicators:
    """Input indicators for funding stress calculation"""
    # Credit spreads (basis points)
    hy_spread: Optional[float] = None        # High yield OAS
    ig_spread: Optional[float] = None        # Investment grade OAS

    # Rate spreads (percentage)
    ted_spread: Optional[float] = None       # 3M LIBOR - 3M T-Bill
    sofr_effr_spread: Optional[float] = None # SOFR - EFFR
    sofr_iorb_spread: Optional[float] = None # SOFR - IORB

    # Fed facilities (billions)
    reverse_repo: Optional[float] = None
    discount_window: Optional[float] = None
    btfp_usage: Optional[float] = None
    h41_facility_change: Optional[float] = None  # Week-over-week change

    # Bank health
    deposit_change_pct: Optional[float] = None   # Week-over-week change
    reserve_balances: Optional[float] = None

    # Stress indices
    stlfsi: Optional[float] = None    # St. Louis Fed FSI
    nfci: Optional[float] = None      # Chicago Fed NFCI

    def to_dict(self) -> Dict:
        return {
            'credit_spreads': {
                'hy_spread': self.hy_spread,
                'ig_spread': self.ig_spread,
            },
            'rate_spreads': {
                'ted_spread': self.ted_spread,
                'sofr_effr_spread': self.sofr_effr_spread,
                'sofr_iorb_spread': self.sofr_iorb_spread,
            },
            'fed_facilities': {
                'reverse_repo': self.reverse_repo,
                'discount_window': self.discount_window,
                'btfp_usage': self.btfp_usage,
                'h41_facility_change': self.h41_facility_change,
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


@dataclass
class FundingScore:
    """Result of funding stress calculation"""
    score: float                          # 0-100
    drivers: List[str]                    # Human-readable explanations
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    # Component scores
    credit_spread_score: float = 0        # From HY/IG spreads
    ted_spread_score: float = 0           # From TED spread
    rate_dislocation_score: float = 0     # From SOFR spreads
    facility_usage_score: float = 0       # From Fed facilities
    deposit_score: float = 0              # From deposit trends
    stress_index_score: float = 0         # From STLFSI/NFCI

    # Raw indicators
    indicators: Optional[FundingIndicators] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'score': round(self.score, 1),
            'drivers': self.drivers,
            'calculated_at': self.calculated_at.isoformat(),
            'components': {
                'credit_spread': round(self.credit_spread_score, 1),
                'ted_spread': round(self.ted_spread_score, 1),
                'rate_dislocation': round(self.rate_dislocation_score, 1),
                'facility_usage': round(self.facility_usage_score, 1),
                'deposit': round(self.deposit_score, 1),
                'stress_index': round(self.stress_index_score, 1),
            },
            'indicators': self.indicators.to_dict() if self.indicators else None,
        }


def calculate_funding_stress(indicators: FundingIndicators) -> FundingScore:
    """
    Calculate funding stress score (0-100).

    Component weights:
    - Credit spreads: 0-25 points
    - TED spread: 0-20 points
    - Rate dislocations: 0-20 points
    - Fed facility usage: 0-15 points
    - Deposit trends: 0-10 points
    - Stress indices: 0-10 points

    Args:
        indicators: Current funding indicators

    Returns:
        FundingScore with score 0-100 and drivers
    """
    score = 0.0
    drivers = []
    result = FundingScore(score=0, drivers=[], indicators=indicators)

    # ==================== Component 1: Credit Spreads (0-25) ====================
    credit_score = 0

    # High yield spread
    if indicators.hy_spread is not None:
        if indicators.hy_spread >= 800:
            credit_score += 15
            drivers.append(f"HY spread critical: {indicators.hy_spread:.0f} bps")
        elif indicators.hy_spread >= 600:
            credit_score += 12
            drivers.append(f"HY spread elevated: {indicators.hy_spread:.0f} bps")
        elif indicators.hy_spread >= 500:
            credit_score += 8
        elif indicators.hy_spread >= 400:
            credit_score += 4

    # Investment grade spread
    if indicators.ig_spread is not None:
        if indicators.ig_spread >= 250:
            credit_score += 10
            drivers.append(f"IG spread critical: {indicators.ig_spread:.0f} bps")
        elif indicators.ig_spread >= 175:
            credit_score += 7
        elif indicators.ig_spread >= 150:
            credit_score += 5
        elif indicators.ig_spread >= 125:
            credit_score += 3

    result.credit_spread_score = min(credit_score, 25)
    score += result.credit_spread_score

    # ==================== Component 2: TED Spread (0-20) ====================
    if indicators.ted_spread is not None:
        if indicators.ted_spread >= 1.0:
            ted_score = 20
            drivers.append(f"TED spread crisis: {indicators.ted_spread:.2f}%")
        elif indicators.ted_spread >= 0.75:
            ted_score = 16
            drivers.append(f"TED spread elevated: {indicators.ted_spread:.2f}%")
        elif indicators.ted_spread >= 0.5:
            ted_score = 12
        elif indicators.ted_spread >= 0.35:
            ted_score = 8
        elif indicators.ted_spread >= 0.25:
            ted_score = 4
        else:
            ted_score = 0

        result.ted_spread_score = ted_score
        score += ted_score

    # ==================== Component 3: Rate Dislocations (0-20) ====================
    dislocation_score = 0

    # SOFR-EFFR spread (repo stress indicator)
    if indicators.sofr_effr_spread is not None:
        spread = abs(indicators.sofr_effr_spread)
        if spread >= 0.25:
            dislocation_score += 12
            drivers.append(f"SOFR-EFFR dislocation: {spread:.2f}%")
        elif spread >= 0.15:
            dislocation_score += 8
        elif spread >= 0.10:
            dislocation_score += 5
        elif spread >= 0.05:
            dislocation_score += 2

    # SOFR-IORB spread (arbitrage breakdown)
    if indicators.sofr_iorb_spread is not None:
        spread = abs(indicators.sofr_iorb_spread)
        if spread >= 0.20:
            dislocation_score += 8
            drivers.append(f"SOFR-IORB dislocation: {spread:.2f}%")
        elif spread >= 0.10:
            dislocation_score += 5
        elif spread >= 0.05:
            dislocation_score += 2

    result.rate_dislocation_score = min(dislocation_score, 20)
    score += result.rate_dislocation_score

    # ==================== Component 4: Fed Facility Usage (0-15) ====================
    facility_score = 0

    # Discount window usage (emergency lending)
    if indicators.discount_window is not None and indicators.discount_window > 0:
        if indicators.discount_window >= 50:  # $50B+
            facility_score += 10
            drivers.append(f"Discount window usage: ${indicators.discount_window:.0f}B")
        elif indicators.discount_window >= 20:
            facility_score += 7
        elif indicators.discount_window >= 5:
            facility_score += 4
        else:
            facility_score += 2

    # BTFP usage
    if indicators.btfp_usage is not None and indicators.btfp_usage > 0:
        if indicators.btfp_usage >= 100:  # $100B+
            facility_score += 5
        elif indicators.btfp_usage >= 50:
            facility_score += 3
        else:
            facility_score += 1

    # H.4.1 facility change (week-over-week increase)
    if indicators.h41_facility_change is not None:
        if indicators.h41_facility_change >= 50:  # $50B+ increase
            facility_score += 8
            drivers.append(f"Fed facility surge: +${indicators.h41_facility_change:.0f}B")
        elif indicators.h41_facility_change >= 20:
            facility_score += 5
        elif indicators.h41_facility_change >= 10:
            facility_score += 3

    result.facility_usage_score = min(facility_score, 15)
    score += result.facility_usage_score

    # ==================== Component 5: Deposit Trends (0-10) ====================
    if indicators.deposit_change_pct is not None:
        if indicators.deposit_change_pct <= -5:
            deposit_score = 10
            drivers.append(f"Severe deposit outflow: {indicators.deposit_change_pct:.1f}%")
        elif indicators.deposit_change_pct <= -3:
            deposit_score = 8
            drivers.append(f"Deposit outflow: {indicators.deposit_change_pct:.1f}%")
        elif indicators.deposit_change_pct <= -2:
            deposit_score = 6
        elif indicators.deposit_change_pct <= -1:
            deposit_score = 3
        else:
            deposit_score = 0

        result.deposit_score = deposit_score
        score += deposit_score

    # ==================== Component 6: Stress Indices (0-10) ====================
    stress_score = 0

    # St. Louis Fed Financial Stress Index
    if indicators.stlfsi is not None:
        if indicators.stlfsi >= 2.0:
            stress_score += 6
            drivers.append(f"STLFSI extreme: {indicators.stlfsi:.2f}")
        elif indicators.stlfsi >= 1.5:
            stress_score += 5
        elif indicators.stlfsi >= 1.0:
            stress_score += 4
        elif indicators.stlfsi >= 0.5:
            stress_score += 2
        elif indicators.stlfsi > 0:
            stress_score += 1

    # Chicago Fed NFCI
    if indicators.nfci is not None:
        if indicators.nfci >= 0.5:
            stress_score += 4
        elif indicators.nfci >= 0.25:
            stress_score += 3
        elif indicators.nfci > 0:
            stress_score += 2

    result.stress_index_score = min(stress_score, 10)
    score += result.stress_index_score

    # ==================== Final Score ====================
    result.score = min(score, 100)
    result.drivers = drivers[:5]  # Top 5 drivers

    return result


def get_funding_level(score: float) -> str:
    """Get human-readable level from score"""
    if score >= 80:
        return "CRISIS"
    elif score >= 60:
        return "SEVERE"
    elif score >= 40:
        return "ELEVATED"
    elif score >= 20:
        return "MODERATE"
    else:
        return "NORMAL"


def get_funding_color(score: float) -> str:
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
def quick_funding_assessment(
    hy_spread: float = None,
    ted_spread: float = None,
    deposit_change_pct: float = None,
    stlfsi: float = None,
) -> FundingScore:
    """Quick funding stress assessment with minimal inputs"""
    indicators = FundingIndicators(
        hy_spread=hy_spread,
        ted_spread=ted_spread,
        deposit_change_pct=deposit_change_pct,
        stlfsi=stlfsi,
    )
    return calculate_funding_stress(indicators)
