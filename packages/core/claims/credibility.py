"""
Enhanced Credibility Scoring

Calculates credibility score (0-100) for claims based on multiple factors.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class CredibilityFactors:
    """Factors that influence credibility score"""
    # Source factors
    account_age_days: Optional[int] = None
    account_karma: Optional[int] = None
    author_history_score: Optional[float] = None  # 0-1, based on past accuracy

    # Content factors
    has_evidence: bool = False
    has_document: bool = False
    has_link: bool = False
    has_screenshot: bool = False

    # Engagement factors
    upvotes: int = 0
    comments: int = 0
    shares: int = 0

    # Cross-source factors
    corroboration_count: int = 0  # Same claim from other sources
    corroboration_window_hours: int = 24

    # Penalty factors
    has_absolute_language: bool = False
    has_sensationalism: bool = False
    has_conspiracy_markers: bool = False
    is_new_account: bool = False

    def to_dict(self) -> Dict:
        return {
            'source': {
                'account_age_days': self.account_age_days,
                'account_karma': self.account_karma,
                'author_history_score': self.author_history_score,
            },
            'content': {
                'has_evidence': self.has_evidence,
                'has_document': self.has_document,
                'has_link': self.has_link,
                'has_screenshot': self.has_screenshot,
            },
            'engagement': {
                'upvotes': self.upvotes,
                'comments': self.comments,
                'shares': self.shares,
            },
            'corroboration': {
                'count': self.corroboration_count,
                'window_hours': self.corroboration_window_hours,
            },
            'penalties': {
                'absolute_language': self.has_absolute_language,
                'sensationalism': self.has_sensationalism,
                'conspiracy_markers': self.has_conspiracy_markers,
                'new_account': self.is_new_account,
            },
        }


@dataclass
class CredibilityScore:
    """Result of credibility calculation"""
    score: int  # 0-100
    level: str  # high, medium, low, very_low
    factors: CredibilityFactors
    breakdown: Dict[str, int]  # Component contributions
    calculated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'score': self.score,
            'level': self.level,
            'factors': self.factors.to_dict(),
            'breakdown': self.breakdown,
            'calculated_at': self.calculated_at.isoformat(),
        }


def calculate_credibility(factors: CredibilityFactors) -> CredibilityScore:
    """
    Calculate credibility score (0-100).

    Component weights:
    - Account history: 0-20 points
    - Evidence presence: 0-25 points
    - Engagement: 0-15 points
    - Cross-source corroboration: 0-25 points
    - Base score: 15 points

    Penalties:
    - Absolute language: -15
    - Sensationalism: -10
    - Conspiracy markers: -20
    - New account: -10
    """
    score = 15  # Base score
    breakdown = {'base': 15}

    # ==================== Account History (0-20) ====================
    account_score = 0

    if factors.account_age_days is not None:
        if factors.account_age_days >= 365:
            account_score += 10
        elif factors.account_age_days >= 180:
            account_score += 7
        elif factors.account_age_days >= 90:
            account_score += 5
        elif factors.account_age_days >= 30:
            account_score += 2

    if factors.account_karma is not None:
        if factors.account_karma >= 10000:
            account_score += 5
        elif factors.account_karma >= 5000:
            account_score += 3
        elif factors.account_karma >= 1000:
            account_score += 2

    if factors.author_history_score is not None:
        account_score += int(factors.author_history_score * 5)

    account_score = min(account_score, 20)
    breakdown['account_history'] = account_score
    score += account_score

    # ==================== Evidence (0-25) ====================
    evidence_score = 0

    if factors.has_document:
        evidence_score += 15
    if factors.has_screenshot:
        evidence_score += 10
    if factors.has_link:
        evidence_score += 5
    if factors.has_evidence:
        evidence_score += 5

    evidence_score = min(evidence_score, 25)
    breakdown['evidence'] = evidence_score
    score += evidence_score

    # ==================== Engagement (0-15) ====================
    engagement_score = 0
    total_engagement = factors.upvotes + factors.comments + factors.shares

    if total_engagement >= 1000:
        engagement_score = 15
    elif total_engagement >= 500:
        engagement_score = 12
    elif total_engagement >= 200:
        engagement_score = 9
    elif total_engagement >= 100:
        engagement_score = 6
    elif total_engagement >= 50:
        engagement_score = 3

    breakdown['engagement'] = engagement_score
    score += engagement_score

    # ==================== Corroboration (0-25) ====================
    corroboration_score = 0

    if factors.corroboration_count >= 5:
        corroboration_score = 25
    elif factors.corroboration_count >= 3:
        corroboration_score = 20
    elif factors.corroboration_count >= 2:
        corroboration_score = 15
    elif factors.corroboration_count >= 1:
        corroboration_score = 8

    breakdown['corroboration'] = corroboration_score
    score += corroboration_score

    # ==================== Penalties ====================
    penalties = 0

    if factors.has_absolute_language:
        penalties += 15
    if factors.has_sensationalism:
        penalties += 10
    if factors.has_conspiracy_markers:
        penalties += 20
    if factors.is_new_account:
        penalties += 10

    breakdown['penalties'] = -penalties
    score -= penalties

    # ==================== Final Score ====================
    final_score = max(0, min(100, score))

    # Determine level
    if final_score >= 80:
        level = 'high'
    elif final_score >= 60:
        level = 'medium'
    elif final_score >= 40:
        level = 'low'
    else:
        level = 'very_low'

    return CredibilityScore(
        score=final_score,
        level=level,
        factors=factors,
        breakdown=breakdown,
    )


def quick_credibility_check(
    upvotes: int = 0,
    comments: int = 0,
    has_link: bool = False,
    account_age_days: int = None,
    corroboration_count: int = 0,
) -> int:
    """Quick credibility score with minimal inputs"""
    factors = CredibilityFactors(
        upvotes=upvotes,
        comments=comments,
        has_link=has_link,
        account_age_days=account_age_days,
        corroboration_count=corroboration_count,
    )
    result = calculate_credibility(factors)
    return result.score


def should_escalate(score: int, claim_type: str) -> bool:
    """Determine if claim should be escalated for urgent review"""
    # High credibility always escalates
    if score >= 80:
        return True

    # Critical claim types with medium credibility
    if claim_type in ('nationalization', 'liquidity') and score >= 60:
        return True

    # High severity with decent credibility
    if claim_type in ('investigation', 'delivery') and score >= 70:
        return True

    return False
