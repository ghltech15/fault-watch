"""
Price Monitor
Fetches and tracks prices for silver, gold, bank stocks, and other assets
"""

import os
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')


@dataclass
class PriceData:
    symbol: str
    price: float
    change: float
    change_pct: float
    prev_close: float
    high: float
    low: float
    volume: int
    timestamp: datetime

    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'price': self.price,
            'change': self.change,
            'change_pct': self.change_pct,
            'prev_close': self.prev_close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'timestamp': self.timestamp.isoformat(),
        }


class PriceMonitor:
    """Monitor prices for various assets"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or FINNHUB_API_KEY
        self.base_url = 'https://finnhub.io/api/v1'
        self.cache: Dict[str, PriceData] = {}
        self.cache_ttl = 60  # seconds
        self.last_fetch: Dict[str, datetime] = {}

        # Symbol mapping
        self.symbols = {
            'silver': 'SLV',      # iShares Silver Trust (proxy for silver)
            'gold': 'GLD',        # SPDR Gold Shares
            'vix': 'VIX',         # Volatility Index
            'morgan_stanley': 'MS',
            'citigroup': 'C',
            'jpmorgan': 'JPM',
            'hsbc': 'HSBC',
            'scotiabank': 'BNS',
            'bank_of_america': 'BAC',
            'goldman': 'GS',
            'deutsche_bank': 'DB',
            'ubs': 'UBS',
            'barclays': 'BCS',
            # ETFs
            'regional_banks': 'KRE',
            'financials': 'XLF',
            'real_estate': 'VNQ',
        }

        # Price history for tracking changes
        self.price_history: Dict[str, List[float]] = {}

    def _fetch_quote(self, symbol: str) -> Optional[Dict]:
        """Fetch quote from Finnhub API"""
        if not self.api_key:
            logger.warning("No Finnhub API key configured")
            return None

        try:
            url = f"{self.base_url}/quote"
            params = {'symbol': symbol, 'token': self.api_key}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None

    def get_price(self, asset: str, force_refresh: bool = False) -> Optional[PriceData]:
        """Get current price for an asset"""
        symbol = self.symbols.get(asset, asset.upper())

        # Check cache
        if not force_refresh and symbol in self.last_fetch:
            elapsed = (datetime.now() - self.last_fetch[symbol]).total_seconds()
            if elapsed < self.cache_ttl and symbol in self.cache:
                return self.cache[symbol]

        # Fetch from API
        quote = self._fetch_quote(symbol)
        if not quote or quote.get('c', 0) == 0:
            return self.cache.get(symbol)  # Return cached if available

        # Handle SLV -> silver price conversion (SLV is ~1:1 with silver)
        price = quote['c']

        price_data = PriceData(
            symbol=symbol,
            price=price,
            change=quote.get('d', 0) or 0,
            change_pct=quote.get('dp', 0) or 0,
            prev_close=quote.get('pc', price) or price,
            high=quote.get('h', price) or price,
            low=quote.get('l', price) or price,
            volume=0,  # Finnhub doesn't return volume in quote
            timestamp=datetime.now(),
        )

        # Update cache
        self.cache[symbol] = price_data
        self.last_fetch[symbol] = datetime.now()

        # Update price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]

        return price_data

    def get_all_prices(self) -> Dict[str, PriceData]:
        """Get prices for all tracked assets"""
        prices = {}
        for asset, symbol in self.symbols.items():
            price_data = self.get_price(asset)
            if price_data:
                prices[asset] = price_data
        return prices

    def get_bank_prices(self) -> Dict[str, PriceData]:
        """Get prices for all bank stocks"""
        bank_assets = [
            'morgan_stanley', 'citigroup', 'jpmorgan', 'hsbc',
            'scotiabank', 'bank_of_america', 'goldman', 'ubs'
        ]
        return {asset: self.get_price(asset) for asset in bank_assets
                if self.get_price(asset)}

    def get_metal_prices(self) -> Dict[str, PriceData]:
        """Get prices for precious metals"""
        return {
            'silver': self.get_price('silver'),
            'gold': self.get_price('gold'),
        }

    def get_week_change(self, asset: str) -> Optional[float]:
        """Calculate weekly change for an asset"""
        symbol = self.symbols.get(asset, asset.upper())
        history = self.price_history.get(symbol, [])

        if len(history) < 2:
            return None

        # Use available history (may not be full week)
        oldest = history[0]
        newest = history[-1]

        if oldest == 0:
            return None

        return ((newest - oldest) / oldest) * 100

    def check_price_alerts(self, alert_manager) -> List:
        """Check all prices against alert thresholds"""
        alerts = []

        # Check silver
        silver = self.get_price('silver')
        if silver and silver.prev_close > 0:
            alert = alert_manager.check_price_alerts(
                silver.price, silver.prev_close, 'silver'
            )
            if alert:
                alerts.append(alert)

        # Check bank stocks
        banks = [
            ('MS', 'Morgan Stanley', 'morgan_stanley'),
            ('C', 'Citigroup', 'citigroup'),
            ('HSBC', 'HSBC', 'hsbc'),
            ('BNS', 'Scotiabank', 'scotiabank'),
        ]
        for ticker, name, asset in banks:
            price_data = self.get_price(asset)
            if price_data and price_data.prev_close > 0:
                alert = alert_manager.check_bank_stock_alerts(
                    ticker, name, price_data.price, price_data.prev_close
                )
                if alert:
                    alerts.append(alert)

        return alerts

    def get_summary(self) -> Dict:
        """Get price summary for dashboard"""
        silver = self.get_price('silver')
        gold = self.get_price('gold')
        vix = self.get_price('vix')

        return {
            'silver': {
                'price': silver.price if silver else None,
                'change_pct': silver.change_pct if silver else None,
                'week_change': self.get_week_change('silver'),
            },
            'gold': {
                'price': gold.price if gold else None,
                'change_pct': gold.change_pct if gold else None,
                'week_change': self.get_week_change('gold'),
            },
            'vix': {
                'price': vix.price if vix else None,
                'change_pct': vix.change_pct if vix else None,
            },
            'last_updated': datetime.now().isoformat(),
        }
