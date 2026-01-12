"""
Database Integration
Supabase persistence for alerts, metrics, and historical data
"""

import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')


class DatabaseClient:
    """Supabase database client for FaultWatch"""

    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.client = None

        if self.url and self.key:
            try:
                from supabase import create_client
                self.client = create_client(self.url, self.key)
                logger.info("Supabase client initialized")
            except ImportError:
                logger.warning("Supabase library not installed. Install with: pip install supabase")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase: {e}")

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None

    # ============ ALERTS ============

    def save_alert(self, alert_data: Dict) -> Optional[str]:
        """Save alert to database"""
        if not self.client:
            return None

        try:
            result = self.client.table('alerts').insert(alert_data).execute()
            if result.data:
                return result.data[0].get('id')
        except Exception as e:
            logger.error(f"Error saving alert: {e}")
        return None

    def get_alerts(
        self,
        severity: str = None,
        alert_type: str = None,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict]:
        """Get alerts from database"""
        if not self.client:
            return []

        try:
            query = self.client.table('alerts').select('*')

            if severity:
                query = query.eq('severity', severity)
            if alert_type:
                query = query.eq('alert_type', alert_type)

            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            query = query.gte('created_at', cutoff)
            query = query.order('created_at', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    def mark_alert_acknowledged(self, alert_id: str) -> bool:
        """Mark alert as acknowledged"""
        if not self.client:
            return False

        try:
            self.client.table('alerts').update(
                {'acknowledged': True, 'acknowledged_at': datetime.now().isoformat()}
            ).eq('id', alert_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False

    # ============ METRICS ============

    def save_metrics(self, metrics_data: Dict) -> bool:
        """Save current metrics snapshot"""
        if not self.client:
            return False

        try:
            data = {
                **metrics_data,
                'timestamp': datetime.now().isoformat(),
            }
            self.client.table('metrics_history').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
            return False

    def get_metrics_history(
        self,
        metric_type: str = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict]:
        """Get historical metrics"""
        if not self.client:
            return []

        try:
            query = self.client.table('metrics_history').select('*')

            if metric_type:
                query = query.eq('metric_type', metric_type)

            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            query = query.gte('timestamp', cutoff)
            query = query.order('timestamp', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
            return []

    # ============ PRICES ============

    def save_price(self, symbol: str, price_data: Dict) -> bool:
        """Save price data point"""
        if not self.client:
            return False

        try:
            data = {
                'symbol': symbol,
                **price_data,
                'timestamp': datetime.now().isoformat(),
            }
            self.client.table('price_history').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving price: {e}")
            return False

    def get_price_history(
        self,
        symbol: str,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict]:
        """Get price history for a symbol"""
        if not self.client:
            return []

        try:
            query = self.client.table('price_history').select('*')
            query = query.eq('symbol', symbol)

            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            query = query.gte('timestamp', cutoff)
            query = query.order('timestamp', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching prices: {e}")
            return []

    # ============ SEC FILINGS ============

    def save_sec_filing(self, filing_data: Dict) -> Optional[str]:
        """Save SEC filing record"""
        if not self.client:
            return None

        try:
            result = self.client.table('sec_filings').insert(filing_data).execute()
            if result.data:
                return result.data[0].get('id')
        except Exception as e:
            logger.error(f"Error saving SEC filing: {e}")
        return None

    def get_sec_filings(
        self,
        company: str = None,
        form_type: str = None,
        days: int = 30,
        limit: int = 50
    ) -> List[Dict]:
        """Get SEC filings from database"""
        if not self.client:
            return []

        try:
            query = self.client.table('sec_filings').select('*')

            if company:
                query = query.eq('company', company)
            if form_type:
                query = query.eq('form_type', form_type)

            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query = query.gte('filed_date', cutoff)
            query = query.order('filed_date', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching SEC filings: {e}")
            return []

    # ============ SOCIAL POSTS ============

    def save_social_post(self, post_data: Dict) -> Optional[str]:
        """Save social media post"""
        if not self.client:
            return None

        try:
            result = self.client.table('social_posts').insert(post_data).execute()
            if result.data:
                return result.data[0].get('id')
        except Exception as e:
            logger.error(f"Error saving social post: {e}")
        return None

    def get_trending_posts(
        self,
        platform: str = None,
        min_score: int = 100,
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict]:
        """Get trending social posts"""
        if not self.client:
            return []

        try:
            query = self.client.table('social_posts').select('*')

            if platform:
                query = query.eq('platform', platform)

            query = query.gte('score', min_score)

            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            query = query.gte('created_at', cutoff)
            query = query.order('score', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return []

    # ============ COMEX DATA ============

    def save_comex_data(self, comex_data: Dict) -> bool:
        """Save COMEX inventory snapshot"""
        if not self.client:
            return False

        try:
            data = {
                **comex_data,
                'timestamp': datetime.now().isoformat(),
            }
            self.client.table('comex_history').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving COMEX data: {e}")
            return False

    def get_comex_history(
        self,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """Get COMEX historical data"""
        if not self.client:
            return []

        try:
            query = self.client.table('comex_history').select('*')

            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query = query.gte('timestamp', cutoff)
            query = query.order('timestamp', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching COMEX data: {e}")
            return []

    # ============ NEWS ============

    def save_news_article(self, article_data: Dict) -> Optional[str]:
        """Save news article"""
        if not self.client:
            return None

        try:
            result = self.client.table('news_articles').insert(article_data).execute()
            if result.data:
                return result.data[0].get('id')
        except Exception as e:
            logger.error(f"Error saving article: {e}")
        return None

    def get_news_articles(
        self,
        source: str = None,
        keywords: List[str] = None,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict]:
        """Get news articles"""
        if not self.client:
            return []

        try:
            query = self.client.table('news_articles').select('*')

            if source:
                query = query.eq('source', source)

            cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
            query = query.gte('published_at', cutoff)
            query = query.order('published_at', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return []

    # ============ DEALER DATA ============

    def save_dealer_premium(self, premium_data: Dict) -> bool:
        """Save dealer premium snapshot"""
        if not self.client:
            return False

        try:
            data = {
                **premium_data,
                'timestamp': datetime.now().isoformat(),
            }
            self.client.table('dealer_premiums').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Error saving premium data: {e}")
            return False

    def get_premium_history(
        self,
        metal: str = 'silver',
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """Get dealer premium history"""
        if not self.client:
            return []

        try:
            query = self.client.table('dealer_premiums').select('*')
            query = query.eq('metal', metal)

            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query = query.gte('timestamp', cutoff)
            query = query.order('timestamp', desc=True)
            query = query.limit(limit)

            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching premiums: {e}")
            return []

    # ============ UTILITY ============

    def cleanup_old_data(self, days: int = 90) -> Dict:
        """Clean up old data from all tables"""
        if not self.client:
            return {'success': False, 'message': 'Database not connected'}

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        tables = [
            'alerts', 'metrics_history', 'price_history',
            'social_posts', 'news_articles', 'dealer_premiums'
        ]

        results = {}
        for table in tables:
            try:
                self.client.table(table).delete().lt('created_at', cutoff).execute()
                results[table] = 'cleaned'
            except Exception as e:
                results[table] = f'error: {e}'

        return {'success': True, 'results': results}

    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        if not self.client:
            return {'connected': False}

        stats = {'connected': True, 'tables': {}}
        tables = [
            'alerts', 'metrics_history', 'price_history', 'sec_filings',
            'social_posts', 'comex_history', 'news_articles', 'dealer_premiums'
        ]

        for table in tables:
            try:
                result = self.client.table(table).select('*', count='exact').limit(1).execute()
                stats['tables'][table] = result.count or 0
            except Exception:
                stats['tables'][table] = 'error'

        return stats


# Global database instance
db = DatabaseClient()
