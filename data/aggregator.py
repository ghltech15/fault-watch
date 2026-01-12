"""
Data Aggregator
Combines all data sources into unified dashboard data
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .prices import PriceMonitor
from .fed import FedMonitor
from .comex import ComexMonitor
from .sec_monitor import SECMonitor
from .alerts import AlertManager
from .credibility import CredibilityFilter
from .database import db

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates all data sources for the dashboard"""

    def __init__(self):
        self.price_monitor = PriceMonitor()
        self.fed_monitor = FedMonitor()
        self.comex_monitor = ComexMonitor()
        self.sec_monitor = SECMonitor()
        self.alert_manager = AlertManager()
        self.credibility_filter = CredibilityFilter()

        # Import scrapers (may fail if dependencies not installed)
        try:
            from scrapers.reddit_scraper import RedditScraper
            self.reddit_scraper = RedditScraper()
        except ImportError:
            self.reddit_scraper = None
            logger.warning("Reddit scraper not available")

        try:
            from scrapers.news_scraper import NewsScraper
            self.news_scraper = NewsScraper()
        except ImportError:
            self.news_scraper = None
            logger.warning("News scraper not available")

        try:
            from scrapers.dealer_scraper import DealerScraper
            self.dealer_scraper = DealerScraper()
        except ImportError:
            self.dealer_scraper = None
            logger.warning("Dealer scraper not available")

        try:
            from scrapers.regulatory_scraper import RegulatoryScraper
            self.regulatory_scraper = RegulatoryScraper()
        except ImportError:
            self.regulatory_scraper = None
            logger.warning("Regulatory scraper not available")

        self.executor = ThreadPoolExecutor(max_workers=5)
        self.last_full_refresh = None
        self.cache_ttl = 60  # seconds

    def get_price_data(self) -> Dict:
        """Get all price data"""
        return self.price_monitor.get_summary()

    def get_fed_data(self) -> Dict:
        """Get Federal Reserve data"""
        return self.fed_monitor.get_summary()

    def get_comex_data(self) -> Dict:
        """Get COMEX inventory data"""
        return self.comex_monitor.get_summary()

    def get_sec_data(self) -> Dict:
        """Get SEC filing data"""
        return self.sec_monitor.get_summary()

    def get_alerts(self, limit: int = 20) -> List[Dict]:
        """Get current alerts"""
        return self.alert_manager.get_alerts(limit=limit)

    def get_critical_alerts(self) -> List[Dict]:
        """Get critical and high severity alerts"""
        return self.alert_manager.get_critical_alerts()

    def get_social_data(self) -> Dict:
        """Get social media data"""
        if not self.reddit_scraper:
            return {'error': 'Reddit scraper not available'}
        return self.reddit_scraper.get_summary()

    def get_news_data(self) -> Dict:
        """Get news data"""
        if not self.news_scraper:
            return {'error': 'News scraper not available'}
        return self.news_scraper.get_summary()

    def get_dealer_data(self) -> Dict:
        """Get dealer premium data"""
        if not self.dealer_scraper:
            return {'error': 'Dealer scraper not available'}
        return self.dealer_scraper.get_summary()

    def get_regulatory_data(self) -> Dict:
        """Get regulatory data"""
        if not self.regulatory_scraper:
            return {'error': 'Regulatory scraper not available'}
        return self.regulatory_scraper.get_summary()

    def check_all_alerts(self) -> List[Dict]:
        """Check all data sources for alerts"""
        alerts = []

        # Price alerts
        try:
            alerts.extend(self.price_monitor.check_price_alerts(self.alert_manager))
        except Exception as e:
            logger.error(f"Price alert check failed: {e}")

        # Fed alerts
        try:
            alerts.extend(self.fed_monitor.check_alerts(self.alert_manager))
        except Exception as e:
            logger.error(f"Fed alert check failed: {e}")

        # COMEX alerts
        try:
            alerts.extend(self.comex_monitor.check_alerts(self.alert_manager))
        except Exception as e:
            logger.error(f"COMEX alert check failed: {e}")

        # SEC alerts
        try:
            alerts.extend(self.sec_monitor.check_alerts(self.alert_manager))
        except Exception as e:
            logger.error(f"SEC alert check failed: {e}")

        # Dealer alerts
        if self.dealer_scraper:
            try:
                alerts.extend(self.dealer_scraper.check_alerts(self.alert_manager))
            except Exception as e:
                logger.error(f"Dealer alert check failed: {e}")

        # Regulatory alerts
        if self.regulatory_scraper:
            try:
                alerts.extend(self.regulatory_scraper.check_alerts(self.alert_manager))
            except Exception as e:
                logger.error(f"Regulatory alert check failed: {e}")

        # Persist alerts to database
        for alert in alerts:
            try:
                db.save_alert(alert.to_dict())
            except Exception as e:
                logger.error(f"Failed to save alert: {e}")

        return [a.to_dict() for a in alerts]

    def get_dashboard_summary(self) -> Dict:
        """Get complete dashboard summary"""
        return {
            'prices': self.get_price_data(),
            'fed': self.get_fed_data(),
            'comex': self.get_comex_data(),
            'alerts': {
                'summary': self.alert_manager.get_summary(),
                'recent': self.get_alerts(limit=10),
                'critical': self.get_critical_alerts(),
            },
            'last_updated': datetime.now().isoformat(),
        }

    def get_full_data(self) -> Dict:
        """Get all data from all sources"""
        data = {
            'prices': self.get_price_data(),
            'fed': self.get_fed_data(),
            'comex': self.get_comex_data(),
            'sec': self.get_sec_data(),
            'alerts': self.alert_manager.get_summary(),
            'social': self.get_social_data() if self.reddit_scraper else None,
            'news': self.get_news_data() if self.news_scraper else None,
            'dealers': self.get_dealer_data() if self.dealer_scraper else None,
            'regulatory': self.get_regulatory_data() if self.regulatory_scraper else None,
            'last_updated': datetime.now().isoformat(),
        }

        # Persist metrics snapshot
        try:
            db.save_metrics(data)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

        self.last_full_refresh = datetime.now()
        return data

    def refresh_all(self) -> Dict:
        """Force refresh all data sources"""
        # Clear caches
        self.price_monitor.cache.clear()
        self.fed_monitor.cache.clear()
        self.comex_monitor.cache.clear()
        self.sec_monitor.cache.clear()

        if self.reddit_scraper:
            self.reddit_scraper.cache.clear()
        if self.news_scraper:
            self.news_scraper.cache.clear()
        if self.dealer_scraper:
            self.dealer_scraper.cache.clear()
        if self.regulatory_scraper:
            self.regulatory_scraper.cache.clear()

        # Check for new alerts
        new_alerts = self.check_all_alerts()

        # Get fresh data
        data = self.get_full_data()
        data['new_alerts'] = new_alerts

        return data

    def get_stress_indicators(self) -> Dict:
        """Get aggregated stress indicators"""
        fed_stress = self.fed_monitor.get_stress_indicators()
        comex = self.comex_monitor.get_full_data()
        prices = self.price_monitor.get_summary()

        # Calculate composite stress score
        stress_score = 0
        indicators = []

        # Fed indicators
        if fed_stress.get('ted_spread'):
            ted = fed_stress['ted_spread']
            if ted > 1.0:
                stress_score += 30
                indicators.append(f"TED spread elevated: {ted:.2f}%")
            elif ted > 0.5:
                stress_score += 15
                indicators.append(f"TED spread rising: {ted:.2f}%")

        # COMEX indicators
        if comex.coverage_ratio > 3:
            stress_score += 25
            indicators.append(f"COMEX coverage ratio critical: {comex.coverage_ratio:.1f}x")
        elif comex.coverage_ratio > 2:
            stress_score += 10
            indicators.append(f"COMEX coverage elevated: {comex.coverage_ratio:.1f}x")

        if comex.days_of_supply < 20:
            stress_score += 20
            indicators.append(f"COMEX supply low: {comex.days_of_supply:.0f} days")

        # Silver price volatility
        silver = prices.get('silver', {})
        if silver.get('change_pct'):
            change = abs(silver['change_pct'])
            if change > 5:
                stress_score += 15
                indicators.append(f"Silver volatile: {silver['change_pct']:.1f}%")

        # VIX
        vix = prices.get('vix', {})
        if vix.get('price'):
            if vix['price'] > 30:
                stress_score += 20
                indicators.append(f"VIX elevated: {vix['price']:.1f}")
            elif vix['price'] > 20:
                stress_score += 10
                indicators.append(f"VIX rising: {vix['price']:.1f}")

        # Determine overall status
        if stress_score >= 70:
            status = 'CRITICAL'
        elif stress_score >= 50:
            status = 'HIGH'
        elif stress_score >= 30:
            status = 'ELEVATED'
        elif stress_score >= 15:
            status = 'MODERATE'
        else:
            status = 'NORMAL'

        return {
            'stress_score': min(100, stress_score),
            'status': status,
            'indicators': indicators,
            'fed_stress': fed_stress,
            'comex_status': comex.status,
            'timestamp': datetime.now().isoformat(),
        }

    def get_bank_exposure_summary(self) -> Dict:
        """Get summary of bank precious metals exposure"""
        bank_prices = self.price_monitor.get_bank_prices()

        # Calculate aggregate exposure metrics
        total_dropping = 0
        banks_in_trouble = []

        for asset, price_data in bank_prices.items():
            if price_data and price_data.change_pct < -3:
                total_dropping += 1
                banks_in_trouble.append({
                    'bank': asset,
                    'ticker': price_data.symbol,
                    'price': price_data.price,
                    'change_pct': price_data.change_pct,
                })

        return {
            'bank_count': len(bank_prices),
            'banks_dropping': total_dropping,
            'troubled_banks': banks_in_trouble,
            'timestamp': datetime.now().isoformat(),
        }


# Global aggregator instance
aggregator = DataAggregator()
