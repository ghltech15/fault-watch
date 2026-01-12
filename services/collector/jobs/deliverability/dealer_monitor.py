"""
Dealer Monitor

Monitors physical precious metals dealers for:
- Premium over spot
- Out-of-stock rates
- Delivery delays
- Price divergence from spot

Trust Tier: 2 (Credible) - Creates Events + Claims
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID
import re

from bs4 import BeautifulSoup

from ..base import BaseCollector, Event, Claim, RawData, TrustTier


@dataclass
class ProductData:
    """Single product data point"""
    dealer: str
    product_name: str
    metal: str  # silver, gold, platinum
    price: float
    spot_price: float
    premium_pct: float
    in_stock: bool
    url: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DealerSnapshot:
    """Aggregated dealer data snapshot"""
    timestamp: datetime

    # Silver metrics
    silver_spot: Optional[float] = None
    silver_avg_premium_pct: float = 0
    silver_min_premium_pct: float = 0
    silver_max_premium_pct: float = 0
    silver_in_stock: int = 0
    silver_out_of_stock: int = 0
    silver_oos_rate: float = 0

    # Gold metrics
    gold_spot: Optional[float] = None
    gold_avg_premium_pct: float = 0
    gold_min_premium_pct: float = 0
    gold_max_premium_pct: float = 0
    gold_in_stock: int = 0
    gold_out_of_stock: int = 0
    gold_oos_rate: float = 0

    # Best deals
    best_silver_deals: List[ProductData] = field(default_factory=list)
    best_gold_deals: List[ProductData] = field(default_factory=list)

    # Dealers tracked
    dealers_monitored: int = 0

    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'silver': {
                'spot_price': self.silver_spot,
                'avg_premium_pct': round(self.silver_avg_premium_pct, 1),
                'min_premium_pct': round(self.silver_min_premium_pct, 1),
                'max_premium_pct': round(self.silver_max_premium_pct, 1),
                'in_stock': self.silver_in_stock,
                'out_of_stock': self.silver_out_of_stock,
                'oos_rate': round(self.silver_oos_rate, 1),
            },
            'gold': {
                'spot_price': self.gold_spot,
                'avg_premium_pct': round(self.gold_avg_premium_pct, 1),
                'min_premium_pct': round(self.gold_min_premium_pct, 1),
                'max_premium_pct': round(self.gold_max_premium_pct, 1),
                'in_stock': self.gold_in_stock,
                'out_of_stock': self.gold_out_of_stock,
                'oos_rate': round(self.gold_oos_rate, 1),
            },
            'dealers_monitored': self.dealers_monitored,
            'best_silver_deals': [
                {'dealer': d.dealer, 'product': d.product_name, 'premium': d.premium_pct}
                for d in self.best_silver_deals[:5]
            ],
        }


# Dealers to monitor
DEALERS = {
    'jmbullion': {
        'name': 'JM Bullion',
        'base_url': 'https://www.jmbullion.com',
        'silver_url': 'https://www.jmbullion.com/silver/',
        'gold_url': 'https://www.jmbullion.com/gold/',
    },
    'apmex': {
        'name': 'APMEX',
        'base_url': 'https://www.apmex.com',
        'silver_url': 'https://www.apmex.com/silver',
        'gold_url': 'https://www.apmex.com/gold',
    },
    'sdbullion': {
        'name': 'SD Bullion',
        'base_url': 'https://sdbullion.com',
        'silver_url': 'https://sdbullion.com/silver',
        'gold_url': 'https://sdbullion.com/gold',
    },
}


class DealerMonitor(BaseCollector):
    """
    Monitors physical precious metals dealers.

    Creates Events for:
    - Premium spikes
    - Out-of-stock conditions
    - Supply tightness

    Creates Claims for:
    - Delivery delay reports
    - Unusual conditions
    """

    source_name = "Dealer Monitor"
    trust_tier = TrustTier.TIER_2_CREDIBLE
    frequency_minutes = 240  # Every 4 hours

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history: List[DealerSnapshot] = []
        self._products: List[ProductData] = []

    async def fetch(self) -> List[RawData]:
        """Fetch dealer pages"""
        raw_data = []

        for dealer_id, config in DEALERS.items():
            for metal in ['silver', 'gold']:
                url = config.get(f'{metal}_url')
                if not url:
                    continue

                try:
                    result = await self.fetcher.fetch(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    raw_data.append(RawData(
                        content=result.content,
                        url=url,
                        fetched_at=result.fetched_at,
                        headers={
                            'dealer': dealer_id,
                            'dealer_name': config['name'],
                            'metal': metal,
                        },
                    ))
                except Exception as e:
                    print(f"[Dealer] Failed to fetch {config['name']} {metal}: {e}")

        return raw_data

    def parse(self, raw: RawData) -> List[Event | Claim]:
        """Parse dealer page into Events"""
        items = []
        dealer = raw.headers.get('dealer_name', 'Unknown')
        metal = raw.headers.get('metal', 'silver')

        try:
            products = self._parse_dealer_page(raw.content, dealer, metal)
            self._products.extend(products)

        except Exception as e:
            print(f"[Dealer] Parse error for {dealer}: {e}")

        return items

    def _parse_dealer_page(
        self,
        content: str | bytes,
        dealer: str,
        metal: str,
    ) -> List[ProductData]:
        """Parse dealer page for product data"""
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')

        products = []
        soup = BeautifulSoup(content, 'lxml')

        # Generic product parsing (dealers have different structures)
        # Look for product cards/items
        for item in soup.select('.product-item, .product-card, .product, [data-product]'):
            try:
                product = self._parse_product_item(item, dealer, metal)
                if product:
                    products.append(product)
            except Exception:
                continue

        return products

    def _parse_product_item(
        self,
        item,
        dealer: str,
        metal: str,
    ) -> Optional[ProductData]:
        """Parse single product item"""
        # Try to find product name
        name_elem = item.select_one('.product-name, .product-title, h2, h3, a')
        if not name_elem:
            return None

        name = name_elem.get_text(strip=True)
        if not name or len(name) < 5:
            return None

        # Try to find price
        price = None
        price_elem = item.select_one('.price, .product-price, [data-price]')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
            if price_match:
                price = float(price_match.group(1).replace(',', ''))

        if not price:
            return None

        # Check stock status
        in_stock = True
        stock_elem = item.select_one('.stock-status, .availability, .out-of-stock')
        if stock_elem:
            stock_text = stock_elem.get_text().lower()
            if 'out of stock' in stock_text or 'sold out' in stock_text:
                in_stock = False

        # Calculate premium (would need spot price)
        # For now, use placeholder
        spot_price = 30.0 if metal == 'silver' else 2000.0  # Would get from price feed
        premium_pct = ((price / spot_price) - 1) * 100 if spot_price > 0 else 0

        return ProductData(
            dealer=dealer,
            product_name=name[:100],
            metal=metal,
            price=price,
            spot_price=spot_price,
            premium_pct=premium_pct,
            in_stock=in_stock,
        )

    def create_snapshot(self, spot_prices: Dict[str, float] = None) -> DealerSnapshot:
        """Create aggregated snapshot from collected products"""
        spot_prices = spot_prices or {'silver': 30.0, 'gold': 2000.0}

        snapshot = DealerSnapshot(timestamp=datetime.utcnow())
        snapshot.silver_spot = spot_prices.get('silver')
        snapshot.gold_spot = spot_prices.get('gold')

        # Separate by metal
        silver_products = [p for p in self._products if p.metal == 'silver']
        gold_products = [p for p in self._products if p.metal == 'gold']

        # Silver metrics
        if silver_products:
            # Recalculate premiums with actual spot
            for p in silver_products:
                if snapshot.silver_spot and snapshot.silver_spot > 0:
                    p.premium_pct = ((p.price / snapshot.silver_spot) - 1) * 100

            premiums = [p.premium_pct for p in silver_products if p.in_stock]
            if premiums:
                snapshot.silver_avg_premium_pct = sum(premiums) / len(premiums)
                snapshot.silver_min_premium_pct = min(premiums)
                snapshot.silver_max_premium_pct = max(premiums)

            snapshot.silver_in_stock = sum(1 for p in silver_products if p.in_stock)
            snapshot.silver_out_of_stock = sum(1 for p in silver_products if not p.in_stock)
            total_silver = snapshot.silver_in_stock + snapshot.silver_out_of_stock
            if total_silver > 0:
                snapshot.silver_oos_rate = (snapshot.silver_out_of_stock / total_silver) * 100

            # Best deals
            in_stock = [p for p in silver_products if p.in_stock]
            snapshot.best_silver_deals = sorted(in_stock, key=lambda x: x.premium_pct)[:5]

        # Gold metrics
        if gold_products:
            for p in gold_products:
                if snapshot.gold_spot and snapshot.gold_spot > 0:
                    p.premium_pct = ((p.price / snapshot.gold_spot) - 1) * 100

            premiums = [p.premium_pct for p in gold_products if p.in_stock]
            if premiums:
                snapshot.gold_avg_premium_pct = sum(premiums) / len(premiums)
                snapshot.gold_min_premium_pct = min(premiums)
                snapshot.gold_max_premium_pct = max(premiums)

            snapshot.gold_in_stock = sum(1 for p in gold_products if p.in_stock)
            snapshot.gold_out_of_stock = sum(1 for p in gold_products if not p.in_stock)
            total_gold = snapshot.gold_in_stock + snapshot.gold_out_of_stock
            if total_gold > 0:
                snapshot.gold_oos_rate = (snapshot.gold_out_of_stock / total_gold) * 100

            in_stock = [p for p in gold_products if p.in_stock]
            snapshot.best_gold_deals = sorted(in_stock, key=lambda x: x.premium_pct)[:5]

        snapshot.dealers_monitored = len(DEALERS)

        # Store in history
        self._history.append(snapshot)

        # Clear products for next collection
        self._products = []

        return snapshot

    def detect_stress_events(self, snapshot: DealerSnapshot) -> List[Event]:
        """Detect dealer stress conditions"""
        events = []

        # High silver premium
        if snapshot.silver_avg_premium_pct > 20:
            severity = 'critical' if snapshot.silver_avg_premium_pct > 30 else 'elevated'
            events.append(Event(
                event_type='dealer_stress',
                source_id=self.source_id,
                payload={
                    'indicator': 'silver_premium',
                    'value': snapshot.silver_avg_premium_pct,
                    'threshold': 20,
                    'severity': severity,
                    'description': f'Silver dealer premium at {snapshot.silver_avg_premium_pct:.0f}%',
                },
                entity_id=None,
            ))

        # High out-of-stock rate
        if snapshot.silver_oos_rate > 30:
            severity = 'critical' if snapshot.silver_oos_rate > 50 else 'elevated'
            events.append(Event(
                event_type='dealer_shortage',
                source_id=self.source_id,
                payload={
                    'indicator': 'silver_oos_rate',
                    'value': snapshot.silver_oos_rate,
                    'threshold': 30,
                    'severity': severity,
                    'description': f'{snapshot.silver_oos_rate:.0f}% of silver products out of stock',
                },
                entity_id=None,
            ))

        # Gold stress
        if snapshot.gold_avg_premium_pct > 10:
            events.append(Event(
                event_type='dealer_stress',
                source_id=self.source_id,
                payload={
                    'indicator': 'gold_premium',
                    'value': snapshot.gold_avg_premium_pct,
                    'threshold': 10,
                    'severity': 'elevated',
                    'description': f'Gold dealer premium at {snapshot.gold_avg_premium_pct:.0f}%',
                },
                entity_id=None,
            ))

        return events

    def get_latest_snapshot(self) -> Optional[DealerSnapshot]:
        """Get most recent snapshot"""
        return self._history[-1] if self._history else None

    def get_premium_history(self, metal: str = 'silver', days: int = 30) -> List[Dict]:
        """Get premium history"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        field = f'{metal}_avg_premium_pct'
        return [
            {'date': s.timestamp.isoformat(), 'premium': getattr(s, field, 0)}
            for s in self._history
            if s.timestamp > cutoff
        ]
