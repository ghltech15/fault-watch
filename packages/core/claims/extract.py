"""
Claim Extraction Engine

Extracts structured claims from social media posts and news articles.
Detects claim types, mentioned entities, and supporting evidence.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from ..entities import EntityResolver, Entity, extract_entities


# Claim type patterns
CLAIM_PATTERNS = {
    'nationalization': {
        'patterns': [
            r'\b(nationalized?|nationalizing|nationalisation)\b',
            r'\b(government\s+takeover|state\s+control)\b',
            r'\b(bail[\s-]?out|bailout|bailed\s+out)\b',
            r'\b(rescue\s+package|emergency\s+rescue)\b',
            r'\b(taken\s+over\s+by\s+(the\s+)?government)\b',
        ],
        'severity': 'critical',
        'requires_entity': True,
    },
    'investigation': {
        'patterns': [
            r'\b(under\s+investigation|being\s+investigated)\b',
            r'\b(probe|probing|probed)\b',
            r'\b(subpoena|subpoenaed)\b',
            r'\b(Wells\s+notice)\b',
            r'\b(inquiry|inquiries)\b',
            r'\b(DOJ|SEC|CFTC|FBI)\s+(investigation|probe|looking\s+into)\b',
        ],
        'severity': 'high',
        'requires_entity': True,
    },
    'liquidity': {
        'patterns': [
            r'\b(bank\s+run|run\s+on\s+(the\s+)?bank)\b',
            r'\b(liquidity\s+crisis|liquidity\s+crunch)\b',
            r'\b(withdrawal|withdrawals)\s+(surge|spike|limit)\b',
            r'\b(deposit\s+flight|deposits?\s+(leaving|fleeing))\b',
            r'\b(insolvenc[ey]|insolvent)\b',
            r'\b(bankruptcy|bankrupt)\b',
            r'\b(can\'t\s+meet\s+(obligations|withdrawals))\b',
        ],
        'severity': 'critical',
        'requires_entity': True,
    },
    'delivery': {
        'patterns': [
            r'\b(delivery\s+failure|failed?\s+to\s+deliver)\b',
            r'\b(can\'t\s+deliver|cannot\s+deliver)\b',
            r'\b(no\s+silver|no\s+gold|out\s+of\s+(silver|gold))\b',
            r'\b(empty\s+vault|vault\s+is\s+empty)\b',
            r'\b(shortage|shortages)\b',
            r'\b(force\s+majeure)\b',
            r'\b(default(ed|ing)?)\s+on\s+delivery\b',
            r'\b(COMEX\s+(default|failure|crisis))\b',
        ],
        'severity': 'high',
        'requires_entity': False,
    },
    'fraud': {
        'patterns': [
            r'\b(fraud|fraudulent)\b',
            r'\b(manipulation|manipulating|manipulated)\b',
            r'\b(spoofing|spoofed)\b',
            r'\b(rigged|rigging)\b',
            r'\b(naked\s+short|naked\s+shorting)\b',
            r'\b(paper\s+(silver|gold))\b',
            r'\b(price\s+suppression)\b',
        ],
        'severity': 'medium',
        'requires_entity': False,
    },
    'insider': {
        'patterns': [
            r'\b(insider|inside\s+source)\b',
            r'\b(whistleblower)\b',
            r'\b(leaked|leak)\b',
            r'\b(confidential\s+(source|information))\b',
            r'\b(source\s+says|sources?\s+claim)\b',
            r'\b(according\s+to\s+(a\s+)?source)\b',
        ],
        'severity': 'medium',
        'requires_entity': False,
    },
    'price_target': {
        'patterns': [
            r'\b(silver|gold)\s+(will|going\s+to)\s+(\$|hit\s+\$?)[\d,]+\b',
            r'\b(target\s+price|price\s+target)\s*(of\s+)?\$?[\d,]+\b',
            r'\b(price\s+prediction)\b',
            r'\b(to\s+the\s+moon|moon(ing)?)\b',
            r'\b(squeeze|short\s+squeeze)\b',
            r'\$[\d,]+\s+(silver|gold)\b',
        ],
        'severity': 'low',
        'requires_entity': False,
    },
}

# Evidence indicators (adds credibility)
EVIDENCE_PATTERNS = {
    'document': [
        r'\b(document|filing|report)\b',
        r'\b(screenshot|screen\s+shot)\b',
        r'\b(sec\.gov|cftc\.gov|occ\.gov)\b',
        r'\b(form\s+(10-K|10-Q|8-K|4))\b',
    ],
    'official_source': [
        r'\b(official|officially)\b',
        r'\b(confirmed\s+by|according\s+to)\s+(SEC|CFTC|OCC|FDIC|Fed)\b',
        r'\b(press\s+release|announcement)\b',
    ],
    'link': [
        r'https?://[^\s]+',
    ],
}

# Penalty patterns (reduces credibility)
PENALTY_PATTERNS = {
    'absolute_language': [
        r'\b(guaranteed|100%|definitely|certainly)\b',
        r'\b(will\s+happen|going\s+to\s+happen)\b',
        r'\b(trust\s+me|believe\s+me)\b',
        r'\b(no\s+doubt|without\s+doubt)\b',
    ],
    'sensationalism': [
        r'\b(breaking|urgent|alert)\b',
        r'!!+',
        r'\b(wake\s+up|sheeple)\b',
        r'\b(they\s+don\'t\s+want\s+you\s+to\s+know)\b',
    ],
    'conspiracy': [
        r'\b(illuminati|cabal|deep\s+state)\b',
        r'\b(new\s+world\s+order|NWO)\b',
        r'\b(cover[\s-]?up)\b',
    ],
}


@dataclass
class ExtractedClaim:
    """A claim extracted from text"""
    claim_text: str
    claim_type: str
    severity: str
    entities_mentioned: List[Entity]
    evidence_indicators: List[str]
    penalty_indicators: List[str]
    confidence: float  # 0-1, based on pattern match quality
    source_url: Optional[str] = None
    author: Optional[str] = None
    engagement: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            'claim_text': self.claim_text,
            'claim_type': self.claim_type,
            'severity': self.severity,
            'entities': [e.name for e in self.entities_mentioned],
            'evidence': self.evidence_indicators,
            'penalties': self.penalty_indicators,
            'confidence': round(self.confidence, 2),
            'source_url': self.source_url,
            'author': self.author,
            'engagement': self.engagement,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class SocialPost:
    """Input social media post"""
    title: str
    content: str
    url: Optional[str] = None
    author: Optional[str] = None
    subreddit: Optional[str] = None
    score: int = 0
    num_comments: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_id: Optional[UUID] = None


class ClaimExtractor:
    """
    Extracts claims from social media posts and news.

    Features:
    - Pattern-based claim type detection
    - Entity extraction and linking
    - Evidence and penalty detection
    - Confidence scoring
    """

    def __init__(self, entity_resolver: EntityResolver = None):
        self.entity_resolver = entity_resolver or EntityResolver()
        self._compiled_patterns: Dict[str, List] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance"""
        for claim_type, config in CLAIM_PATTERNS.items():
            self._compiled_patterns[claim_type] = [
                re.compile(p, re.IGNORECASE)
                for p in config['patterns']
            ]

    def extract_claims(self, post: SocialPost) -> List[ExtractedClaim]:
        """
        Extract claims from a social post.

        Returns list of claims found in the post.
        """
        claims = []
        full_text = f"{post.title} {post.content}"
        text_lower = full_text.lower()

        # Extract entities mentioned
        entities = extract_entities(full_text)

        # Check each claim type
        for claim_type, config in CLAIM_PATTERNS.items():
            patterns = self._compiled_patterns[claim_type]

            for pattern in patterns:
                match = pattern.search(full_text)
                if match:
                    # Skip if requires entity but none found
                    if config.get('requires_entity') and not entities:
                        continue

                    # Extract evidence indicators
                    evidence = self._find_evidence(full_text)

                    # Extract penalty indicators
                    penalties = self._find_penalties(full_text)

                    # Calculate confidence
                    confidence = self._calculate_confidence(
                        match, entities, evidence, penalties, post
                    )

                    # Create claim
                    claim = ExtractedClaim(
                        claim_text=full_text[:500],  # Truncate
                        claim_type=claim_type,
                        severity=config['severity'],
                        entities_mentioned=entities,
                        evidence_indicators=evidence,
                        penalty_indicators=penalties,
                        confidence=confidence,
                        source_url=post.url,
                        author=post.author,
                        engagement=post.score + post.num_comments,
                        timestamp=post.timestamp,
                    )
                    claims.append(claim)
                    break  # One claim per type per post

        return claims

    def _find_evidence(self, text: str) -> List[str]:
        """Find evidence indicators in text"""
        found = []
        for evidence_type, patterns in EVIDENCE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found.append(evidence_type)
                    break
        return found

    def _find_penalties(self, text: str) -> List[str]:
        """Find penalty indicators in text"""
        found = []
        for penalty_type, patterns in PENALTY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    found.append(penalty_type)
                    break
        return found

    def _calculate_confidence(
        self,
        match: re.Match,
        entities: List[Entity],
        evidence: List[str],
        penalties: List[str],
        post: SocialPost,
    ) -> float:
        """Calculate confidence score for a claim"""
        confidence = 0.5  # Base

        # Entity boost
        if entities:
            confidence += 0.1 * min(len(entities), 3)

        # Evidence boost
        if 'document' in evidence:
            confidence += 0.15
        if 'official_source' in evidence:
            confidence += 0.15
        if 'link' in evidence:
            confidence += 0.05

        # Engagement boost (normalized)
        engagement = post.score + post.num_comments
        if engagement >= 1000:
            confidence += 0.1
        elif engagement >= 500:
            confidence += 0.07
        elif engagement >= 100:
            confidence += 0.05

        # Penalty deductions
        if 'absolute_language' in penalties:
            confidence -= 0.15
        if 'sensationalism' in penalties:
            confidence -= 0.1
        if 'conspiracy' in penalties:
            confidence -= 0.2

        return max(0.1, min(0.95, confidence))


def extract_claims_from_post(post: SocialPost) -> List[ExtractedClaim]:
    """Convenience function to extract claims"""
    extractor = ClaimExtractor()
    return extractor.extract_claims(post)


def extract_claims_batch(posts: List[SocialPost]) -> List[ExtractedClaim]:
    """Extract claims from multiple posts"""
    extractor = ClaimExtractor()
    all_claims = []
    for post in posts:
        claims = extractor.extract_claims(post)
        all_claims.extend(claims)
    return all_claims
