"""
Reddit Scraper
Monitors Reddit for silver/gold and financial crisis discussions
"""

import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'FaultWatch/1.0')


@dataclass
class RedditPost:
    id: str
    title: str
    selftext: str
    author: str
    subreddit: str
    score: int
    upvote_ratio: float
    num_comments: int
    created_utc: datetime
    url: str
    permalink: str
    link_flair_text: Optional[str]
    is_self: bool

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'selftext': self.selftext[:500] if self.selftext else '',
            'author': self.author,
            'subreddit': self.subreddit,
            'score': self.score,
            'upvote_ratio': self.upvote_ratio,
            'num_comments': self.num_comments,
            'created_utc': self.created_utc.isoformat(),
            'url': self.url,
            'permalink': f"https://reddit.com{self.permalink}",
            'link_flair_text': self.link_flair_text,
            'is_self': self.is_self,
        }


class RedditScraper:
    """Scrape Reddit for relevant discussions"""

    def __init__(self):
        self.client_id = REDDIT_CLIENT_ID
        self.client_secret = REDDIT_CLIENT_SECRET
        self.user_agent = REDDIT_USER_AGENT
        self.base_url = 'https://oauth.reddit.com'
        self.auth_url = 'https://www.reddit.com/api/v1/access_token'

        self.access_token = None
        self.token_expires = None

        # Target subreddits
        self.subreddits = [
            'wallstreetsilver',
            'silverbugs',
            'gold',
            'wallstreetbets',
            'stocks',
            'investing',
            'economics',
            'collapse',
            'preppers',
        ]

        # Search keywords
        self.keywords = [
            'silver squeeze',
            'comex',
            'physical silver',
            'bank collapse',
            'morgan stanley',
            'citigroup silver',
            'hsbc precious metals',
            'wells notice',
            'short squeeze',
            'silver manipulation',
            'gold manipulation',
            'federal reserve',
            'bank run',
        ]

        self.cache: Dict[str, List] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_fetch: Dict[str, datetime] = {}

    def _authenticate(self) -> bool:
        """Get Reddit OAuth token"""
        if not self.client_id or not self.client_secret:
            logger.warning("Reddit credentials not configured")
            return False

        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return True

        try:
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            data = {'grant_type': 'client_credentials'}
            headers = {'User-Agent': self.user_agent}

            response = requests.post(
                self.auth_url,
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expires = datetime.now() + timedelta(seconds=token_data['expires_in'] - 60)
            return True

        except Exception as e:
            logger.error(f"Reddit auth failed: {e}")
            return False

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Reddit API"""
        if not self._authenticate():
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': self.user_agent,
            }
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Reddit request failed: {e}")
            return None

    def get_subreddit_posts(
        self,
        subreddit: str,
        sort: str = 'hot',
        limit: int = 25,
        time_filter: str = 'day'
    ) -> List[RedditPost]:
        """Get posts from a subreddit"""
        cache_key = f'{subreddit}_{sort}_{time_filter}'

        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        params = {'limit': limit}
        if sort == 'top':
            params['t'] = time_filter

        endpoint = f'/r/{subreddit}/{sort}'
        data = self._make_request(endpoint, params)

        if not data:
            return self.cache.get(cache_key, [])

        posts = []
        for child in data.get('data', {}).get('children', []):
            post_data = child['data']
            post = RedditPost(
                id=post_data['id'],
                title=post_data['title'],
                selftext=post_data.get('selftext', ''),
                author=post_data['author'],
                subreddit=post_data['subreddit'],
                score=post_data['score'],
                upvote_ratio=post_data.get('upvote_ratio', 0),
                num_comments=post_data['num_comments'],
                created_utc=datetime.fromtimestamp(post_data['created_utc']),
                url=post_data['url'],
                permalink=post_data['permalink'],
                link_flair_text=post_data.get('link_flair_text'),
                is_self=post_data['is_self'],
            )
            posts.append(post)

        self.cache[cache_key] = posts
        self.last_fetch[cache_key] = datetime.now()

        return posts

    def search_reddit(
        self,
        query: str,
        subreddit: str = None,
        sort: str = 'relevance',
        time_filter: str = 'day',
        limit: int = 25
    ) -> List[RedditPost]:
        """Search Reddit for posts"""
        params = {
            'q': query,
            'sort': sort,
            't': time_filter,
            'limit': limit,
            'type': 'link',
        }
        if subreddit:
            params['restrict_sr'] = True
            endpoint = f'/r/{subreddit}/search'
        else:
            endpoint = '/search'

        data = self._make_request(endpoint, params)
        if not data:
            return []

        posts = []
        for child in data.get('data', {}).get('children', []):
            post_data = child['data']
            post = RedditPost(
                id=post_data['id'],
                title=post_data['title'],
                selftext=post_data.get('selftext', ''),
                author=post_data['author'],
                subreddit=post_data['subreddit'],
                score=post_data['score'],
                upvote_ratio=post_data.get('upvote_ratio', 0),
                num_comments=post_data['num_comments'],
                created_utc=datetime.fromtimestamp(post_data['created_utc']),
                url=post_data['url'],
                permalink=post_data['permalink'],
                link_flair_text=post_data.get('link_flair_text'),
                is_self=post_data['is_self'],
            )
            posts.append(post)

        return posts

    def get_all_subreddit_posts(self, limit_per_sub: int = 10) -> List[RedditPost]:
        """Get posts from all monitored subreddits"""
        all_posts = []

        for subreddit in self.subreddits:
            posts = self.get_subreddit_posts(subreddit, limit=limit_per_sub)
            all_posts.extend(posts)
            time.sleep(0.5)  # Rate limiting

        # Sort by score
        all_posts.sort(key=lambda x: x.score, reverse=True)
        return all_posts

    def search_all_keywords(self, limit_per_keyword: int = 10) -> List[RedditPost]:
        """Search for all monitored keywords"""
        all_posts = []
        seen_ids = set()

        for keyword in self.keywords:
            posts = self.search_reddit(keyword, limit=limit_per_keyword)
            for post in posts:
                if post.id not in seen_ids:
                    seen_ids.add(post.id)
                    all_posts.append(post)
            time.sleep(0.5)  # Rate limiting

        # Sort by score
        all_posts.sort(key=lambda x: x.score, reverse=True)
        return all_posts

    def get_trending_posts(self, min_score: int = 100) -> List[RedditPost]:
        """Get trending posts above score threshold"""
        all_posts = self.get_all_subreddit_posts(limit_per_sub=25)
        return [p for p in all_posts if p.score >= min_score]

    def get_dd_posts(self) -> List[RedditPost]:
        """Get Due Diligence posts"""
        dd_posts = []

        for subreddit in ['wallstreetsilver', 'silverbugs', 'wallstreetbets']:
            posts = self.get_subreddit_posts(subreddit, sort='hot', limit=50)
            for post in posts:
                flair = (post.link_flair_text or '').lower()
                if 'dd' in flair or 'due diligence' in flair or 'research' in flair:
                    dd_posts.append(post)

        return dd_posts

    def analyze_sentiment(self, posts: List[RedditPost]) -> Dict:
        """Basic sentiment analysis of posts"""
        bullish_keywords = ['squeeze', 'moon', 'buy', 'bullish', 'up', 'rising', 'breakout']
        bearish_keywords = ['crash', 'dump', 'sell', 'bearish', 'down', 'falling', 'collapse']

        bullish_count = 0
        bearish_count = 0
        neutral_count = 0

        for post in posts:
            text = f"{post.title} {post.selftext}".lower()
            bull_score = sum(1 for kw in bullish_keywords if kw in text)
            bear_score = sum(1 for kw in bearish_keywords if kw in text)

            if bull_score > bear_score:
                bullish_count += 1
            elif bear_score > bull_score:
                bearish_count += 1
            else:
                neutral_count += 1

        total = len(posts) or 1
        return {
            'bullish_pct': (bullish_count / total) * 100,
            'bearish_pct': (bearish_count / total) * 100,
            'neutral_pct': (neutral_count / total) * 100,
            'total_posts': len(posts),
            'avg_score': sum(p.score for p in posts) / total if posts else 0,
        }

    def get_summary(self) -> Dict:
        """Get Reddit monitoring summary"""
        hot_posts = self.get_all_subreddit_posts(limit_per_sub=10)
        trending = [p for p in hot_posts if p.score >= 100]
        sentiment = self.analyze_sentiment(hot_posts)

        return {
            'total_posts_fetched': len(hot_posts),
            'trending_posts': len(trending),
            'sentiment': sentiment,
            'top_posts': [p.to_dict() for p in hot_posts[:10]],
            'subreddits_monitored': len(self.subreddits),
            'last_updated': datetime.now().isoformat(),
        }
