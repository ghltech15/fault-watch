"""
Reddit Collector for Social Claims

Collects posts from financial subreddits and extracts claims
about banks, markets, and precious metals.

Trust Tier: 3 (Social) - Creates CLAIMS, not EVENTS
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..base import BaseCollector, TrustTier

logger = logging.getLogger(__name__)


# Subreddits to monitor for financial claims
MONITORED_SUBREDDITS = [
    'wallstreetsilver',
    'silverbugs',
    'gold',
    'economics',
    'finance',
    'investing',
    'stocks',
    'banking',
]

# Keywords that indicate potentially relevant posts
RELEVANCE_KEYWORDS = [
    # Banks
    'bank', 'banking', 'banks', 'fdic', 'bailout', 'bail out',
    'nationalize', 'nationalization', 'failure', 'collapse',
    # Investigations
    'sec', 'cftc', 'investigation', 'probe', 'subpoena', 'fraud',
    'manipulation', 'spoofing', 'whistleblower',
    # Precious metals
    'silver', 'gold', 'comex', 'delivery', 'shortage', 'premium',
    'out of stock', 'oos', 'vault', 'registered',
    # Liquidity
    'liquidity', 'run on', 'withdrawal', 'deposits', 'insolvency',
]


@dataclass
class RedditPost:
    """Raw Reddit post data"""
    id: str
    title: str
    selftext: str
    subreddit: str
    author: str
    score: int
    num_comments: int
    url: str
    permalink: str
    created_utc: float
    is_self: bool


class RedditCollector(BaseCollector):
    """
    Collects claims from Reddit financial subreddits.

    Uses Reddit's JSON API (no authentication required for public posts).
    Rate limited to avoid 429 errors.

    Trust Tier: 3 - Social (creates Claims, not Events)
    """

    source_name = "Reddit"
    trust_tier = TrustTier.TIER_3_SOCIAL
    frequency_minutes = 15  # Check every 15 minutes

    def __init__(self, fetcher=None, db=None):
        super().__init__(fetcher, db)
        self.subreddits = MONITORED_SUBREDDITS
        self.min_score = 10  # Minimum upvotes to consider
        self.posts_per_subreddit = 25  # Hot posts to fetch

    async def collect(self) -> Dict[str, Any]:
        """Collect posts from monitored subreddits"""
        results = {
            'claims_created': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'posts_processed': 0,
        }

        for subreddit in self.subreddits:
            try:
                posts = await self._fetch_subreddit_posts(subreddit)

                for post in posts:
                    results['posts_processed'] += 1

                    # Check relevance
                    if not self._is_relevant(post):
                        continue

                    # Check minimum engagement
                    if post.score < self.min_score:
                        continue

                    # Create claim from post
                    claim_result = await self._create_claim_from_post(post)

                    if claim_result == 'created':
                        results['claims_created'] += 1
                    elif claim_result == 'duplicate':
                        results['duplicates_skipped'] += 1
                    elif claim_result == 'error':
                        results['errors'] += 1

                # Rate limiting between subreddits
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error collecting from r/{subreddit}: {e}")
                results['errors'] += 1

        return results

    async def _fetch_subreddit_posts(self, subreddit: str) -> List[RedditPost]:
        """Fetch hot posts from a subreddit using JSON API"""
        posts = []

        url = f"https://www.reddit.com/r/{subreddit}/hot.json"
        params = {
            'limit': self.posts_per_subreddit,
            'raw_json': 1,
        }

        try:
            data = await self.fetcher.fetch_json(url, params=params)

            if not data or 'data' not in data:
                return posts

            for child in data['data'].get('children', []):
                post_data = child.get('data', {})

                post = RedditPost(
                    id=post_data.get('id', ''),
                    title=post_data.get('title', ''),
                    selftext=post_data.get('selftext', ''),
                    subreddit=post_data.get('subreddit', subreddit),
                    author=post_data.get('author', '[deleted]'),
                    score=post_data.get('score', 0),
                    num_comments=post_data.get('num_comments', 0),
                    url=post_data.get('url', ''),
                    permalink=post_data.get('permalink', ''),
                    created_utc=post_data.get('created_utc', 0),
                    is_self=post_data.get('is_self', True),
                )
                posts.append(post)

        except Exception as e:
            logger.error(f"Failed to fetch r/{subreddit}: {e}")

        return posts

    def _is_relevant(self, post: RedditPost) -> bool:
        """Check if post contains relevant financial keywords"""
        text = f"{post.title} {post.selftext}".lower()

        for keyword in RELEVANCE_KEYWORDS:
            if keyword in text:
                return True

        return False

    async def _create_claim_from_post(self, post: RedditPost) -> str:
        """
        Create a claim record from a Reddit post.

        Returns: 'created', 'duplicate', 'error', or 'skipped'
        """
        from packages.core.claims import (
            SocialPost,
            ClaimExtractor,
            CredibilityFactors,
            calculate_credibility,
        )

        try:
            # Convert to SocialPost format
            social_post = SocialPost(
                title=post.title,
                content=post.selftext,
                url=f"https://reddit.com{post.permalink}",
                author=post.author,
                subreddit=post.subreddit,
                score=post.score,
                num_comments=post.num_comments,
                timestamp=datetime.utcfromtimestamp(post.created_utc),
            )

            # Extract claims
            extractor = ClaimExtractor()
            extracted_claims = extractor.extract_claims(social_post)

            if not extracted_claims:
                return 'skipped'

            # Calculate credibility for each claim
            for claim in extracted_claims:
                factors = CredibilityFactors(
                    upvotes=post.score,
                    comments=post.num_comments,
                    has_link='http' in post.selftext or 'http' in post.title,
                    has_sensationalism='!!' in post.title or '!!' in post.selftext,
                )

                cred_score = calculate_credibility(factors)

                # Store claim if DB available
                if self.db:
                    # Check for duplicate
                    existing = await self._check_duplicate(post.id, claim.claim_type)
                    if existing:
                        return 'duplicate'

                    await self._store_claim(claim, cred_score, post)

            return 'created'

        except Exception as e:
            logger.error(f"Error creating claim from post {post.id}: {e}")
            return 'error'

    async def _check_duplicate(self, post_id: str, claim_type: str) -> bool:
        """Check if we've already processed this post for this claim type"""
        if not self.db:
            return False

        # Check by URL pattern
        url_pattern = f"%reddit.com%{post_id}%"
        existing = await self.db.execute(
            "SELECT id FROM claims WHERE url LIKE $1 AND claim_type = $2",
            url_pattern, claim_type
        )
        return bool(existing)

    async def _store_claim(self, claim, cred_score, post: RedditPost):
        """Store claim in database"""
        if not self.db:
            return

        await self.db.execute("""
            INSERT INTO claims (
                claim_text, claim_type, source_id, url, author,
                engagement, credibility_score, status, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'new', NOW())
        """,
            claim.claim_text[:500],
            claim.claim_type,
            await self._get_source_id(),
            f"https://reddit.com{post.permalink}",
            post.author,
            post.score + post.num_comments,
            cred_score.score,
        )

    async def _get_source_id(self):
        """Get or create source ID for Reddit"""
        if not self.db:
            return None

        result = await self.db.fetchrow(
            "SELECT id FROM sources WHERE name = 'Reddit'"
        )
        if result:
            return result['id']

        # Create source if not exists
        result = await self.db.fetchrow("""
            INSERT INTO sources (source_type, name, base_url, trust_tier, active)
            VALUES ('api', 'Reddit', 'https://reddit.com', 3, true)
            RETURNING id
        """)
        return result['id'] if result else None


# Collector registration
REDDIT_COLLECTORS = [
    (RedditCollector, 15),  # Every 15 minutes
]
