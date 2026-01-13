"""
Unified Cascade Engine

Combines three component scores into a composite risk score (0-10).

Component Scores (0-100 each):
1. Funding Stress - Credit spreads, rate dislocations, facility usage
2. Enforcement Heat - Regulatory actions, multi-agency coordination
3. Deliverability Stress - COMEX metrics, dealer tightness

Cascade Trigger:
When 2+ component scores are elevated, the composite amplifies
to reflect systemic risk convergence.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .funding import FundingScore
from .enforcement import EnforcementScore
from .deliverability import DeliverabilityScore


@dataclass
class CompositeRisk:
    """
    Unified risk assessment combining all three component scores.

    Score: 0-10 scale
    - 0-1.5: STABLE
    - 1.5-2.5: MONITOR
    - 2.5-4: WATCH
    - 4-6: WARNING
    - 6-8: DANGER
    - 8-10: CRISIS
    """
    score: float                          # 0-10
    funding_component: float              # 0-10 (normalized from 0-100)
    enforcement_component: float          # 0-10 (normalized from 0-100)
    deliverability_component: float       # 0-10 (normalized from 0-100)

    # Cascade detection
    cascade_triggered: bool
    cascade_level: int                    # 0, 1, or 2

    # Weights used
    weights: Dict[str, float]

    # Human-readable explanations
    explain: Dict[str, List[str]]

    # Metadata
    entity_id: Optional[UUID] = None
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            'score': round(self.score, 2),
            'level': get_risk_level(self.score),
            'color': get_risk_color(self.score),
            'components': {
                'funding': round(self.funding_component, 2),
                'enforcement': round(self.enforcement_component, 2),
                'deliverability': round(self.deliverability_component, 2),
            },
            'cascade': {
                'triggered': self.cascade_triggered,
                'level': self.cascade_level,
            },
            'weights': self.weights,
            'explain': self.explain,
            'entity_id': str(self.entity_id) if self.entity_id else None,
            'calculated_at': self.calculated_at.isoformat(),
        }


# Default component weights
DEFAULT_WEIGHTS = {
    'funding': 0.35,
    'enforcement': 0.30,
    'deliverability': 0.35,
}

# Thresholds
HIGH_THRESHOLD = 50       # Score >= 50/100 is "high"
EXTREME_THRESHOLD = 70    # Score >= 70/100 is "extreme"


def calculate_composite_risk(
    funding: FundingScore,
    enforcement: EnforcementScore,
    deliverability: DeliverabilityScore,
    weights: Optional[Dict[str, float]] = None,
    entity_id: Optional[UUID] = None,
) -> CompositeRisk:
    """
    Calculate unified composite risk score (0-10).

    Algorithm:
    1. Normalize each component score to 0-10 scale
    2. Apply weighted sum
    3. Detect cascade conditions (2-of-3 convergence)
    4. Apply cascade multiplier if triggered

    Cascade Triggers:
    - Level 1: 2+ components >= HIGH_THRESHOLD (50) → 1.2x multiplier
    - Level 2: 1+ extreme (70) AND 2+ high (50) → 1.3x multiplier

    Args:
        funding: Funding stress score (0-100)
        enforcement: Enforcement heat score (0-100)
        deliverability: Deliverability stress score (0-100)
        weights: Optional custom weights (must sum to 1.0)
        entity_id: Optional entity this score applies to

    Returns:
        CompositeRisk with score 0-10 and cascade status
    """
    weights = weights or DEFAULT_WEIGHTS.copy()

    # Validate weights
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.01:
        # Normalize weights
        weights = {k: v / weight_sum for k, v in weights.items()}

    # Normalize each score to 0-10
    f_norm = funding.score / 10
    e_norm = enforcement.score / 10
    d_norm = deliverability.score / 10

    # Weighted sum (base composite)
    base_composite = (
        f_norm * weights['funding'] +
        e_norm * weights['enforcement'] +
        d_norm * weights['deliverability']
    )

    # Detect cascade conditions
    scores_100 = [funding.score, enforcement.score, deliverability.score]
    high_count = sum(1 for s in scores_100 if s >= HIGH_THRESHOLD)
    extreme_count = sum(1 for s in scores_100 if s >= EXTREME_THRESHOLD)

    cascade_triggered = False
    cascade_level = 0
    multiplier = 1.0

    if extreme_count >= 1 and high_count >= 2:
        # Level 2 cascade: one extreme + another high
        cascade_triggered = True
        cascade_level = 2
        multiplier = 1.3
    elif high_count >= 2:
        # Level 1 cascade: two or more high
        cascade_triggered = True
        cascade_level = 1
        multiplier = 1.2

    # Apply cascade multiplier
    final_score = base_composite * multiplier

    # Cap at 10
    final_score = min(final_score, 10.0)

    # Build explanation
    explain = {
        'funding_drivers': funding.drivers if hasattr(funding, 'drivers') else [],
        'enforcement_drivers': enforcement.drivers if hasattr(enforcement, 'drivers') else [],
        'deliverability_drivers': deliverability.drivers if hasattr(deliverability, 'drivers') else [],
    }

    if cascade_triggered:
        if cascade_level == 2:
            explain['cascade'] = [
                f"Level 2 cascade: {extreme_count} extreme + {high_count} high scores",
                "Multi-vector stress convergence detected",
                f"Multiplier: {multiplier}x applied",
            ]
        else:
            explain['cascade'] = [
                f"Level 1 cascade: {high_count} elevated scores",
                "Cross-sector stress emerging",
                f"Multiplier: {multiplier}x applied",
            ]
    else:
        explain['cascade'] = []

    return CompositeRisk(
        score=final_score,
        funding_component=f_norm,
        enforcement_component=e_norm,
        deliverability_component=d_norm,
        cascade_triggered=cascade_triggered,
        cascade_level=cascade_level,
        weights=weights,
        explain=explain,
        entity_id=entity_id,
    )


def get_risk_level(score: float) -> str:
    """Get human-readable risk level from composite score"""
    if score >= 8:
        return "CRISIS"
    elif score >= 6:
        return "DANGER"
    elif score >= 4:
        return "WARNING"
    elif score >= 2.5:
        return "WATCH"
    elif score >= 1.5:
        return "MONITOR"
    else:
        return "STABLE"


def get_risk_color(score: float) -> str:
    """Get color for risk level"""
    if score >= 8:
        return "darkred"
    elif score >= 6:
        return "red"
    elif score >= 4:
        return "orange"
    elif score >= 2.5:
        return "yellow"
    elif score >= 1.5:
        return "lightblue"
    else:
        return "green"


def get_risk_description(score: float) -> str:
    """Get description for risk level"""
    level = get_risk_level(score)
    descriptions = {
        "STABLE": "System operating normally, no significant stress indicators",
        "MONITOR": "Minor stress signals, routine monitoring recommended",
        "WATCH": "Elevated stress in one or more sectors, increased vigilance",
        "WARNING": "Significant stress, multiple warning signs present",
        "DANGER": "Critical stress levels, potential for rapid deterioration",
        "CRISIS": "Systemic crisis conditions, extreme caution warranted",
    }
    return descriptions.get(level, "Unknown status")


@dataclass
class DailyScoreSnapshot:
    """Daily composite score for an entity"""
    date: datetime
    entity_id: Optional[UUID]
    funding_stress: float
    enforcement_heat: float
    deliverability_stress: float
    composite_risk: float
    cascade_triggered: bool
    explain_json: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date.isoformat(),
            'entity_id': str(self.entity_id) if self.entity_id else None,
            'scores': {
                'funding_stress': round(self.funding_stress, 1),
                'enforcement_heat': round(self.enforcement_heat, 1),
                'deliverability_stress': round(self.deliverability_stress, 1),
                'composite_risk': round(self.composite_risk, 2),
            },
            'cascade_triggered': self.cascade_triggered,
            'explain': self.explain_json,
        }


def create_daily_snapshot(
    composite: CompositeRisk,
    date: Optional[datetime] = None,
) -> DailyScoreSnapshot:
    """Create a daily snapshot from composite risk for storage"""
    return DailyScoreSnapshot(
        date=date or datetime.utcnow(),
        entity_id=composite.entity_id,
        funding_stress=composite.funding_component * 10,  # Convert back to 0-100
        enforcement_heat=composite.enforcement_component * 10,
        deliverability_stress=composite.deliverability_component * 10,
        composite_risk=composite.score,
        cascade_triggered=composite.cascade_triggered,
        explain_json=composite.explain,
    )


# Quick assessment function
def quick_composite_assessment(
    funding_score: float,
    enforcement_score: float,
    deliverability_score: float,
) -> CompositeRisk:
    """Quick composite calculation with minimal inputs (scores 0-100)"""
    # Create minimal score objects
    funding = FundingScore(
        score=funding_score,
        drivers=[],
    )
    enforcement = EnforcementScore(
        score=enforcement_score,
        drivers=[],
        entity_id=None,
    )
    deliverability = DeliverabilityScore(
        score=deliverability_score,
        drivers=[],
    )

    return calculate_composite_risk(funding, enforcement, deliverability)
