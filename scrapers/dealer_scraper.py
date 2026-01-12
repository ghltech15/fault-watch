"""
Dealer Scraper
Monitors physical precious metals dealer premiums and availability
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class DealerProduct:
    dealer: str
    product_name: str
    product_type: str  # coin, bar, round
    metal: str  # silver, gold
    weight_oz: float
    price: float
    premium_pct: float
    premium_per_oz: float
    in_stock: bool
    url: str
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            'dealer': self.dealer,
            'product_name': self.product_name,
            'product_type': self.product_type,
            'metal': self.metal,
            'weight_oz': self.weight_oz,
            'price': self.price,
            'premium_pct': self.premium_pct,
            'premium_per_oz': self.premium_per_oz,
            'in_stock': self.in_stock,
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
        }


class DealerScraper:
    """Scrape physical precious metals dealers for prices and availability"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        # Dealer product URLs
        self.dealers = {
            'jmbullion': {
                'base_url': 'https://www.jmbullion.com',
                'silver_page': '/silver/',
                'gold_page': '/gold/',
            },
            'apmex': {
                'base_url': 'https://www.apmex.com',
                'silver_page': '/silver',
                'gold_page': '/gold',
            },
            'sdbullion': {
                'base_url': 'https://sdbullion.com',
                'silver_page': '/silver',
                'gold_page': '/gold',
            },
            'provident': {
                'base_url': 'https://www.providentmetals.com',
                'silver_page': '/silver/',
                'gold_page': '/gold/',
            },
            'moneymetals': {
                'base_url': 'https://www.moneymetals.com',
                'silver_page': '/silver',
                'gold_page': '/gold',
            },
        }

        # Reference products for premium tracking
        self.reference_products = {
            'silver': [
                {'name': 'American Silver Eagle', 'weight_oz': 1},
                {'name': 'Canadian Silver Maple Leaf', 'weight_oz': 1},
                {'name': 'Silver Round', 'weight_oz': 1},
                {'name': '10 oz Silver Bar', 'weight_oz': 10},
                {'name': '100 oz Silver Bar', 'weight_oz': 100},
            ],
            'gold': [
                {'name': 'American Gold Eagle', 'weight_oz': 1},
                {'name': 'Canadian Gold Maple Leaf', 'weight_oz': 1},
                {'name': '1 oz Gold Bar', 'weight_oz': 1},
            ],
        }

        self.cache: Dict[str, any] = {}
        self.cache_ttl = 1800  # 30 minutes
        self.last_fetch: Dict[str, datetime] = {}

        # Historical premium data
        self.premium_history: List[Dict] = []

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch webpage content"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        # Match various price formats: $29.99, $1,234.56, etc.
        match = re.search(r'\$[\d,]+\.?\d*', text)
        if match:
            price_str = match.group().replace('$', '').replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                pass
        return None

    def get_spot_price(self, metal: str = 'silver') -> Optional[float]:
        """Get current spot price (from cache or API)"""
        # This would typically call a spot price API
        # Using placeholder - integrate with prices.py in production
        cache_key = f'spot_{metal}'
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Fallback spot prices (update from API in production)
        spots = {
            'silver': 30.00,
            'gold': 2800.00,
        }
        return spots.get(metal)

    def scrape_jmbullion(self, metal: str = 'silver') -> List[DealerProduct]:
        """Scrape JM Bullion prices"""
        dealer_info = self.dealers['jmbullion']
        page = 'silver_page' if metal == 'silver' else 'gold_page'
        url = f"{dealer_info['base_url']}{dealer_info[page]}"

        html = self._fetch_page(url)
        if not html:
            return []

        products = []
        spot_price = self.get_spot_price(metal)

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Find product listings (structure varies by dealer)
            for item in soup.find_all('div', class_='product-item'):
                name_elem = item.find('a', class_='product-name')
                price_elem = item.find('span', class_='price')

                if name_elem and price_elem:
                    name = name_elem.get_text(strip=True)
                    price = self._extract_price(price_elem.get_text())

                    if price and spot_price:
                        # Estimate weight from product name
                        weight = self._estimate_weight(name)
                        premium_pct = ((price / (spot_price * weight)) - 1) * 100
                        premium_per_oz = (price / weight) - spot_price

                        product = DealerProduct(
                            dealer='jmbullion',
                            product_name=name,
                            product_type=self._get_product_type(name),
                            metal=metal,
                            weight_oz=weight,
                            price=price,
                            premium_pct=premium_pct,
                            premium_per_oz=premium_per_oz,
                            in_stock='out of stock' not in item.get_text().lower(),
                            url=name_elem.get('href', url),
                            timestamp=datetime.now(),
                        )
                        products.append(product)

        except Exception as e:
            logger.error(f"Error parsing JM Bullion: {e}")

        return products

    def _estimate_weight(self, product_name: str) -> float:
        """Estimate product weight from name"""
        name_lower = product_name.lower()

        # Check for explicit weights
        weight_patterns = [
            (r'(\d+)\s*oz', lambda m: float(m.group(1))),
            (r'(\d+)\s*ounce', lambda m: float(m.group(1))),
            (r'1/2\s*oz', lambda m: 0.5),
            (r'1/4\s*oz', lambda m: 0.25),
            (r'1/10\s*oz', lambda m: 0.1),
            (r'kilo', lambda m: 32.15),
        ]

        for pattern, extractor in weight_patterns:
            match = re.search(pattern, name_lower)
            if match:
                return extractor(match)

        # Default to 1 oz for coins
        return 1.0

    def _get_product_type(self, product_name: str) -> str:
        """Determine product type from name"""
        name_lower = product_name.lower()

        if 'bar' in name_lower:
            return 'bar'
        elif 'round' in name_lower:
            return 'round'
        elif any(coin in name_lower for coin in ['eagle', 'maple', 'britannia', 'philharmonic', 'libertad']):
            return 'coin'
        else:
            return 'other'

    def get_all_dealer_products(self, metal: str = 'silver') -> List[DealerProduct]:
        """Get products from all dealers"""
        cache_key = f'all_products_{metal}'

        if cache_key in self.cache:
            elapsed = (datetime.now() - self.last_fetch.get(cache_key, datetime.min)).total_seconds()
            if elapsed < self.cache_ttl:
                return self.cache[cache_key]

        all_products = []

        # JM Bullion
        all_products.extend(self.scrape_jmbullion(metal))

        # Add other dealers here
        # all_products.extend(self.scrape_apmex(metal))
        # all_products.extend(self.scrape_sdbullion(metal))

        self.cache[cache_key] = all_products
        self.last_fetch[cache_key] = datetime.now()

        return all_products

    def get_premium_summary(self, metal: str = 'silver') -> Dict:
        """Get summary of current premiums"""
        products = self.get_all_dealer_products(metal)
        spot_price = self.get_spot_price(metal)

        if not products:
            return {
                'spot_price': spot_price,
                'avg_premium_pct': 0,
                'min_premium_pct': 0,
                'max_premium_pct': 0,
                'products_in_stock': 0,
                'products_out_of_stock': 0,
            }

        premiums = [p.premium_pct for p in products if p.in_stock]

        return {
            'spot_price': spot_price,
            'avg_premium_pct': sum(premiums) / len(premiums) if premiums else 0,
            'min_premium_pct': min(premiums) if premiums else 0,
            'max_premium_pct': max(premiums) if premiums else 0,
            'products_in_stock': sum(1 for p in products if p.in_stock),
            'products_out_of_stock': sum(1 for p in products if not p.in_stock),
            'out_of_stock_rate': (sum(1 for p in products if not p.in_stock) / len(products)) * 100 if products else 0,
        }

    def get_best_deals(self, metal: str = 'silver', limit: int = 10) -> List[DealerProduct]:
        """Get products with lowest premiums"""
        products = self.get_all_dealer_products(metal)
        in_stock = [p for p in products if p.in_stock]
        in_stock.sort(key=lambda x: x.premium_pct)
        return in_stock[:limit]

    def get_availability_report(self) -> Dict:
        """Get overall availability report"""
        silver_products = self.get_all_dealer_products('silver')
        gold_products = self.get_all_dealer_products('gold')

        def calc_availability(products):
            if not products:
                return {'in_stock': 0, 'out_of_stock': 0, 'rate': 0}
            in_stock = sum(1 for p in products if p.in_stock)
            out_of_stock = len(products) - in_stock
            return {
                'in_stock': in_stock,
                'out_of_stock': out_of_stock,
                'availability_rate': (in_stock / len(products)) * 100,
            }

        return {
            'silver': calc_availability(silver_products),
            'gold': calc_availability(gold_products),
            'timestamp': datetime.now().isoformat(),
        }

    def track_premium_history(self):
        """Record current premiums for historical tracking"""
        silver_summary = self.get_premium_summary('silver')
        gold_summary = self.get_premium_summary('gold')

        record = {
            'timestamp': datetime.now().isoformat(),
            'silver_premium_avg': silver_summary['avg_premium_pct'],
            'gold_premium_avg': gold_summary['avg_premium_pct'],
            'silver_availability': silver_summary['products_in_stock'],
            'gold_availability': gold_summary['products_in_stock'],
        }

        self.premium_history.append(record)

        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        self.premium_history = [
            r for r in self.premium_history
            if datetime.fromisoformat(r['timestamp']) > cutoff
        ]

    def check_alerts(self, alert_manager) -> List:
        """Check dealer data against alert thresholds"""
        alerts = []
        silver_summary = self.get_premium_summary('silver')

        # Check for premium spikes
        if silver_summary['avg_premium_pct'] > 25:
            from data.alerts import Alert, AlertSeverity, AlertType
            alert = Alert(
                severity=AlertSeverity.HIGH,
                alert_type=AlertType.PREMIUM_SPIKE,
                title=f"SILVER PREMIUM SPIKE: {silver_summary['avg_premium_pct']:.1f}%",
                description=f"Average dealer premium at {silver_summary['avg_premium_pct']:.1f}%",
                source='Dealer Monitor',
                data=silver_summary,
            )
            if alert_manager.add_alert(alert):
                alerts.append(alert)

        # Check for low availability
        if silver_summary['out_of_stock_rate'] > 50:
            from data.alerts import Alert, AlertSeverity, AlertType
            alert = Alert(
                severity=AlertSeverity.MEDIUM,
                alert_type=AlertType.INVENTORY_DROP,
                title="SILVER AVAILABILITY LOW",
                description=f"{silver_summary['out_of_stock_rate']:.0f}% of products out of stock",
                source='Dealer Monitor',
                data=silver_summary,
            )
            if alert_manager.add_alert(alert):
                alerts.append(alert)

        return alerts

    def get_summary(self) -> Dict:
        """Get dealer monitoring summary"""
        silver_summary = self.get_premium_summary('silver')
        gold_summary = self.get_premium_summary('gold')
        availability = self.get_availability_report()

        return {
            'silver': silver_summary,
            'gold': gold_summary,
            'availability': availability,
            'best_silver_deals': [p.to_dict() for p in self.get_best_deals('silver', 5)],
            'dealers_monitored': len(self.dealers),
            'last_updated': datetime.now().isoformat(),
        }
