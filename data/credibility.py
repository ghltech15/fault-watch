"""
Credibility Filter
Filters social media posts for reliability and reduces noise
"""

from typing import Dict, List
from datetime import datetime
import re


class CredibilityFilter:
    """Filter social media posts for credibility"""

    def __init__(self):
        # Trusted sources (high credibility)
        self.trusted_twitter = [
            'federalreserve', 'neaboreis', 'SEC_News', 'ABOREIS',
            'Sprott', 'KitcoNews', 'Reuters', 'Bloomberg',
            'WSJ', 'FT', 'zaboreis', 'TFMetals', 'GoldTelegraph',
            'WallStreetSilv', 'SilverSqueeze', 'zerohedge',
        ]

        self.trusted_reddit_users = [
            # Add known reliable DD posters
            'Ditch_the_DeepState',
            'archertheprotector',
        ]

        # Red flags (reduce credibility)
        self.red_flags = [
            'trust me bro',
            'to the moon',
            'guaranteed',
            '100%',
            'cant go tits up',
            'financial advice',
            'not financial advice',
            'this is it',
            'happening',
            'its over',
            'diamond hands',
            'ape',
            'hodl',
            'yolo',
        ]

        # Verification patterns (increase credibility)
        self.verification_patterns = [
            r'source[:\s]',
            r'according to',
            r'sec\.gov',
            r'cftc\.gov',
            r'filing',
            r'report',
            r'data shows',
            r'official',
            r'confirmed',
            r'reuters',
            r'bloomberg',
            r'cme group',
            r'comex',
            r'lbma',
        ]

        # Minimum thresholds
        self.min_twitter_followers = 1000
        self.min_reddit_karma = 500
        self.min_reddit_account_age_days = 30

    def score_twitter_post(self, post: Dict) -> Dict:
        """Score a Twitter post for credibility"""
        score = 50  # Start neutral
        reasons = []

        # Check if trusted account
        username = post.get('username', '').lower()
        if username in [t.lower() for t in self.trusted_twitter]:
            score += 30
            reasons.append('Trusted account')

        # Check follower count
        followers = post.get('followers', 0)
        if followers > 100000:
            score += 15
            reasons.append('Large following')
        elif followers > 10000:
            score += 10
            reasons.append('Significant following')
        elif followers < self.min_twitter_followers:
            score -= 20
            reasons.append('Low follower count')

        # Check engagement ratio
        likes = post.get('likes', 0)
        retweets = post.get('retweets', 0)
        if followers > 0:
            engagement_rate = (likes + retweets) / followers
            if engagement_rate > 0.1:
                score += 10
                reasons.append('High engagement')

        # Check for red flags
        text = post.get('text', '').lower()
        for flag in self.red_flags:
            if flag in text:
                score -= 10
                reasons.append(f'Red flag: {flag}')

        # Check for verification patterns
        for pattern in self.verification_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 5
                reasons.append('Contains source/verification')
                break

        # Check for links to official sources
        if 'sec.gov' in text or 'cftc.gov' in text or 'federalreserve.gov' in text:
            score += 20
            reasons.append('Links to official source')

        # Check for media (images/links often indicate more effort)
        if post.get('has_media') or post.get('has_link'):
            score += 5
            reasons.append('Contains media/links')

        # Normalize score
        score = max(0, min(100, score))

        post['credibility_score'] = score
        post['credibility_reasons'] = reasons
        post['credibility_tier'] = self.get_tier(score)

        return post

    def score_reddit_post(self, post: Dict) -> Dict:
        """Score a Reddit post for credibility"""
        score = 50
        reasons = []

        # Check subreddit
        subreddit = post.get('subreddit', '').lower()
        if subreddit in ['wallstreetsilver', 'silverbugs']:
            score += 10
            reasons.append('Relevant subreddit')

        # Check if trusted user
        author = post.get('author', '').lower()
        if author in [u.lower() for u in self.trusted_reddit_users]:
            score += 25
            reasons.append('Trusted DD poster')

        # Check post score (upvotes)
        post_score = post.get('score', 0)
        if post_score > 1000:
            score += 20
            reasons.append('Highly upvoted')
        elif post_score > 100:
            score += 10
            reasons.append('Well received')
        elif post_score < 1:
            score -= 20
            reasons.append('Downvoted')

        # Check comment count (discussion = verification)
        comments = post.get('num_comments', 0)
        if comments > 100:
            score += 10
            reasons.append('Active discussion')
        elif comments > 20:
            score += 5
            reasons.append('Good discussion')

        # Check for flair (DD flair is good)
        flair = post.get('link_flair_text', '').lower()
        if 'dd' in flair or 'due diligence' in flair:
            score += 15
            reasons.append('DD flair')
        elif 'news' in flair:
            score += 10
            reasons.append('News flair')

        # Check for red flags
        text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
        for flag in self.red_flags:
            if flag in text:
                score -= 10
                reasons.append(f'Red flag: {flag}')

        # Check for sources
        if 'source' in text or 'link' in text or 'http' in text:
            score += 10
            reasons.append('Contains sources')

        # Check for verification patterns
        for pattern in self.verification_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 5
                reasons.append('Contains verification')
                break

        # Check account age if available
        account_age_days = post.get('author_account_age_days', 365)
        if account_age_days < self.min_reddit_account_age_days:
            score -= 15
            reasons.append('New account')

        # Normalize
        score = max(0, min(100, score))

        post['credibility_score'] = score
        post['credibility_reasons'] = reasons
        post['credibility_tier'] = self.get_tier(score)

        return post

    def score_news_article(self, article: Dict) -> Dict:
        """Score a news article for credibility"""
        score = 50
        reasons = []

        # Check source
        source = article.get('source', '').lower()
        trusted_news = ['reuters', 'bloomberg', 'wsj', 'ft', 'kitco', 'seeking alpha']
        if any(t in source for t in trusted_news):
            score += 30
            reasons.append('Trusted news source')

        # Check for author
        if article.get('author'):
            score += 5
            reasons.append('Has author attribution')

        # Check for date
        if article.get('published_date'):
            score += 5
            reasons.append('Has publication date')

        # Check content length (longer = more detailed)
        content = article.get('content', '')
        if len(content) > 2000:
            score += 10
            reasons.append('Detailed article')
        elif len(content) < 200:
            score -= 10
            reasons.append('Very short article')

        # Check for quotes
        if '"' in content or "'" in content:
            score += 5
            reasons.append('Contains quotes')

        # Normalize
        score = max(0, min(100, score))

        article['credibility_score'] = score
        article['credibility_reasons'] = reasons
        article['credibility_tier'] = self.get_tier(score)

        return article

    def get_tier(self, score: int) -> str:
        """Convert score to tier"""
        if score >= 80:
            return 'HIGH'
        elif score >= 60:
            return 'MEDIUM'
        elif score >= 40:
            return 'LOW'
        else:
            return 'UNRELIABLE'

    def filter_posts(
        self,
        posts: List[Dict],
        min_score: int = 40,
        platform: str = 'twitter'
    ) -> List[Dict]:
        """Filter posts by credibility score"""
        scored_posts = []

        for post in posts:
            if platform == 'twitter':
                scored = self.score_twitter_post(post)
            elif platform == 'reddit':
                scored = self.score_reddit_post(post)
            elif platform == 'news':
                scored = self.score_news_article(post)
            else:
                scored = post
                scored['credibility_score'] = 50
                scored['credibility_tier'] = 'MEDIUM'

            if scored['credibility_score'] >= min_score:
                scored_posts.append(scored)

        # Sort by credibility
        scored_posts.sort(key=lambda x: x['credibility_score'], reverse=True)

        return scored_posts

    def deduplicate_posts(self, posts: List[Dict]) -> List[Dict]:
        """Remove duplicate posts based on content similarity"""
        seen_content = set()
        unique_posts = []

        for post in posts:
            # Create content hash
            text = post.get('text', post.get('title', ''))[:100].lower()
            text_clean = re.sub(r'[^a-z0-9]', '', text)

            if text_clean not in seen_content:
                seen_content.add(text_clean)
                unique_posts.append(post)

        return unique_posts

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract relevant entities from text"""
        entities = {
            'banks': [],
            'tickers': [],
            'prices': [],
            'regulators': [],
        }

        text_lower = text.lower()

        # Banks
        bank_patterns = {
            'Morgan Stanley': ['morgan stanley', ' ms '],
            'Citigroup': ['citigroup', 'citi '],
            'JPMorgan': ['jpmorgan', 'jp morgan', 'jpm'],
            'HSBC': ['hsbc'],
            'UBS': ['ubs'],
            'Scotiabank': ['scotiabank', 'scotia'],
        }
        for bank, patterns in bank_patterns.items():
            if any(p in text_lower for p in patterns):
                entities['banks'].append(bank)

        # Tickers
        ticker_pattern = r'\$([A-Z]{1,5})\b'
        tickers = re.findall(ticker_pattern, text)
        entities['tickers'] = list(set(tickers))

        # Prices
        price_pattern = r'\$(\d+(?:\.\d{1,2})?)'
        prices = re.findall(price_pattern, text)
        entities['prices'] = [float(p) for p in prices]

        # Regulators
        regulators = ['sec', 'cftc', 'fed', 'fdic', 'occ']
        for reg in regulators:
            if reg in text_lower:
                entities['regulators'].append(reg.upper())

        return entities
