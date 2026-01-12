"""
News Scraper
Monitors news RSS feeds and financial news sources
"""

import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import re
import xml.etree.ElementTree as ET
from html import unescape

logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    title: str
    description: str
    url: str
    source: str
    author: Optional[str]
    published_date: datetime
    categories: List[str]
    content: str

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'source': self.source,
            'author': self.author,
            'published_date': self.published_date.isoformat(),
            'categories': self.categories,
            'content': self.content[:500] if self.content else '',
        }


class NewsScraper:
    """Scrape news from RSS feeds and other sources"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'FaultWatch/1.0 News Aggregator',
        }

        # RSS feeds to monitor
        self.rss_feeds = {
            'reuters_finance': 'https://feeds.reuters.com/reuters/businessNews',
            'reuters_markets': 'https://feeds.reuters.com/reuters/marketsNews',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'wsj_markets': 'https://feeds.wsj.com/xml/rss/3_7031.xml',
            'ft_markets': 'https://www.ft.com/markets?format=rss',
            'seeking_alpha': 'https://seekingalpha.com/market_currents.xml',
            'kitco': 'https://www.kitco.com/rss/rss.xml',
            'zerohedge': 'https://feeds.feedburner.com/zerohedge/feed',
        }

        # Keywords for filtering relevant news
        self.filter_keywords = [
            'silver', 'gold', 'precious metal',
            'morgan stanley', 'citigroup', 'hsbc', 'ubs', 'jpmorgan',
            'bank', 'federal reserve', 'fed', 'repo',
            'comex', 'lbma', 'futures', 'derivative',
            'short', 'squeeze', 'manipulation',
            'sec', 'enforcement', 'investigation',
            'crisis', 'collapse', 'bailout', 'nationalization',
        ]

        self.cache: Dict[str, List] = {}
        self.cache_ttl = 600  # 10 minutes
        self.last_fetch: Dict[str, datetime] = {}

    def _parse_rss(self, url: str) -> List[Dict]:
        """Parse RSS feed"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            items = []
            # Handle both RSS 2.0 and Atom formats
            for item in root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                article = {}

                # RSS 2.0 format
                title = item.find('title')
                if title is not None:
                    article['title'] = unescape(title.text or '')

                link = item.find('link')
                if link is not None:
                    article['url'] = link.text or ''

                desc = item.find('description')
                if desc is not None:
                    # Strip HTML tags
                    article['description'] = re.sub(r'<[^>]+>', '', unescape(desc.text or ''))

                pubdate = item.find('pubDate')
                if pubdate is not None:
                    article['published'] = pubdate.text

                author = item.find('author') or item.find('{http://purl.org/dc/elements/1.1/}creator')
                if author is not None:
                    article['author'] = author.text

                categories = item.findall('category')
                article['categories'] = [c.text for c in categories if c.text]

                content = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
                if content is not None:
                    article['content'] = re.sub(r'<[^>]+>', '', unescape(content.text or ''))
                else:
                    article['content'] = article.get('description', '')

                if article.get('title') and article.get('url'):
                    items.append(article)

            return items

        except Exception as e:
            logger.error(f"Error parsing RSS {url}: {e}")
            return []

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return datetime.now()

    def get_feed_articles(self, feed_name: str) -> List[NewsArticle]:
        """Get articles from a specific feed"""
        if feed_name not in self.rss_feeds:
            return []

        cache_key = feed_name
        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        url = self.rss_feeds[feed_name]
        raw_articles = self._parse_rss(url)

        articles = []
        for raw in raw_articles:
            article = NewsArticle(
                title=raw.get('title', ''),
                description=raw.get('description', ''),
                url=raw.get('url', ''),
                source=feed_name,
                author=raw.get('author'),
                published_date=self._parse_date(raw.get('published', '')),
                categories=raw.get('categories', []),
                content=raw.get('content', ''),
            )
            articles.append(article)

        self.cache[cache_key] = articles
        self.last_fetch[cache_key] = datetime.now()

        return articles

    def get_all_articles(self) -> List[NewsArticle]:
        """Get articles from all feeds"""
        all_articles = []

        for feed_name in self.rss_feeds:
            articles = self.get_feed_articles(feed_name)
            all_articles.extend(articles)

        # Sort by date (newest first)
        all_articles.sort(key=lambda x: x.published_date, reverse=True)
        return all_articles

    def filter_relevant_articles(
        self,
        articles: List[NewsArticle],
        keywords: List[str] = None
    ) -> List[NewsArticle]:
        """Filter articles by relevance keywords"""
        if keywords is None:
            keywords = self.filter_keywords

        relevant = []
        for article in articles:
            text = f"{article.title} {article.description} {article.content}".lower()
            if any(kw in text for kw in keywords):
                article_dict = article.to_dict()
                article_dict['matched_keywords'] = [kw for kw in keywords if kw in text]
                relevant.append(article)

        return relevant

    def get_silver_gold_news(self) -> List[NewsArticle]:
        """Get precious metals specific news"""
        all_articles = self.get_all_articles()
        pm_keywords = ['silver', 'gold', 'precious metal', 'comex', 'lbma', 'bullion']
        return self.filter_relevant_articles(all_articles, pm_keywords)

    def get_bank_news(self) -> List[NewsArticle]:
        """Get bank-related news"""
        all_articles = self.get_all_articles()
        bank_keywords = [
            'morgan stanley', 'citigroup', 'citi', 'hsbc', 'ubs', 'jpmorgan',
            'goldman sachs', 'deutsche bank', 'bank of america', 'scotiabank',
            'bank crisis', 'bank collapse', 'bank bailout', 'bank failure'
        ]
        return self.filter_relevant_articles(all_articles, bank_keywords)

    def get_regulatory_news(self) -> List[NewsArticle]:
        """Get regulatory/enforcement news"""
        all_articles = self.get_all_articles()
        reg_keywords = [
            'sec', 'cftc', 'enforcement', 'investigation', 'fine', 'penalty',
            'settlement', 'consent order', 'wells notice', 'subpoena',
            'manipulation', 'fraud', 'spoofing'
        ]
        return self.filter_relevant_articles(all_articles, reg_keywords)

    def get_crisis_indicators(self) -> List[NewsArticle]:
        """Get articles indicating potential crisis"""
        all_articles = self.get_all_articles()
        crisis_keywords = [
            'crisis', 'collapse', 'crash', 'panic', 'run on bank',
            'liquidity', 'bailout', 'nationalization', 'intervention',
            'emergency', 'contagion', 'systemic'
        ]
        return self.filter_relevant_articles(all_articles, crisis_keywords)

    def search_articles(self, query: str) -> List[NewsArticle]:
        """Search all articles for a query"""
        all_articles = self.get_all_articles()
        query_lower = query.lower()

        matching = []
        for article in all_articles:
            text = f"{article.title} {article.description} {article.content}".lower()
            if query_lower in text:
                matching.append(article)

        return matching

    def get_breaking_news(self, hours: int = 6) -> List[NewsArticle]:
        """Get recent breaking news"""
        all_articles = self.get_all_articles()
        cutoff = datetime.now() - timedelta(hours=hours)

        recent = [a for a in all_articles if a.published_date > cutoff]
        relevant = self.filter_relevant_articles(recent)

        return relevant

    def analyze_coverage(self) -> Dict:
        """Analyze news coverage patterns"""
        all_articles = self.get_all_articles()
        relevant = self.filter_relevant_articles(all_articles)

        # Count by source
        by_source = {}
        for article in relevant:
            source = article.source
            by_source[source] = by_source.get(source, 0) + 1

        # Count by keyword
        keyword_counts = {}
        for kw in self.filter_keywords:
            count = sum(1 for a in all_articles
                       if kw in f"{a.title} {a.description}".lower())
            if count > 0:
                keyword_counts[kw] = count

        return {
            'total_articles': len(all_articles),
            'relevant_articles': len(relevant),
            'by_source': by_source,
            'keyword_frequency': keyword_counts,
        }

    def get_summary(self) -> Dict:
        """Get news monitoring summary"""
        relevant = self.filter_relevant_articles(self.get_all_articles())
        silver_gold = self.get_silver_gold_news()
        banks = self.get_bank_news()
        crisis = self.get_crisis_indicators()
        breaking = self.get_breaking_news(hours=6)

        return {
            'total_relevant': len(relevant),
            'precious_metals_news': len(silver_gold),
            'bank_news': len(banks),
            'crisis_indicators': len(crisis),
            'breaking_news': len(breaking),
            'top_stories': [a.to_dict() for a in relevant[:10]],
            'coverage_analysis': self.analyze_coverage(),
            'last_updated': datetime.now().isoformat(),
        }
