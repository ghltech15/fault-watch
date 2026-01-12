"""
Enforcement Heat Scoring Engine

Calculates enforcement heat score (0-100) based on regulatory actions.

Factors:
- Recent enforcement actions (30-day window)
- Multi-agency coordination
- Action severity weights
- Tempo/acceleration (90-day trend)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID
from collections import defaultdict


# Severity weights for different action types
ACTION_SEVERITY = {
    # Highest severity - criminal/DOJ
    'criminal_referral': 40,
    'indictment': 40,
    # High severity - formal orders
    'cease_desist': 25,
    'consent_order': 20,
    'removal': 20,
    # Medium severity - investigations/settlements
    'wells_notice': 15,
    'settlement': 10,
    'penalty': 10,
    'civil_money_penalty': 10,
    # Lower severity - agreements/findings
    'formal_agreement': 8,
    'covered_action': 8,  # Whistleblower
    'enforcement': 5,     # Generic
    # Informational
    'spoofing': 15,
    'manipulation': 15,
    'fraud': 12,
    'position_limit_violation': 10,
}

# Regulator coordination multipliers
MULTI_AGENCY_MULTIPLIER = {
    2: 1.5,   # 2 agencies
    3: 2.0,   # 3 agencies
    4: 2.5,   # 4+ agencies
}

# Time windows
RECENT_WINDOW_DAYS = 30
TREND_WINDOW_DAYS = 90


@dataclass
class EnforcementScore:
    """Result of enforcement heat calculation"""
    score: float                          # 0-100
    drivers: List[str]                    # Human-readable explanations
    entity_id: Optional[UUID] = None
    entity_name: Optional[str] = None
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    # Component scores
    recent_action_score: float = 0        # From 30-day actions
    severity_score: float = 0             # From action types
    multi_agency_score: float = 0         # From coordination
    tempo_score: float = 0                # From acceleration

    # Raw data
    actions_30d: int = 0
    actions_90d: int = 0
    agencies_involved: List[str] = field(default_factory=list)
    action_types: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            'score': round(self.score, 1),
            'drivers': self.drivers,
            'entity_id': str(self.entity_id) if self.entity_id else None,
            'entity_name': self.entity_name,
            'calculated_at': self.calculated_at.isoformat(),
            'components': {
                'recent_action': round(self.recent_action_score, 1),
                'severity': round(self.severity_score, 1),
                'multi_agency': round(self.multi_agency_score, 1),
                'tempo': round(self.tempo_score, 1),
            },
            'raw': {
                'actions_30d': self.actions_30d,
                'actions_90d': self.actions_90d,
                'agencies': self.agencies_involved,
                'action_types': self.action_types,
            },
        }


@dataclass
class EnforcementEvent:
    """Simplified event structure for scoring"""
    event_type: str
    source_name: str                      # Regulator name
    observed_at: datetime
    payload: Dict[str, Any]
    entity_id: Optional[UUID] = None


def calculate_enforcement_heat(
    entity_id: Optional[UUID],
    events: List[EnforcementEvent],
    entity_name: Optional[str] = None,
) -> EnforcementScore:
    """
    Calculate enforcement heat score for an entity.

    Args:
        entity_id: Entity UUID (can be None for market-wide)
        events: List of enforcement events
        entity_name: Optional entity name for display

    Returns:
        EnforcementScore with score 0-100 and drivers
    """
    now = datetime.utcnow()
    score = 0.0
    drivers = []

    # Filter to relevant events
    relevant_events = [
        e for e in events
        if entity_id is None or e.entity_id == entity_id
    ]

    # Time-windowed events
    events_30d = [
        e for e in relevant_events
        if e.observed_at > now - timedelta(days=RECENT_WINDOW_DAYS)
    ]
    events_90d = [
        e for e in relevant_events
        if e.observed_at > now - timedelta(days=TREND_WINDOW_DAYS)
    ]

    # Initialize score object
    result = EnforcementScore(
        score=0,
        drivers=[],
        entity_id=entity_id,
        entity_name=entity_name,
        actions_30d=len(events_30d),
        actions_90d=len(events_90d),
    )

    # ==================== Component 1: Recent Actions (0-25) ====================
    if events_30d:
        # Base score: 10 points per action, max 25
        recent_score = min(10 * len(events_30d), 25)
        result.recent_action_score = recent_score
        score += recent_score
        drivers.append(f"{len(events_30d)} enforcement action(s) in last 30 days")

    # ==================== Component 2: Severity (0-35) ====================
    severity_total = 0
    action_types = set()

    for event in events_30d:
        action_type = event.payload.get('action_type', 'enforcement')
        action_types.add(action_type)
        severity_total += ACTION_SEVERITY.get(action_type, 5)

    if severity_total > 0:
        # Cap at 35 points
        severity_score = min(severity_total, 35)
        result.severity_score = severity_score
        score += severity_score

        # Add driver for high-severity actions
        high_severity = [t for t in action_types if ACTION_SEVERITY.get(t, 0) >= 15]
        if high_severity:
            drivers.append(f"High-severity actions: {', '.join(high_severity)}")

    result.action_types = list(action_types)

    # ==================== Component 3: Multi-Agency (0-20) ====================
    agencies = set()
    for event in events_30d:
        regulator = event.payload.get('regulator') or event.source_name
        if regulator:
            agencies.add(regulator.upper())

    result.agencies_involved = list(agencies)

    if len(agencies) > 1:
        # Multi-agency coordination is a red flag
        multiplier = MULTI_AGENCY_MULTIPLIER.get(len(agencies), 2.5)

        # Base multi-agency score
        multi_score = 10 * (len(agencies) - 1)  # 10 per additional agency
        multi_score = min(multi_score, 20)

        result.multi_agency_score = multi_score
        score += multi_score

        # Apply multiplier to total score (partial)
        bonus = (score * (multiplier - 1)) * 0.3  # 30% of the multiplier effect
        score += bonus

        drivers.append(f"Multi-agency coordination: {', '.join(agencies)}")

    # ==================== Component 4: Tempo/Acceleration (0-20) ====================
    if len(events_90d) > len(events_30d):
        # Calculate acceleration
        # Events in first 60 days vs last 30 days
        events_60_30 = [
            e for e in events_90d
            if e.observed_at <= now - timedelta(days=30)
        ]

        if len(events_60_30) > 0:
            # Acceleration ratio
            ratio = len(events_30d) / max(len(events_60_30), 1)

            if ratio > 2:
                # Actions doubled - significant acceleration
                tempo_score = 20
                drivers.append("Enforcement tempo accelerating significantly")
            elif ratio > 1.5:
                tempo_score = 15
                drivers.append("Enforcement tempo increasing")
            elif ratio > 1:
                tempo_score = 10
            else:
                tempo_score = 0

            result.tempo_score = tempo_score
            score += tempo_score

    elif len(events_30d) > 0 and len(events_90d) == len(events_30d):
        # All events are recent - new enforcement cluster
        if len(events_30d) >= 2:
            tempo_score = 15
            result.tempo_score = tempo_score
            score += tempo_score
            drivers.append("New enforcement cluster in last 30 days")

    # ==================== Final Score ====================
    result.score = min(score, 100)  # Cap at 100
    result.drivers = drivers[:5]   # Limit to top 5 drivers

    return result


def calculate_market_enforcement_heat(events: List[EnforcementEvent]) -> EnforcementScore:
    """
    Calculate market-wide enforcement heat.

    Aggregates across all entities for systemic view.
    """
    return calculate_enforcement_heat(
        entity_id=None,
        events=events,
        entity_name="Market-Wide",
    )


def get_enforcement_level(score: float) -> str:
    """Get human-readable level from score"""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "ELEVATED"
    elif score >= 20:
        return "MODERATE"
    else:
        return "LOW"


def get_enforcement_color(score: float) -> str:
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


# Convenience functions for common queries

def get_entities_under_enforcement(
    events: List[EnforcementEvent],
    min_score: float = 30,
) -> List[EnforcementScore]:
    """Get all entities with enforcement heat above threshold"""
    # Group events by entity
    by_entity: Dict[UUID, List[EnforcementEvent]] = defaultdict(list)

    for event in events:
        if event.entity_id:
            by_entity[event.entity_id].append(event)

    # Calculate scores
    scores = []
    for entity_id, entity_events in by_entity.items():
        score = calculate_enforcement_heat(entity_id, entity_events)
        if score.score >= min_score:
            scores.append(score)

    # Sort by score descending
    scores.sort(key=lambda s: s.score, reverse=True)

    return scores


def detect_enforcement_cluster(
    events: List[EnforcementEvent],
    window_days: int = 14,
    min_events: int = 3,
) -> Optional[Dict]:
    """
    Detect enforcement cluster (multiple actions in short window).

    Returns cluster info if detected, None otherwise.
    """
    now = datetime.utcnow()
    window_start = now - timedelta(days=window_days)

    recent = [e for e in events if e.observed_at > window_start]

    if len(recent) >= min_events:
        # Group by entity
        by_entity: Dict[Optional[UUID], int] = defaultdict(int)
        agencies = set()

        for event in recent:
            by_entity[event.entity_id] += 1
            regulator = event.payload.get('regulator') or event.source_name
            if regulator:
                agencies.add(regulator)

        # Find most targeted entity
        most_targeted = max(by_entity.items(), key=lambda x: x[1])

        return {
            'detected': True,
            'window_days': window_days,
            'total_events': len(recent),
            'agencies_involved': list(agencies),
            'most_targeted_entity': most_targeted[0],
            'most_targeted_count': most_targeted[1],
            'is_multi_agency': len(agencies) > 1,
        }

    return None
