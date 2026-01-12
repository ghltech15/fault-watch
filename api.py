"""
fault.watch API Backend
========================
FastAPI backend for the fault.watch dashboard.
Provides REST endpoints for market data, bank analysis, and content generation.

Run with: uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import json
import os

import requests

from content_generator import ContentGenerator, TemplateType, ContentConfig, VideoConfig
from content_triggers import TriggerManager, TriggerConfig

# =============================================================================
# APP CONFIGURATION
# =============================================================================

app = FastAPI(
    title="fault.watch API",
    description="Systemic Risk Monitoring & TikTok Content Generation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:3001",
        "https://fault-watch-ui.fly.dev",  # Production frontend
        "https://fault.watch",  # Custom domain
        "https://www.fault.watch",  # www subdomain
        "https://*.vercel.app",  # Vercel previews
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# CONSTANTS
# =============================================================================

SEC_DEADLINE = datetime(2026, 2, 15, 16, 0, 0)
LLOYDS_DEADLINE = datetime(2026, 1, 31, 23, 59, 59)

# Bank Short Positions (in ounces)
MS_SHORT_POSITION_OZ = 5_900_000_000
CITI_SHORT_POSITION_OZ = 6_340_000_000
JPM_LONG_POSITION_OZ = 750_000_000

BANK_SHORT_POSITIONS = {
    'C': {
        'name': 'Citigroup',
        'ticker': 'C',
        'position': 'SHORT',
        'ounces': 6_340_000_000,
        'equity': 175_000_000_000,
        'insolvency_price': 80,
        'note': "LARGEST short - Lloyd's insurance deadline Jan 31"
    },
    'MS': {
        'name': 'Morgan Stanley',
        'ticker': 'MS',
        'position': 'SHORT',
        'ounces': 5_900_000_000,
        'equity': 100_000_000_000,
        'insolvency_price': 47,
        'note': 'SEC deadline Feb 15'
    },
    'JPM': {
        'name': 'JPMorgan',
        'ticker': 'JPM',
        'position': 'LONG',
        'ounces': 750_000_000,
        'equity': 330_000_000_000,
        'note': 'FLIPPED from 200M short to 750M LONG (Jun-Oct 2025)'
    },
}

BANK_PM_EXPOSURE = {
    'JPM': {'name': 'JPMorgan Chase', 'ticker': 'JPM', 'pm_derivatives': 437.4e9, 'equity': 330e9, 'pct_total': 62.1},
    'C': {'name': 'Citigroup', 'ticker': 'C', 'pm_derivatives': 204.3e9, 'equity': 175e9, 'pct_total': 29.0},
    'BAC': {'name': 'Bank of America', 'ticker': 'BAC', 'pm_derivatives': 47.9e9, 'equity': 280e9, 'pct_total': 6.8},
    'GS': {'name': 'Goldman Sachs', 'ticker': 'GS', 'pm_derivatives': 0.614e9, 'equity': 120e9, 'pct_total': 0.1},
    'MS': {'name': 'Morgan Stanley', 'ticker': 'MS', 'pm_derivatives': None, 'equity': 100e9, 'pct_total': None, 'note': 'Not in OCC Top 4 - Hidden exposure'},
    'HSBC': {'name': 'HSBC Holdings', 'ticker': 'HSBC', 'pm_derivatives': None, 'equity': 190e9, 'pct_total': None, 'note': 'LBMA Market Maker - London exposure'},
    'DB': {'name': 'Deutsche Bank', 'ticker': 'DB', 'pm_derivatives': None, 'equity': 55e9, 'pct_total': None, 'note': 'Settled PM manipulation 2016'},
    'UBS': {'name': 'UBS Group', 'ticker': 'UBS', 'pm_derivatives': None, 'equity': 100e9, 'pct_total': None, 'note': '$15M CFTC fine 2018'},
    'BCS': {'name': 'Barclays', 'ticker': 'BCS', 'pm_derivatives': None, 'equity': 50e9, 'pct_total': None, 'note': 'LBMA Market Maker'},
    'BNS': {'name': 'Scotiabank', 'ticker': 'BNS', 'pm_derivatives': None, 'equity': 65e9, 'pct_total': None, 'note': '$127M fine 2020 PM manipulation'},
}

FED_REPO_TOTAL = 51.25  # billions

THRESHOLDS = {
    'vix': {'warning': 25, 'critical': 35},
    'silver': {'warning': 90, 'critical': 100},
    'gold': {'warning': 4700, 'critical': 5000},
    'ms_daily': {'warning': -3, 'critical': -7},
    'ms_price': {'warning': 100, 'critical': 80},
    'fed_repo': {'warning': 20, 'critical': 50},
}

# FRED API Key (free, 120 requests/min)
FRED_API_KEY = os.getenv('FRED_API_KEY', '')

# =============================================================================
# CONTAGION SECTORS - Investment Opportunities
# =============================================================================

CONTAGION_SECTORS = {
    'regional_banks': {
        'name': 'Regional Banks',
        'etf': 'KRE',
        'inverse': 'FAZ',
        'why': 'Credit contagion, deposit flight from big banks',
        'plays': ['KRE puts', 'FAZ calls (3x inverse financials)'],
    },
    'commercial_re': {
        'name': 'Commercial Real Estate',
        'etf': 'VNQ',
        'inverse': 'SRS',
        'why': 'Banks stop lending, vacancy rates spike, defaults surge',
        'plays': ['SRS (2x inverse RE)', 'Puts on O, VNO, SPG'],
    },
    'insurance': {
        'name': 'Insurance/Reinsurance',
        'etf': 'KIE',
        'inverse': None,
        'why': "Lloyd's exposure, bank failure claims, counterparty risk",
        'plays': ['Puts on MET, PRU, AIG, ALL'],
    },
    'credit_cards': {
        'name': 'Consumer Credit',
        'etf': None,
        'inverse': None,
        'why': 'Default rates spike, banks cut credit lines',
        'plays': ['Puts on COF, SYF, DFS, AXP'],
    },
    'auto_lenders': {
        'name': 'Auto Finance',
        'etf': None,
        'inverse': None,
        'why': 'Subprime auto collapse, repo surge',
        'plays': ['Puts on ALLY, CAR, SC'],
    },
    'mortgage_reits': {
        'name': 'Mortgage REITs',
        'etf': 'REM',
        'inverse': None,
        'why': 'Interest rate chaos, MBS losses, margin calls',
        'plays': ['Puts on NLY, AGNC, STWD'],
    },
    'private_equity': {
        'name': 'Private Equity',
        'etf': None,
        'inverse': None,
        'why': 'Leverage unwinds, portfolio company defaults',
        'plays': ['Puts on BX, KKR, APO, CG'],
    },
    'clearing_houses': {
        'name': 'Clearing/Exchanges',
        'etf': None,
        'inverse': None,
        'why': 'Counterparty risk, margin call cascades',
        'plays': ['Puts on CME, ICE, NDAQ'],
    },
}

# Junior Silver Miners - High leverage plays
JUNIOR_SILVER_MINERS = {
    'AG': {'name': 'First Majestic Silver', 'leverage': 'high'},
    'EXK': {'name': 'Endeavour Silver', 'leverage': 'very_high'},
    'PAAS': {'name': 'Pan American Silver', 'leverage': 'medium'},
    'HL': {'name': 'Hecla Mining', 'leverage': 'medium'},
    'CDE': {'name': 'Coeur Mining', 'leverage': 'high'},
    'MAG': {'name': 'MAG Silver', 'leverage': 'very_high'},
    'SILV': {'name': 'SilverCrest Metals', 'leverage': 'high'},
}

# FRED Series IDs for economic data
FRED_SERIES = {
    'ted_spread': 'TEDRATE',           # TED Spread (interbank stress)
    'credit_spread': 'BAMLC0A0CM',     # Investment Grade Credit Spread
    'high_yield_spread': 'BAMLH0A0HYM2', # High Yield Spread
    'bank_credit': 'TOTBKCR',          # Total Bank Credit
    'commercial_paper': 'COMPAPER',    # Commercial Paper Outstanding
    'repo_rate': 'SOFR',               # SOFR Rate
    'reverse_repo': 'RRPONTSYD',       # Reverse Repo
    'delinquency_credit': 'DRCCLACBS', # Credit Card Delinquency
    'delinquency_auto': 'DRSFRMACBS',  # Auto Loan Delinquency
    'bank_deposits': 'DPSACBW027SBOG', # Bank Deposits
    'loan_loss': 'LLRNPT',             # Loan Loss Provisions
}

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class PriceData(BaseModel):
    price: float
    prev_close: Optional[float] = None
    change_pct: float = 0
    week_change: float = 0


class CountdownData(BaseModel):
    days: int
    hours: int
    minutes: int
    expired: bool
    deadline: str
    label: str


class AlertData(BaseModel):
    level: str  # 'critical', 'warning', 'info'
    title: str
    detail: str
    action: Optional[str] = None


class BankExposure(BaseModel):
    name: str
    ticker: str
    position: Optional[str] = None
    ounces: Optional[int] = None
    equity: float
    pm_derivatives: Optional[float] = None
    pct_total: Optional[float] = None
    insolvency_price: Optional[float] = None
    note: Optional[str] = None
    current_price: Optional[float] = None
    daily_change: Optional[float] = None
    weekly_change: Optional[float] = None
    risk_score: Optional[float] = None
    paper_loss: Optional[float] = None


class ScenarioData(BaseModel):
    silver_price: float
    ms_loss: float
    citi_loss: float
    jpm_gain: float
    total_short_loss: float
    ms_insolvent: bool
    citi_insolvent: bool
    fed_coverage_pct: float


class DominoStatus(BaseModel):
    id: str
    label: str
    status: str
    color: str
    detail: str


class DashboardData(BaseModel):
    risk_index: float
    risk_label: str
    risk_color: str
    prices: Dict[str, PriceData]
    countdowns: Dict[str, CountdownData]
    alerts: List[AlertData]
    dominoes: List[DominoStatus]
    stress_level: float
    last_updated: str


class ContentRequest(BaseModel):
    template: str  # 'price_alert', 'countdown', 'bank_crisis', 'daily_summary'
    data: Dict[str, Any]
    generate_video: bool = False


class ContentResponse(BaseModel):
    success: bool
    file_path: Optional[str] = None
    file_type: str  # 'image' or 'video'


# =============================================================================
# NEW MODELS - Contagion & Credit Stress
# =============================================================================

class CreditStressData(BaseModel):
    """Credit market stress indicators"""
    ted_spread: Optional[float] = None  # TED spread (LIBOR - T-Bill)
    credit_spread: Optional[float] = None  # IG credit spread
    high_yield_spread: Optional[float] = None  # Junk bond spread
    sofr_rate: Optional[float] = None  # SOFR overnight rate
    stress_level: str = 'normal'  # normal, elevated, high, extreme
    stress_score: float = 0  # 0-100


class LiquidityData(BaseModel):
    """Liquidity crisis indicators"""
    reverse_repo: Optional[float] = None  # Fed reverse repo (billions)
    bank_deposits: Optional[float] = None  # Total bank deposits
    deposit_change_pct: Optional[float] = None  # Weekly change
    commercial_paper: Optional[float] = None  # CP outstanding
    liquidity_score: float = 0  # 0-100 (higher = more stress)


class DelinquencyData(BaseModel):
    """Consumer credit delinquency rates"""
    credit_card: Optional[float] = None  # CC delinquency rate %
    auto_loan: Optional[float] = None  # Auto loan delinquency %
    mortgage: Optional[float] = None  # Mortgage delinquency %
    trend: str = 'stable'  # improving, stable, worsening, critical


class ComexData(BaseModel):
    """COMEX silver inventory data"""
    registered_oz: Optional[float] = None  # Deliverable silver
    eligible_oz: Optional[float] = None  # Total vault silver
    total_oz: Optional[float] = None
    open_interest_oz: Optional[float] = None  # Futures contracts
    coverage_ratio: Optional[float] = None  # OI / Registered
    days_of_supply: Optional[float] = None
    status: str = 'normal'  # normal, tight, critical, default_risk


class ContagionSector(BaseModel):
    """Sector contagion data"""
    id: str
    name: str
    etf: Optional[str] = None
    inverse_etf: Optional[str] = None
    current_price: Optional[float] = None
    change_pct: Optional[float] = None
    week_change: Optional[float] = None
    why_collapse: str
    investment_plays: List[str]
    risk_level: str = 'low'  # low, medium, high, critical
    contagion_score: float = 0  # 0-100


class JuniorMiner(BaseModel):
    """Junior silver miner data"""
    ticker: str
    name: str
    price: Optional[float] = None
    change_pct: Optional[float] = None
    leverage_level: str  # medium, high, very_high
    potential_multiple: Optional[str] = None  # e.g. "10-20x"


class ContagionRiskData(BaseModel):
    """Overall contagion risk assessment"""
    contagion_score: float  # 0-100 overall contagion risk
    contagion_level: str  # contained, spreading, systemic, collapse
    contagion_color: str
    credit_stress: CreditStressData
    liquidity: LiquidityData
    delinquencies: DelinquencyData
    comex: ComexData
    sectors: List[ContagionSector]
    junior_miners: List[JuniorMiner]
    cascade_stage: int  # 1-5 (which domino is falling)
    cascade_description: str
    last_updated: str
    error: Optional[str] = None


class TriggerStatusResponse(BaseModel):
    enabled: bool
    price_thresholds: Dict[str, List[float]]
    scheduled_times: List[str]
    next_scheduled: Optional[str]
    last_triggered: Dict[str, str]
    cooldown_hours: float
    generate_video: bool
    total_generated: int


# =============================================================================
# DATA FETCHING
# =============================================================================

import os
from zoneinfo import ZoneInfo

# Finnhub API key (set via environment variable) - 60 calls/min free tier
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')

# Cache for prices (30 minute cache during market hours)
_price_cache: Dict[str, Any] = {}
_cache_time: Optional[datetime] = None
CACHE_TTL_SECONDS = 1800  # 30 minutes


def is_market_hours() -> bool:
    """Check if US market is open (9:30 AM - 4:00 PM ET, Mon-Fri)"""
    et = ZoneInfo('America/New_York')
    now = datetime.now(et)

    # Check if weekday (0=Monday, 4=Friday)
    if now.weekday() > 4:
        return False

    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= now <= market_close


def should_fetch_new_data() -> bool:
    """Determine if we should fetch new data based on cache and market hours"""
    global _cache_time

    # If no cache, fetch
    if _cache_time is None:
        return True

    # Check cache age
    cache_age = (datetime.now() - _cache_time).total_seconds()

    # During market hours: refresh every 30 minutes
    if is_market_hours():
        return cache_age >= CACHE_TTL_SECONDS

    # Outside market hours: use cached data, refresh every 2 hours
    return cache_age >= 7200


def fetch_finnhub_quote(symbol: str) -> Optional[Dict]:
    """Fetch quote from Finnhub (60 calls/min free tier)"""
    if not FINNHUB_API_KEY:
        return None

    try:
        url = f'https://finnhub.io/api/v1/quote'
        params = {
            'symbol': symbol,
            'token': FINNHUB_API_KEY
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Finnhub returns: c=current, pc=previous close, d=change, dp=change percent
            if data and data.get('c', 0) > 0:
                return {
                    'price': float(data['c']),
                    'prev_close': float(data.get('pc', data['c'])),
                    'change_pct': float(data.get('dp', 0)),
                    'high': float(data.get('h', 0)),
                    'low': float(data.get('l', 0)),
                }
    except Exception as e:
        print(f"Finnhub error for {symbol}: {e}")
    return None


def fetch_finnhub_forex(symbol: str) -> Optional[Dict]:
    """Fetch forex/commodity from Finnhub"""
    if not FINNHUB_API_KEY:
        return None

    try:
        url = f'https://finnhub.io/api/v1/forex/candle'
        # Get last day of data
        import time
        now = int(time.time())
        params = {
            'symbol': symbol,
            'resolution': 'D',
            'from': now - 86400 * 5,
            'to': now,
            'token': FINNHUB_API_KEY
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and data.get('s') == 'ok' and data.get('c'):
                closes = data['c']
                current = closes[-1]
                prev = closes[-2] if len(closes) > 1 else current
                first = closes[0]
                return {
                    'price': float(current),
                    'prev_close': float(prev),
                    'change_pct': ((current / prev) - 1) * 100 if prev else 0,
                    'week_change': ((current / first) - 1) * 100 if first else 0,
                }
    except Exception as e:
        print(f"Finnhub forex error for {symbol}: {e}")
    return None


def fetch_all_prices() -> Dict[str, PriceData]:
    """Fetch real-time prices from Finnhub with smart caching"""
    global _price_cache, _cache_time

    # Return cached data if still valid
    if not should_fetch_new_data() and _price_cache:
        print("Returning cached price data")
        return _price_cache

    prices = {}

    # Finnhub stock symbols (US stocks)
    finnhub_stocks = {
        'SPY': 'sp500',
        'MS': 'morgan_stanley',
        'JPM': 'jpmorgan',
        'C': 'citigroup',
        'BAC': 'bank_of_america',
        'GS': 'goldman',
        'WFC': 'wells_fargo',
        'HSBC': 'hsbc',
        'DB': 'deutsche_bank',
        'UBS': 'ubs',
        'BCS': 'barclays',
        'BNS': 'scotiabank',
        'KRE': 'regional_banks',
        'XLF': 'financials',
        'GDX': 'gold_miners',
        'SLV': 'slv',
        'GLD': 'gld',
        'TLT': 'long_treasury',
        'HYG': 'high_yield',
        'XLE': 'energy',
    }

    # Fetch stock quotes from Finnhub
    if FINNHUB_API_KEY:
        print(f"Fetching {len(finnhub_stocks)} stocks from Finnhub...")
        for symbol, name in finnhub_stocks.items():
            quote = fetch_finnhub_quote(symbol)
            if quote and quote['price'] > 0:
                prices[name] = PriceData(
                    price=quote['price'],
                    prev_close=quote['prev_close'],
                    change_pct=quote['change_pct'],
                    week_change=0
                )

        # Derive silver price from SLV ETF
        # SLV tracks silver at roughly 1:1 (each share ≈ 0.93 oz silver)
        if 'slv' in prices:
            slv_price = prices['slv'].price
            prices['silver'] = PriceData(
                price=slv_price,  # SLV roughly equals silver spot
                prev_close=prices['slv'].prev_close,
                change_pct=prices['slv'].change_pct,
                week_change=0
            )

        # Derive gold price from GLD ETF
        # GLD tracks gold at roughly 1/10 (each share ≈ 0.1 oz gold)
        if 'gld' in prices:
            gld_price = prices['gld'].price
            prices['gold'] = PriceData(
                price=gld_price * 10,  # GLD is ~1/10 of gold spot
                prev_close=prices['gld'].prev_close * 10 if prices['gld'].prev_close else None,
                change_pct=prices['gld'].change_pct,
                week_change=0
            )

        # VIX - try CBOE VIX futures
        vix_quote = fetch_finnhub_quote('VXX')  # VIX short-term futures ETN
        if vix_quote and vix_quote['price'] > 0:
            prices['vix'] = PriceData(
                price=vix_quote['price'],
                prev_close=vix_quote['prev_close'],
                change_pct=vix_quote['change_pct'],
                week_change=0
            )
    else:
        print("WARNING: No FINNHUB_API_KEY set - cannot fetch stock prices")

    # CoinGecko for crypto (always available, no auth needed)
    try:
        resp = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin,ethereum', 'vs_currencies': 'usd', 'include_24hr_change': 'true'},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if 'bitcoin' in data:
                prices['bitcoin'] = PriceData(
                    price=data['bitcoin']['usd'],
                    change_pct=data['bitcoin'].get('usd_24h_change', 0),
                    week_change=0
                )
    except Exception as e:
        print(f"CoinGecko error: {e}")

    # Calculate Gold/Silver Ratio if both available
    if 'gold' in prices and 'silver' in prices and prices['silver'].price > 0:
        prices['gold_silver_ratio'] = PriceData(
            price=prices['gold'].price / prices['silver'].price,
            change_pct=0
        )

    # Only update cache if we got meaningful data (at least 5 prices)
    if len(prices) >= 5:
        _price_cache = prices
        _cache_time = datetime.now()
        print(f"Cached {len(prices)} prices")
    else:
        print(f"Only got {len(prices)} prices, not caching")

    return prices if prices else _price_cache


# =============================================================================
# CONTAGION DATA FETCHING
# =============================================================================

# Cache for contagion data (refresh every hour)
_contagion_cache: Optional[Dict] = None
_contagion_cache_time: Optional[datetime] = None
CONTAGION_CACHE_TTL = 3600  # 1 hour


def fetch_fred_series(series_id: str) -> Optional[float]:
    """Fetch latest value from FRED API"""
    if not FRED_API_KEY:
        return None

    try:
        url = 'https://api.stlouisfed.org/fred/series/observations'
        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 1
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            observations = data.get('observations', [])
            if observations and observations[0].get('value') != '.':
                return float(observations[0]['value'])
    except Exception as e:
        print(f"FRED error for {series_id}: {e}")
    return None


def fetch_credit_stress() -> CreditStressData:
    """Fetch credit market stress indicators from FRED"""
    ted_spread = fetch_fred_series('TEDRATE')
    credit_spread = fetch_fred_series('BAMLC0A0CM')
    hy_spread = fetch_fred_series('BAMLH0A0HYM2')
    sofr = fetch_fred_series('SOFR')

    # Calculate stress score (0-100)
    stress_score = 0

    if ted_spread:
        if ted_spread > 1.0:
            stress_score += 30
        elif ted_spread > 0.5:
            stress_score += 15
        elif ted_spread > 0.25:
            stress_score += 5

    if hy_spread:
        if hy_spread > 800:
            stress_score += 40
        elif hy_spread > 500:
            stress_score += 25
        elif hy_spread > 400:
            stress_score += 10

    if credit_spread:
        if credit_spread > 200:
            stress_score += 30
        elif credit_spread > 150:
            stress_score += 15
        elif credit_spread > 100:
            stress_score += 5

    # Determine stress level
    if stress_score >= 70:
        stress_level = 'extreme'
    elif stress_score >= 50:
        stress_level = 'high'
    elif stress_score >= 25:
        stress_level = 'elevated'
    else:
        stress_level = 'normal'

    return CreditStressData(
        ted_spread=ted_spread,
        credit_spread=credit_spread,
        high_yield_spread=hy_spread,
        sofr_rate=sofr,
        stress_level=stress_level,
        stress_score=min(stress_score, 100)
    )


def fetch_liquidity_data() -> LiquidityData:
    """Fetch liquidity indicators from FRED"""
    reverse_repo = fetch_fred_series('RRPONTSYD')
    deposits = fetch_fred_series('DPSACBW027SBOG')
    commercial_paper = fetch_fred_series('COMPAPER')

    # Convert reverse repo from millions to billions
    if reverse_repo:
        reverse_repo = reverse_repo / 1000

    # Calculate liquidity stress score
    liquidity_score = 0

    # High reverse repo = excess liquidity parked at Fed (can be sign of stress)
    if reverse_repo and reverse_repo > 2000:
        liquidity_score += 20
    elif reverse_repo and reverse_repo > 1000:
        liquidity_score += 10

    return LiquidityData(
        reverse_repo=reverse_repo,
        bank_deposits=deposits,
        deposit_change_pct=None,  # Would need historical calc
        commercial_paper=commercial_paper,
        liquidity_score=min(liquidity_score, 100)
    )


def fetch_delinquency_data() -> DelinquencyData:
    """Fetch consumer delinquency rates from FRED"""
    cc_delinquency = fetch_fred_series('DRCCLACBS')
    auto_delinquency = fetch_fred_series('DRSFRMACBS')

    # Determine trend based on levels
    trend = 'stable'
    if cc_delinquency:
        if cc_delinquency > 4.0:
            trend = 'critical'
        elif cc_delinquency > 3.0:
            trend = 'worsening'

    return DelinquencyData(
        credit_card=cc_delinquency,
        auto_loan=auto_delinquency,
        mortgage=None,
        trend=trend
    )


def fetch_comex_data() -> ComexData:
    """
    Fetch COMEX silver inventory data.
    Note: Real COMEX data requires CME DataMine subscription.
    Using estimates based on public reports.
    """
    # These would ideally come from CME DataMine API
    # Using recent public estimates for now
    registered = 280_000_000  # ~280M oz registered (deliverable)
    eligible = 520_000_000   # ~520M oz eligible (total vault)
    open_interest = 800_000_000  # ~800M oz in futures contracts

    total = registered + eligible
    coverage_ratio = open_interest / registered if registered > 0 else 999

    # Days of supply based on average daily delivery volume
    avg_daily_delivery = 5_000_000  # 5M oz/day average
    days_of_supply = registered / avg_daily_delivery if avg_daily_delivery > 0 else 0

    # Determine status
    if coverage_ratio > 5:
        status = 'critical'
    elif coverage_ratio > 3:
        status = 'tight'
    elif coverage_ratio > 2:
        status = 'elevated'
    else:
        status = 'normal'

    return ComexData(
        registered_oz=registered,
        eligible_oz=eligible,
        total_oz=total,
        open_interest_oz=open_interest,
        coverage_ratio=round(coverage_ratio, 2),
        days_of_supply=round(days_of_supply, 1),
        status=status
    )


def fetch_contagion_sectors(prices: Dict[str, PriceData]) -> List[ContagionSector]:
    """Calculate contagion risk for each sector"""
    sectors = []

    # Map sector ETFs to price keys
    sector_price_map = {
        'regional_banks': 'regional_banks',
        'commercial_re': None,  # VNQ not in our price list yet
        'insurance': None,
        'credit_cards': None,
        'auto_lenders': None,
        'mortgage_reits': None,
        'private_equity': None,
        'clearing_houses': None,
    }

    # Fetch additional sector ETFs from Finnhub
    additional_etfs = {
        'VNQ': 'commercial_re',
        'REM': 'mortgage_reits',
        'COF': 'credit_cards',
        'ALLY': 'auto_lenders',
        'BX': 'private_equity',
        'CME': 'clearing_houses',
        'MET': 'insurance',
    }

    etf_prices = {}
    if FINNHUB_API_KEY:
        for symbol, sector_id in additional_etfs.items():
            quote = fetch_finnhub_quote(symbol)
            if quote and quote['price'] > 0:
                etf_prices[sector_id] = quote

    for sector_id, sector_info in CONTAGION_SECTORS.items():
        # Get price data
        price_key = sector_price_map.get(sector_id)
        price_data = prices.get(price_key) if price_key else None

        # Check additional ETF prices
        if not price_data and sector_id in etf_prices:
            quote = etf_prices[sector_id]
            current_price = quote['price']
            change_pct = quote['change_pct']
        elif price_data:
            current_price = price_data.price
            change_pct = price_data.change_pct
        else:
            current_price = None
            change_pct = None

        # Calculate contagion score based on price movement
        contagion_score = 0
        if change_pct:
            if change_pct < -10:
                contagion_score = 90
            elif change_pct < -5:
                contagion_score = 60
            elif change_pct < -3:
                contagion_score = 40
            elif change_pct < 0:
                contagion_score = 20

        # Determine risk level
        if contagion_score >= 70:
            risk_level = 'critical'
        elif contagion_score >= 50:
            risk_level = 'high'
        elif contagion_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        sectors.append(ContagionSector(
            id=sector_id,
            name=sector_info['name'],
            etf=sector_info.get('etf'),
            inverse_etf=sector_info.get('inverse'),
            current_price=current_price,
            change_pct=change_pct,
            week_change=price_data.week_change if price_data else None,
            why_collapse=sector_info['why'],
            investment_plays=sector_info['plays'],
            risk_level=risk_level,
            contagion_score=contagion_score
        ))

    return sectors


def fetch_junior_miners(prices: Dict[str, PriceData]) -> List[JuniorMiner]:
    """Fetch junior silver miner data"""
    miners = []

    for ticker, info in JUNIOR_SILVER_MINERS.items():
        quote = fetch_finnhub_quote(ticker) if FINNHUB_API_KEY else None

        # Determine potential multiple based on leverage
        multiples = {
            'medium': '5-10x',
            'high': '10-20x',
            'very_high': '20-50x'
        }

        miners.append(JuniorMiner(
            ticker=ticker,
            name=info['name'],
            price=quote['price'] if quote else None,
            change_pct=quote['change_pct'] if quote else None,
            leverage_level=info['leverage'],
            potential_multiple=multiples.get(info['leverage'], '5-10x')
        ))

    return miners


def calculate_cascade_stage(prices: Dict[str, PriceData], credit_stress: CreditStressData) -> tuple:
    """
    Determine which stage of the domino cascade we're in.

    Stage 1: Silver rising, banks stable
    Stage 2: Silver spiking, bank stocks falling
    Stage 3: Credit stress emerging, regional bank contagion
    Stage 4: Liquidity crisis, broad market panic
    Stage 5: Systemic collapse, Fed intervention
    """
    silver = prices.get('silver')
    ms = prices.get('morgan_stanley')
    citi = prices.get('citigroup')
    kre = prices.get('regional_banks')
    vix = prices.get('vix')

    stage = 1
    description = "Silver accumulation phase - banks stable"

    # Stage 2: Silver spiking, banks under pressure
    if silver and silver.price > 40:
        if (ms and ms.change_pct < -2) or (citi and citi.change_pct < -2):
            stage = 2
            description = "Bank stress emerging - watch MS and Citi closely"

    # Stage 3: Credit stress, regional contagion
    if credit_stress.stress_score > 30:
        if kre and kre.change_pct < -3:
            stage = 3
            description = "Credit contagion spreading to regional banks"

    # Stage 4: Liquidity crisis
    if credit_stress.stress_score > 50:
        if vix and vix.price > 30:
            stage = 4
            description = "Liquidity crisis - broad market panic"

    # Stage 5: Systemic collapse
    if credit_stress.stress_score > 70:
        if (ms and ms.change_pct < -10) or (citi and citi.change_pct < -10):
            stage = 5
            description = "SYSTEMIC COLLAPSE - Fed intervention imminent"

    return stage, description


def fetch_contagion_risk() -> ContagionRiskData:
    """Fetch comprehensive contagion risk data"""
    global _contagion_cache, _contagion_cache_time

    # Check cache
    if _contagion_cache_time and (datetime.now() - _contagion_cache_time).seconds < CONTAGION_CACHE_TTL:
        return _contagion_cache

    # Fetch all data
    prices = fetch_all_prices()
    credit_stress = fetch_credit_stress()
    liquidity = fetch_liquidity_data()
    delinquencies = fetch_delinquency_data()
    comex = fetch_comex_data()
    sectors = fetch_contagion_sectors(prices)
    junior_miners = fetch_junior_miners(prices)

    # Calculate cascade stage
    cascade_stage, cascade_description = calculate_cascade_stage(prices, credit_stress)

    # Calculate overall contagion score
    contagion_score = 0

    # Credit stress contribution (0-40)
    contagion_score += credit_stress.stress_score * 0.4

    # COMEX status contribution (0-30)
    comex_scores = {'normal': 0, 'elevated': 10, 'tight': 20, 'critical': 30}
    contagion_score += comex_scores.get(comex.status, 0)

    # Sector contagion contribution (0-30)
    avg_sector_score = sum(s.contagion_score for s in sectors) / len(sectors) if sectors else 0
    contagion_score += avg_sector_score * 0.3

    contagion_score = min(contagion_score, 100)

    # Determine contagion level
    if contagion_score >= 75:
        contagion_level = 'collapse'
        contagion_color = '#ff0000'
    elif contagion_score >= 50:
        contagion_level = 'systemic'
        contagion_color = '#ff3b5c'
    elif contagion_score >= 25:
        contagion_level = 'spreading'
        contagion_color = '#ff8c42'
    else:
        contagion_level = 'contained'
        contagion_color = '#4ade80'

    result = ContagionRiskData(
        contagion_score=round(contagion_score, 1),
        contagion_level=contagion_level,
        contagion_color=contagion_color,
        credit_stress=credit_stress,
        liquidity=liquidity,
        delinquencies=delinquencies,
        comex=comex,
        sectors=sectors,
        junior_miners=junior_miners,
        cascade_stage=cascade_stage,
        cascade_description=cascade_description,
        last_updated=datetime.now().isoformat()
    )

    # Update cache
    _contagion_cache = result
    _contagion_cache_time = datetime.now()

    return result


# =============================================================================
# CALCULATION FUNCTIONS
# =============================================================================

def calculate_countdown(deadline: datetime, label: str) -> CountdownData:
    """Calculate time remaining to a deadline"""
    now = datetime.now()
    remaining = deadline - now
    if remaining.total_seconds() <= 0:
        return CountdownData(
            days=0, hours=0, minutes=0, expired=True,
            deadline=deadline.isoformat(), label=label
        )
    return CountdownData(
        days=remaining.days,
        hours=remaining.seconds // 3600,
        minutes=(remaining.seconds % 3600) // 60,
        expired=False,
        deadline=deadline.isoformat(),
        label=label
    )


def calculate_bank_exposure(ticker: str, silver_price: float, entry_price: float = 30) -> Dict[str, Any]:
    """Calculate bank exposure and losses from silver position"""
    bank = BANK_SHORT_POSITIONS.get(ticker)
    if not bank:
        return {}

    position_oz = bank['ounces']
    is_short = bank['position'] == 'SHORT'

    if is_short:
        current_value = position_oz * silver_price
        entry_value = position_oz * entry_price
        paper_loss = current_value - entry_value
    else:  # LONG
        paper_loss = -(position_oz * (silver_price - entry_price))  # Negative loss = gain

    equity = bank['equity']

    return {
        'position_oz': position_oz,
        'position_type': bank['position'],
        'current_value': position_oz * silver_price,
        'paper_loss': paper_loss,
        'loss_vs_equity': paper_loss / equity if is_short else 0,
        'insolvent': paper_loss > equity if is_short else False,
        'insolvency_price': bank.get('insolvency_price'),
    }


def calculate_stress_level(prices: Dict[str, PriceData]) -> float:
    """Calculate MS stress level 0-100"""
    stress = 0

    ms = prices.get('morgan_stanley')
    if ms:
        ms_daily = ms.change_pct
        ms_weekly = ms.week_change

        if ms_daily < -10: stress += 30
        elif ms_daily < -5: stress += 20
        elif ms_daily < -3: stress += 10
        elif ms_daily < 0: stress += 5

        if ms_weekly < -15: stress += 25
        elif ms_weekly < -10: stress += 15
        elif ms_weekly < -5: stress += 10

    silver = prices.get('silver')
    if silver:
        if silver.price > 120: stress += 25
        elif silver.price > 100: stress += 20
        elif silver.price > 90: stress += 10
        elif silver.price > 85: stress += 5

    vix = prices.get('vix')
    if vix:
        if vix.price > 40: stress += 15
        elif vix.price > 30: stress += 10
        elif vix.price > 25: stress += 5

    kre = prices.get('regional_banks')
    if kre:
        if kre.week_change < -10: stress += 15
        elif kre.week_change < -5: stress += 10

    return min(stress, 100)


def calculate_risk_index(prices: Dict[str, PriceData], stress_level: float) -> float:
    """Calculate overall risk index 0-10"""
    risk = 0

    # Silver contribution (0-3)
    silver = prices.get('silver')
    if silver:
        if silver.price > 100: risk += 3
        elif silver.price > 90: risk += 2
        elif silver.price > 80: risk += 1

    # MS stress contribution (0-3)
    risk += (stress_level / 100) * 3

    # VIX contribution (0-2)
    vix = prices.get('vix')
    if vix:
        if vix.price > 35: risk += 2
        elif vix.price > 25: risk += 1

    # Countdown urgency (0-2)
    sec_countdown = calculate_countdown(SEC_DEADLINE, "SEC")
    lloyds_countdown = calculate_countdown(LLOYDS_DEADLINE, "Lloyd's")

    if sec_countdown.days < 7 or lloyds_countdown.days < 7:
        risk += 2
    elif sec_countdown.days < 14 or lloyds_countdown.days < 14:
        risk += 1

    return min(risk, 10)


def generate_alerts(prices: Dict[str, PriceData], stress_level: float) -> List[AlertData]:
    """Generate all alerts based on current conditions"""
    alerts = []

    sec_countdown = calculate_countdown(SEC_DEADLINE, "SEC")
    lloyds_countdown = calculate_countdown(LLOYDS_DEADLINE, "Lloyd's")

    # Citigroup alerts
    citi = prices.get('citigroup')
    if citi:
        if citi.change_pct < -7:
            alerts.append(AlertData(
                level='critical',
                title='CITI STOCK CRASHING',
                detail=f'Down {abs(citi.change_pct):.1f}% today',
                action='Monitor for contagion to other banks'
            ))
        elif citi.change_pct < -3:
            alerts.append(AlertData(
                level='warning',
                title='CITI UNDER PRESSURE',
                detail=f'Down {abs(citi.change_pct):.1f}% today',
                action='Watch for acceleration'
            ))

    # Lloyd's deadline
    if lloyds_countdown.days < 3 and not lloyds_countdown.expired:
        alerts.append(AlertData(
            level='critical',
            title="LLOYD'S DEADLINE IMMINENT",
            detail=f'{lloyds_countdown.days}d {lloyds_countdown.hours}h remaining',
            action='Citi loses insurance coverage Jan 31'
        ))
    elif lloyds_countdown.days < 14 and not lloyds_countdown.expired:
        alerts.append(AlertData(
            level='warning',
            title="LLOYD'S DEADLINE APPROACHING",
            detail=f'{lloyds_countdown.days} days remaining',
            action='Monitor Citi positioning'
        ))

    # Morgan Stanley alerts
    ms = prices.get('morgan_stanley')
    if ms:
        if ms.change_pct < -7:
            alerts.append(AlertData(
                level='critical',
                title='MS STOCK CRASHING',
                detail=f'Down {abs(ms.change_pct):.1f}% today',
                action='Watch for margin call triggers'
            ))
        elif ms.change_pct < -3:
            alerts.append(AlertData(
                level='warning',
                title='MS UNDER PRESSURE',
                detail=f'Down {abs(ms.change_pct):.1f}% today',
                action='Set tight alerts'
            ))

        if ms.price < 100:
            alerts.append(AlertData(
                level='critical',
                title='MS BELOW $100',
                detail=f'Currently ${ms.price:.2f}',
                action='Approaching insolvency price'
            ))

    # SEC Countdown
    if sec_countdown.days < 7 and not sec_countdown.expired:
        alerts.append(AlertData(
            level='critical',
            title='SEC DEADLINE IMMINENT',
            detail=f'{sec_countdown.days}d {sec_countdown.hours}h remaining',
            action='12.24B oz shorts must close'
        ))
    elif sec_countdown.days < 14 and not sec_countdown.expired:
        alerts.append(AlertData(
            level='warning',
            title='SEC DEADLINE APPROACHING',
            detail=f'{sec_countdown.days} days remaining',
            action='Monitor short covering activity'
        ))

    # Silver alerts
    silver = prices.get('silver')
    if silver:
        if silver.price > 100:
            alerts.append(AlertData(
                level='critical',
                title='SILVER BREAKOUT - $100+',
                detail=f'Currently ${silver.price:.2f}',
                action='Bank insolvency territory'
            ))
        elif silver.price > 90:
            alerts.append(AlertData(
                level='warning',
                title='Silver Approaching Critical',
                detail=f'Currently ${silver.price:.2f}',
                action='Watch for acceleration above $100'
            ))

    # VIX alerts
    vix = prices.get('vix')
    if vix and vix.price > 35:
        alerts.append(AlertData(
            level='critical',
            title='EXTREME VOLATILITY',
            detail=f'VIX at {vix.price:.1f}',
            action='Market panic mode'
        ))

    return alerts


def calculate_domino_status(prices: Dict[str, PriceData]) -> List[DominoStatus]:
    """Calculate status of each domino in the cascade"""
    dominoes = []

    # Domino 1: MS Stock
    ms = prices.get('morgan_stanley')
    if ms:
        if ms.price < 80:
            status, color = 'CRITICAL', '#ff3b5c'
        elif ms.price < 100 or ms.change_pct < -5:
            status, color = 'WARNING', '#ff8c42'
        elif ms.change_pct < -2:
            status, color = 'ELEVATED', '#fbbf24'
        else:
            status, color = 'STABLE', '#4ade80'
        dominoes.append(DominoStatus(
            id='ms_stock', label='MS Stock',
            status=status, color=color, detail=f'${ms.price:.0f}'
        ))

    # Domino 2: Silver
    silver = prices.get('silver')
    if silver:
        if silver.price > 150:
            status, color = 'EXPLODING', '#ff3b5c'
        elif silver.price > 100:
            status, color = 'SQUEEZING', '#ff8c42'
        elif silver.price > 90:
            status, color = 'RISING', '#fbbf24'
        else:
            status, color = 'STABLE', '#4ade80'
        dominoes.append(DominoStatus(
            id='silver', label='Silver Price',
            status=status, color=color, detail=f'${silver.price:.0f}'
        ))

    # Domino 3: Citi
    citi = prices.get('citigroup')
    if citi:
        if citi.change_pct < -7:
            status, color = 'CRITICAL', '#ff3b5c'
        elif citi.change_pct < -3:
            status, color = 'WARNING', '#ff8c42'
        else:
            status, color = 'STABLE', '#4ade80'
        dominoes.append(DominoStatus(
            id='citi', label='Citigroup',
            status=status, color=color, detail=f'{citi.change_pct:+.1f}%'
        ))

    # Domino 4: Regional Banks
    kre = prices.get('regional_banks')
    if kre:
        if kre.week_change < -10:
            status, color = 'CONTAGION', '#ff3b5c'
        elif kre.week_change < -5:
            status, color = 'STRESS', '#ff8c42'
        else:
            status, color = 'STABLE', '#4ade80'
        dominoes.append(DominoStatus(
            id='regional_banks', label='Regional Banks',
            status=status, color=color, detail=f'{kre.week_change:+.1f}% wk'
        ))

    # Domino 5: VIX
    vix = prices.get('vix')
    if vix:
        if vix.price > 40:
            status, color = 'PANIC', '#ff3b5c'
        elif vix.price > 30:
            status, color = 'FEAR', '#ff8c42'
        elif vix.price > 20:
            status, color = 'ELEVATED', '#fbbf24'
        else:
            status, color = 'CALM', '#4ade80'
        dominoes.append(DominoStatus(
            id='vix', label='VIX',
            status=status, color=color, detail=f'{vix.price:.1f}'
        ))

    return dominoes


def calculate_scenario(silver_price: float) -> ScenarioData:
    """Calculate scenario at a given silver price"""
    ms_loss = MS_SHORT_POSITION_OZ * (silver_price - 30) / 1e9
    citi_loss = CITI_SHORT_POSITION_OZ * (silver_price - 30) / 1e9
    jpm_gain = JPM_LONG_POSITION_OZ * (silver_price - 30) / 1e9
    total_short_loss = ms_loss + citi_loss

    ms_equity_b = 100
    citi_equity_b = 175

    fed_coverage = (FED_REPO_TOTAL / total_short_loss) * 100 if total_short_loss > 0 else 100

    return ScenarioData(
        silver_price=silver_price,
        ms_loss=ms_loss,
        citi_loss=citi_loss,
        jpm_gain=jpm_gain,
        total_short_loss=total_short_loss,
        ms_insolvent=ms_loss > ms_equity_b,
        citi_insolvent=citi_loss > citi_equity_b,
        fed_coverage_pct=fed_coverage
    )


# =============================================================================
# CONTENT GENERATION
# =============================================================================

# Global instances
content_generator = ContentGenerator()
trigger_manager = TriggerManager(generator=content_generator)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "fault.watch API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard():
    """Get complete dashboard data in a single call"""
    prices = fetch_all_prices()
    stress_level = calculate_stress_level(prices)
    risk_index = calculate_risk_index(prices, stress_level)

    # Determine risk label and color
    if risk_index >= 7:
        risk_label, risk_color = 'CRITICAL', '#ff3b5c'
    elif risk_index >= 5:
        risk_label, risk_color = 'ELEVATED', '#ff8c42'
    else:
        risk_label, risk_color = 'STABLE', '#4ade80'

    return DashboardData(
        risk_index=round(risk_index, 1),
        risk_label=risk_label,
        risk_color=risk_color,
        prices={k: v for k, v in prices.items()},
        countdowns={
            'sec': calculate_countdown(SEC_DEADLINE, "SEC Deadline"),
            'lloyds': calculate_countdown(LLOYDS_DEADLINE, "Lloyd's Deadline"),
        },
        alerts=generate_alerts(prices, stress_level),
        dominoes=calculate_domino_status(prices),
        stress_level=stress_level,
        last_updated=datetime.now().isoformat()
    )


@app.get("/api/prices")
async def get_prices():
    """Get current prices for all tracked assets"""
    return fetch_all_prices()


@app.get("/api/prices/{asset}")
async def get_price(asset: str):
    """Get price for a specific asset"""
    prices = fetch_all_prices()
    if asset not in prices:
        raise HTTPException(status_code=404, detail=f"Asset '{asset}' not found")
    return {asset: prices[asset]}


@app.get("/api/countdowns")
async def get_countdowns():
    """Get all deadline countdowns"""
    return {
        'sec': calculate_countdown(SEC_DEADLINE, "SEC Deadline"),
        'lloyds': calculate_countdown(LLOYDS_DEADLINE, "Lloyd's Deadline"),
    }


@app.get("/api/alerts")
async def get_alerts():
    """Get current alerts"""
    prices = fetch_all_prices()
    stress_level = calculate_stress_level(prices)
    return generate_alerts(prices, stress_level)


@app.get("/api/banks")
async def get_banks():
    """Get all bank exposure data"""
    prices = fetch_all_prices()
    silver_price = prices.get('silver', PriceData(price=30)).price

    banks = []
    for key, bank_data in BANK_PM_EXPOSURE.items():
        ticker_map = {
            'JPM': 'jpmorgan', 'C': 'citigroup', 'BAC': 'bank_of_america',
            'GS': 'goldman', 'MS': 'morgan_stanley', 'HSBC': 'hsbc',
            'DB': 'deutsche_bank', 'UBS': 'ubs', 'BCS': 'barclays', 'BNS': 'scotiabank'
        }
        price_key = ticker_map.get(key, key.lower())
        price_data = prices.get(price_key)

        exposure = calculate_bank_exposure(key, silver_price) if key in BANK_SHORT_POSITIONS else {}

        banks.append(BankExposure(
            name=bank_data['name'],
            ticker=bank_data['ticker'],
            position=BANK_SHORT_POSITIONS.get(key, {}).get('position'),
            ounces=BANK_SHORT_POSITIONS.get(key, {}).get('ounces'),
            equity=bank_data['equity'],
            pm_derivatives=bank_data.get('pm_derivatives'),
            pct_total=bank_data.get('pct_total'),
            insolvency_price=BANK_SHORT_POSITIONS.get(key, {}).get('insolvency_price'),
            note=bank_data.get('note'),
            current_price=price_data.price if price_data else None,
            daily_change=price_data.change_pct if price_data else None,
            weekly_change=price_data.week_change if price_data else None,
            paper_loss=exposure.get('paper_loss'),
        ))

    return banks


@app.get("/api/banks/{ticker}")
async def get_bank(ticker: str):
    """Get detailed data for a specific bank"""
    ticker = ticker.upper()
    if ticker not in BANK_PM_EXPOSURE:
        raise HTTPException(status_code=404, detail=f"Bank '{ticker}' not found")

    prices = fetch_all_prices()
    silver_price = prices.get('silver', PriceData(price=30)).price

    bank_data = BANK_PM_EXPOSURE[ticker]
    ticker_map = {
        'JPM': 'jpmorgan', 'C': 'citigroup', 'BAC': 'bank_of_america',
        'GS': 'goldman', 'MS': 'morgan_stanley', 'HSBC': 'hsbc',
        'DB': 'deutsche_bank', 'UBS': 'ubs', 'BCS': 'barclays', 'BNS': 'scotiabank'
    }
    price_key = ticker_map.get(ticker, ticker.lower())
    price_data = prices.get(price_key)

    exposure = calculate_bank_exposure(ticker, silver_price) if ticker in BANK_SHORT_POSITIONS else {}
    short_data = BANK_SHORT_POSITIONS.get(ticker, {})

    return {
        'info': bank_data,
        'short_position': short_data,
        'exposure': exposure,
        'current_price': price_data.price if price_data else None,
        'daily_change': price_data.change_pct if price_data else None,
        'weekly_change': price_data.week_change if price_data else None,
    }


@app.get("/api/scenarios")
async def get_scenarios():
    """Get scenario analysis for multiple silver prices"""
    scenarios = {}
    for price in [50, 75, 100, 125, 150, 200]:
        scenarios[f"silver_{price}"] = calculate_scenario(price)
    return scenarios


@app.get("/api/scenarios/{silver_price}")
async def get_scenario(silver_price: float):
    """Get scenario analysis for a specific silver price"""
    return calculate_scenario(silver_price)


@app.get("/api/dominoes")
async def get_dominoes():
    """Get domino cascade status"""
    prices = fetch_all_prices()
    return calculate_domino_status(prices)


# =============================================================================
# CONTAGION & SYSTEMIC RISK ENDPOINTS
# =============================================================================

@app.get("/api/contagion", response_model=ContagionRiskData)
async def get_contagion_risk():
    """
    Get comprehensive contagion risk data including:
    - Overall contagion score and level
    - Credit stress indicators (TED spread, credit spreads)
    - Liquidity indicators (reverse repo, deposits)
    - Consumer delinquency rates
    - COMEX silver inventory status
    - Sector-by-sector contagion risk
    - Junior silver miner opportunities
    - Current cascade stage (1-5)
    """
    return fetch_contagion_risk()


@app.get("/api/contagion/credit")
async def get_credit_stress():
    """Get credit market stress indicators"""
    return fetch_credit_stress()


@app.get("/api/contagion/liquidity")
async def get_liquidity():
    """Get liquidity crisis indicators"""
    return fetch_liquidity_data()


@app.get("/api/contagion/delinquencies")
async def get_delinquencies():
    """Get consumer credit delinquency rates"""
    return fetch_delinquency_data()


@app.get("/api/contagion/comex")
async def get_comex():
    """Get COMEX silver inventory and delivery data"""
    return fetch_comex_data()


@app.get("/api/contagion/sectors")
async def get_contagion_sectors():
    """Get sector-by-sector contagion risk and investment plays"""
    prices = fetch_all_prices()
    return fetch_contagion_sectors(prices)


@app.get("/api/contagion/sectors/{sector_id}")
async def get_sector_detail(sector_id: str):
    """Get detailed data for a specific sector"""
    if sector_id not in CONTAGION_SECTORS:
        raise HTTPException(status_code=404, detail=f"Sector '{sector_id}' not found")

    sector_info = CONTAGION_SECTORS[sector_id]
    prices = fetch_all_prices()
    sectors = fetch_contagion_sectors(prices)

    sector_data = next((s for s in sectors if s.id == sector_id), None)

    return {
        'info': sector_info,
        'current': sector_data,
        'related_tickers': sector_info.get('plays', [])
    }


@app.get("/api/miners")
async def get_junior_miners():
    """Get junior silver miner data and leverage potential"""
    prices = fetch_all_prices()
    return fetch_junior_miners(prices)


@app.get("/api/miners/{ticker}")
async def get_miner_detail(ticker: str):
    """Get detailed data for a specific junior miner"""
    ticker = ticker.upper()
    if ticker not in JUNIOR_SILVER_MINERS:
        raise HTTPException(status_code=404, detail=f"Miner '{ticker}' not found")

    info = JUNIOR_SILVER_MINERS[ticker]
    quote = fetch_finnhub_quote(ticker) if FINNHUB_API_KEY else None

    return {
        'ticker': ticker,
        'name': info['name'],
        'leverage': info['leverage'],
        'price': quote['price'] if quote else None,
        'change_pct': quote['change_pct'] if quote else None,
        'potential': {
            'medium': '5-10x in silver squeeze',
            'high': '10-20x in silver squeeze',
            'very_high': '20-50x in silver squeeze'
        }.get(info['leverage'])
    }


@app.get("/api/cascade")
async def get_cascade_status():
    """
    Get current domino cascade stage (1-5)

    Stage 1: Silver accumulation - banks stable
    Stage 2: Bank stress emerging - watch MS/Citi
    Stage 3: Credit contagion - regional banks
    Stage 4: Liquidity crisis - broad panic
    Stage 5: Systemic collapse - Fed intervention
    """
    prices = fetch_all_prices()
    credit_stress = fetch_credit_stress()
    stage, description = calculate_cascade_stage(prices, credit_stress)

    return {
        'stage': stage,
        'description': description,
        'stages': {
            1: 'Silver accumulation phase - banks stable',
            2: 'Bank stress emerging - watch MS and Citi closely',
            3: 'Credit contagion spreading to regional banks',
            4: 'Liquidity crisis - broad market panic',
            5: 'SYSTEMIC COLLAPSE - Fed intervention imminent'
        }
    }


@app.get("/api/opportunities")
async def get_investment_opportunities():
    """
    Get categorized investment opportunities for different budgets
    """
    prices = fetch_all_prices()
    miners = fetch_junior_miners(prices)
    sectors = fetch_contagion_sectors(prices)

    # Get current prices for key plays
    plays_under_100 = []
    plays_under_500 = []
    plays_leveraged = []

    # Add junior miners
    for miner in miners:
        if miner.price and miner.price < 20:
            plays_under_100.append({
                'type': 'stock',
                'ticker': miner.ticker,
                'name': miner.name,
                'price': miner.price,
                'thesis': f'Junior silver miner - {miner.potential_multiple} potential',
                'risk': 'very_high'
            })

    # Add inverse ETFs
    inverse_etfs = [
        {'ticker': 'FAZ', 'name': '3x Inverse Financials', 'thesis': 'Profits from bank collapse'},
        {'ticker': 'SRS', 'name': '2x Inverse Real Estate', 'thesis': 'Profits from CRE collapse'},
        {'ticker': 'SQQQ', 'name': '3x Inverse Nasdaq', 'thesis': 'Profits from tech crash'},
    ]

    for etf in inverse_etfs:
        quote = fetch_finnhub_quote(etf['ticker']) if FINNHUB_API_KEY else None
        if quote:
            plays_leveraged.append({
                'type': 'inverse_etf',
                'ticker': etf['ticker'],
                'name': etf['name'],
                'price': quote['price'],
                'thesis': etf['thesis'],
                'risk': 'high'
            })

    # Physical silver
    plays_under_500.append({
        'type': 'physical',
        'ticker': 'SILVER',
        'name': 'Physical Silver (1oz rounds)',
        'price': prices.get('silver', PriceData(price=30)).price,
        'thesis': 'Direct exposure, no counterparty risk',
        'risk': 'medium'
    })

    # PSLV
    pslv_quote = fetch_finnhub_quote('PSLV') if FINNHUB_API_KEY else None
    if pslv_quote:
        plays_under_500.append({
            'type': 'etf',
            'ticker': 'PSLV',
            'name': 'Sprott Physical Silver Trust',
            'price': pslv_quote['price'],
            'thesis': 'Physical silver backed, redeemable',
            'risk': 'medium'
        })

    return {
        'under_100': plays_under_100[:5],
        'under_500': plays_under_500,
        'leveraged': plays_leveraged,
        'sectors_at_risk': [
            {
                'sector': s.name,
                'risk_level': s.risk_level,
                'plays': s.investment_plays
            }
            for s in sectors if s.risk_level in ['high', 'critical']
        ],
        'disclaimer': 'This is not financial advice. High-risk investments can lose 100% of value.'
    }


# =============================================================================
# CONTENT GENERATION ENDPOINTS
# =============================================================================

@app.post("/api/content/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """Generate TikTok content (image or video)"""
    try:
        template_map = {
            'price_alert': TemplateType.PRICE_ALERT,
            'countdown': TemplateType.COUNTDOWN,
            'bank_crisis': TemplateType.BANK_CRISIS,
            'daily_summary': TemplateType.DAILY_SUMMARY,
        }

        template = template_map.get(request.template)
        if not template:
            raise HTTPException(status_code=400, detail=f"Unknown template: {request.template}")

        path = trigger_manager.manual_generate(
            template=template,
            data=request.data,
            generate_video=request.generate_video
        )

        return ContentResponse(
            success=True,
            file_path=str(path),
            file_type='video' if request.generate_video else 'image'
        )
    except Exception as e:
        return ContentResponse(
            success=False,
            file_type='unknown',
            error=str(e)
        )


@app.post("/api/content/generate/daily")
async def generate_daily_summary():
    """Generate daily summary content with current data"""
    prices = fetch_all_prices()
    stress_level = calculate_stress_level(prices)
    risk_index = calculate_risk_index(prices, stress_level)

    data = {
        'silver': prices.get('silver', PriceData(price=0)).price,
        'gold': prices.get('gold', PriceData(price=0)).price,
        'ms': prices.get('morgan_stanley', PriceData(price=0)).price,
        'vix': prices.get('vix', PriceData(price=0)).price,
        'risk': risk_index,
    }

    path = trigger_manager.manual_generate(
        template=TemplateType.DAILY_SUMMARY,
        data=data,
        generate_video=False
    )

    return ContentResponse(
        success=True,
        file_path=str(path),
        file_type='image'
    )


@app.get("/api/content/triggers", response_model=TriggerStatusResponse)
async def get_trigger_status():
    """Get content trigger status"""
    return trigger_manager.get_trigger_status()


@app.post("/api/content/triggers/enable")
async def enable_triggers(enabled: bool = True):
    """Enable or disable auto-triggers"""
    trigger_manager.set_enabled(enabled)
    return {"enabled": enabled}


@app.post("/api/content/triggers/video-mode")
async def set_video_mode(generate_video: bool = False):
    """Set video generation mode"""
    trigger_manager.set_video_mode(generate_video)
    return {"generate_video": generate_video}


@app.get("/api/content/files")
async def get_recent_files(limit: int = 10):
    """Get recently generated content files"""
    files = trigger_manager.get_recent_files(limit)
    return [
        {
            "path": str(f),
            "name": f.name,
            "type": "video" if f.suffix == ".mp4" else "image",
            "exists": f.exists()
        }
        for f in files
    ]


@app.get("/api/content/download/{filename}")
async def download_content(filename: str):
    """Download a generated content file"""
    # Check in images
    image_path = Path("./content-output/images") / filename
    if image_path.exists():
        return FileResponse(image_path, filename=filename)

    # Check in videos
    video_path = Path("./content-output/videos") / filename
    if video_path.exists():
        return FileResponse(video_path, filename=filename)

    raise HTTPException(status_code=404, detail="File not found")


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
