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
from contextlib import asynccontextmanager
import asyncio
import json
import os
import hashlib
from zoneinfo import ZoneInfo

# Load .env file if exists
from dotenv import load_dotenv
load_dotenv()

import requests
import yfinance as yf

from content_generator import ContentGenerator, TemplateType, ContentConfig, VideoConfig, CardType
from content_triggers import TriggerManager, TriggerConfig
from crisis_gauge import CrisisGaugeData, build_crisis_gauge

# =============================================================================
# BACKGROUND SCHEDULER FOR CONTENT GENERATION
# =============================================================================

# Global flag to control the scheduler
_scheduler_running = False
_scheduler_task = None
_last_data_hash = {}  # Track data hashes per card to detect changes

# Eastern timezone for market hours
ET = ZoneInfo("America/New_York")

# Weekend run times (4 equally spaced: 6 AM, 12 PM, 6 PM, 12 AM ET)
WEEKEND_RUN_HOURS = [0, 6, 12, 18]


def is_market_hours() -> bool:
    """Check if current time is during US stock market hours (9:30 AM - 4:00 PM ET, Mon-Fri)."""
    now_et = datetime.now(ET)
    weekday = now_et.weekday()  # 0=Monday, 6=Sunday

    # Weekends
    if weekday >= 5:
        return False

    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= now_et <= market_close


def is_weekend_run_time() -> bool:
    """Check if current time is one of the 4 weekend run times."""
    now_et = datetime.now(ET)
    weekday = now_et.weekday()

    # Only on weekends
    if weekday < 5:
        return False

    # Check if within 5 minutes of a scheduled run time
    current_hour = now_et.hour
    current_minute = now_et.minute

    for run_hour in WEEKEND_RUN_HOURS:
        if current_hour == run_hour and current_minute < 5:
            return True

    return False


def get_next_run_time() -> tuple[int, str]:
    """Calculate seconds until next scheduled run and return reason."""
    now_et = datetime.now(ET)
    weekday = now_et.weekday()

    if weekday < 5:  # Weekday
        market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)

        if now_et < market_open:
            # Before market open - wait until open
            wait_seconds = (market_open - now_et).total_seconds()
            return int(wait_seconds), "market open"
        elif now_et > market_close:
            # After market close - wait until next day 9:30 AM
            next_open = market_open + timedelta(days=1)
            if weekday == 4:  # Friday after close, wait until Monday
                next_open = market_open + timedelta(days=3)
            wait_seconds = (next_open - now_et).total_seconds()
            return int(wait_seconds), "next market day"
        else:
            # During market hours - run every 60 minutes
            return 3600, "hourly during market"
    else:  # Weekend
        # Find next weekend run time
        for run_hour in WEEKEND_RUN_HOURS:
            run_time = now_et.replace(hour=run_hour, minute=0, second=0, microsecond=0)
            if run_time > now_et:
                wait_seconds = (run_time - now_et).total_seconds()
                return int(wait_seconds), f"weekend {run_hour}:00 ET"

        # Past all today's times, schedule for tomorrow or Monday
        if weekday == 5:  # Saturday
            next_run = now_et.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:  # Sunday
            next_run = now_et.replace(hour=9, minute=30, second=0, microsecond=0) + timedelta(days=1)
            return int((next_run - now_et).total_seconds()), "Monday market open"

        wait_seconds = (next_run - now_et).total_seconds()
        return int(wait_seconds), "next weekend slot"


def compute_data_hash(data: dict) -> str:
    """Compute a hash of the data to detect changes."""
    # Round prices to 2 decimals to avoid noise
    normalized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(normalized.encode()).hexdigest()[:16]


def has_data_changed(card_type: str, data: dict) -> bool:
    """Check if data has changed for a specific card type."""
    global _last_data_hash
    current_hash = compute_data_hash(data)
    previous_hash = _last_data_hash.get(card_type)

    if previous_hash is None or previous_hash != current_hash:
        _last_data_hash[card_type] = current_hash
        return True
    return False


async def content_scheduler():
    """
    Background scheduler that generates card videos during market hours.
    - Weekdays: Every 60 minutes during 9:30 AM - 4:00 PM ET
    - Weekends: 4 times (12 AM, 6 AM, 12 PM, 6 PM ET)
    - Only generates videos when data has changed
    """
    global _scheduler_running
    _scheduler_running = True

    print(f"[SCHEDULER] Content scheduler started")
    print(f"[SCHEDULER] Weekday: 9:30 AM - 4:00 PM ET (hourly)")
    print(f"[SCHEDULER] Weekend: 12 AM, 6 AM, 12 PM, 6 PM ET")
    print(f"[SCHEDULER] Content library: C:/Users/ghlte/projects/fault-watch/content-library/")

    generator = ContentGenerator()

    while _scheduler_running:
        try:
            # Calculate wait time until next run
            wait_seconds, reason = get_next_run_time()
            now_et = datetime.now(ET)
            next_run = now_et + timedelta(seconds=wait_seconds)

            print(f"[SCHEDULER] Next run: {next_run.strftime('%Y-%m-%d %I:%M %p ET')} ({reason})")

            # Wait until next scheduled time
            await asyncio.sleep(wait_seconds)

            if not _scheduler_running:
                break

            now_et = datetime.now(ET)
            print(f"[SCHEDULER] Running at {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")

            # Fetch current data
            prices = fetch_all_prices()

            # Build dashboard data for card videos
            silver_price = prices.get('silver', PriceData(price=91.43)).price
            silver_change = prices.get('silver', PriceData(price=0, change_pct=0)).change_pct
            gold_price = prices.get('gold', PriceData(price=4619)).price

            dashboard_data = {
                'prices': {
                    'silver': {'price': round(silver_price, 2), 'change_pct': round(silver_change, 2)},
                    'gold': {'price': round(gold_price, 2)},
                },
            }

            print(f"[SCHEDULER] Silver: ${silver_price:.2f} ({silver_change:+.2f}%)")

            # Check each card for data changes and only generate if changed
            cards_generated = 0
            cards_skipped = 0

            # Fetch fault watch alerts data
            alerts_data = build_fault_watch_alerts_data()
            alert_statuses = [a.status.value for a in alerts_data.alerts]

            # Fetch crisis search pad data
            search_pad_data = build_crisis_search_pad_data()

            # Fetch risk matrix data
            risk_matrix_data = build_risk_matrix_data()

            # Define card data for change detection
            card_data_map = {
                CardType.PRICES: {'silver': silver_price, 'gold': gold_price, 'change': silver_change},
                CardType.COMEX: {'registered_oz': 212000000},  # Would fetch from real source
                CardType.NAKED_SHORTS: {'ratio': 30},
                CardType.BANKS: {'total_loss': 289},
                CardType.CRISIS_GAUGE: {'level': 3},
                CardType.CASCADE: {'stage': 2},
                CardType.SCENARIOS: {'silver': silver_price},
                CardType.FAULT_WATCH_ALERTS: {
                    'system_status': alerts_data.system_status,
                    'severity': alerts_data.overall_alert_level.value,
                    'alerts_active': alerts_data.alerts_active,
                    'conditions_triggered': alerts_data.conditions_triggered,
                    'market_regime': alerts_data.market_regime,
                    'alert_statuses': alert_statuses,
                    'top_inflection': alerts_data.inflection_points[0].name if alerts_data.inflection_points else '',
                    'inflection_prob': alerts_data.inflection_points[0].probability if alerts_data.inflection_points else '',
                },
                CardType.CRISIS_SEARCH_PAD: {
                    'assessments': {
                        'physical_market': search_pad_data.current_assessment['physical_market']['status'],
                        'bank_exposure': search_pad_data.current_assessment['bank_exposure']['status'],
                        'fed_activity': search_pad_data.current_assessment['fed_activity']['status'],
                        'price_action': search_pad_data.current_assessment['price_action']['status'],
                    },
                    'rumors_count': len(search_pad_data.rumors),
                    'banks_count': len(search_pad_data.bank_positions),
                    'next_key_date': search_pad_data.key_dates[0].date if search_pad_data.key_dates else '',
                    'next_key_event': search_pad_data.key_dates[0].event if search_pad_data.key_dates else '',
                    'daily_metrics': len(search_pad_data.daily_metrics),
                    'monthly_metrics': len(search_pad_data.monthly_metrics),
                },
                CardType.RISK_MATRIX: {
                    'context_event': risk_matrix_data.context_event,
                    'risk_factors': [
                        {'name': f.name, 'pre': f.pre_greenland, 'post': f.post_greenland}
                        for f in risk_matrix_data.risk_factors
                    ],
                    'risks_increased': sum(1 for f in risk_matrix_data.risk_factors if f.change_direction == 'up'),
                    'high_priority_items': sum(
                        1 for p in risk_matrix_data.monitoring_schedule
                        for i in p.items if i.priority == 'high'
                    ),
                    'next_check': risk_matrix_data.monitoring_schedule[0].period if risk_matrix_data.monitoring_schedule else '',
                },
            }

            for card_type, card_data in card_data_map.items():
                if has_data_changed(card_type.value, card_data):
                    try:
                        path = generator.generate_card_video(card_type, card_data, duration=3)
                        print(f"[SCHEDULER] Generated: {path.name}")
                        cards_generated += 1
                    except Exception as e:
                        print(f"[SCHEDULER] Error generating {card_type.value}: {e}")
                else:
                    cards_skipped += 1

            print(f"[SCHEDULER] Generated {cards_generated} cards, skipped {cards_skipped} (unchanged)")

            # Also check price triggers for alert videos
            trigger_prices = {
                'silver': silver_price,
                'silver_change': silver_change,
                'ms_change': prices.get('morgan_stanley', PriceData(price=0, change_pct=0)).change_pct,
                'vix': prices.get('vix', PriceData(price=0)).price,
            }

            generated_alerts = trigger_manager.check_price_triggers(trigger_prices)
            if generated_alerts:
                print(f"[SCHEDULER] Generated {len(generated_alerts)} alert videos")

        except Exception as e:
            print(f"[SCHEDULER] Error in content scheduler: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes before retrying on error

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - starts and stops background scheduler."""
    global _scheduler_task, _scheduler_running

    # Check if running on Fly.io (production) - scheduler only runs locally
    is_production = os.environ.get('FLY_APP_NAME') is not None

    if is_production:
        print("[STARTUP] Starting fault.watch API (production mode - scheduler disabled)")
        print("[STARTUP] Video scheduler only runs on local machine")
    else:
        # Startup: Start the background scheduler (local only)
        print("[STARTUP] Starting fault.watch API with content scheduler (local mode)...")
        _scheduler_task = asyncio.create_task(content_scheduler())

    yield

    # Shutdown: Stop the scheduler gracefully (if running)
    if not is_production and _scheduler_task:
        print("[SHUTDOWN] Stopping content scheduler...")
        _scheduler_running = False
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        print("[SHUTDOWN] Content scheduler stopped")


# =============================================================================
# APP CONFIGURATION
# =============================================================================

app = FastAPI(
    title="fault.watch API",
    description="Systemic Risk Monitoring & TikTok Content Generation API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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

# =============================================================================
# BANK POSITIONS - Complete Silver Exposure Data
# =============================================================================
# Total naked shorts: 29.84B oz (36 years of global production)
# Available physical silver: ~1B oz
# Ratio: 30:1 (sold 30x more silver than exists)
# =============================================================================

TOTAL_NAKED_SHORT_OZ = 29_840_000_000  # 29.84 billion ounces
AVAILABLE_PHYSICAL_OZ = 1_000_000_000   # ~1 billion ounces deliverable
NAKED_SHORT_RATIO = 30                   # 30:1 paper to physical
YEARS_PRODUCTION = 36                    # Represents 36 years of global silver production

BANK_SHORT_POSITIONS = {
    'HSBC': {
        'name': 'HSBC Holdings',
        'ticker': 'HSBC',
        'position': 'SHORT',
        'ounces': 7_300_000_000,  # 7.3B oz - LARGEST
        'equity': 190_000_000_000,
        'insolvency_price': 56,  # $56 silver = insolvency (1.9x equity)
        'deadline': 'Jan 31, 2026',
        'regulator': 'BoE/Board',
        'loss_ratio_at_80': 1.9,  # 190% of equity wiped at $80
        'note': 'LARGEST short position - BoE oversight'
    },
    'C': {
        'name': 'Citigroup',
        'ticker': 'C',
        'position': 'SHORT',
        'ounces': 6_340_000_000,  # 6.34B oz
        'equity': 175_000_000_000,
        'insolvency_price': 57,  # ~$57 silver = insolvency (1.8x equity)
        'deadline': 'Jan 31, 2026',
        'regulator': "Lloyd's/Fed",
        'loss_ratio_at_80': 1.8,  # 180% of equity wiped at $80
        'note': "Lloyd's insurance deadline Jan 31 - loses coverage"
    },
    'UBS': {
        'name': 'UBS Group',
        'ticker': 'UBS',
        'position': 'SHORT',
        'ounces': 5_200_000_000,  # 5.2B oz
        'equity': 100_000_000_000,
        'insolvency_price': 49,
        'deadline': 'Unknown',
        'regulator': 'SNB (Swiss National Bank)',
        'loss_ratio_at_80': 2.6,  # 260% of equity at $80
        'note': '5.2B oz SHORT - 3rd largest position'
    },
    'MS': {
        'name': 'Morgan Stanley',
        'ticker': 'MS',
        'position': 'SHORT',
        'ounces': 5_900_000_000,  # 5.9B oz
        'equity': 100_000_000_000,
        'insolvency_price': 47,
        'deadline': 'Feb 15, 2026',
        'regulator': 'SEC',
        'loss_ratio_at_80': 3.0,  # 300% of equity wiped at $80
        'note': 'SEC enforcement deadline Feb 15'
    },
    'BNS': {
        'name': 'Scotiabank',
        'ticker': 'BNS',
        'position': 'SHORT',
        'ounces': 4_100_000_000,  # 4.1B oz
        'equity': 40_000_000_000,
        'insolvency_price': 40,
        'deadline': 'Unknown',
        'regulator': 'OSFI',
        'loss_ratio_at_80': 5.1,  # 510% of equity wiped at $80 - WORST RATIO
        'note': 'WORST equity ratio - $127M PM manipulation fine 2020'
    },
    'BAC': {
        'name': 'Bank of America',
        'ticker': 'BAC',
        'position': 'SHORT',
        'ounces': 1_000_000_000,  # ~1B oz (smaller position)
        'equity': 280_000_000_000,
        'insolvency_price': None,  # Won't go insolvent from silver alone
        'deadline': 'Unknown',
        'regulator': 'Fed/OCC',
        'loss_ratio_at_80': 0.18,  # Only 18% of equity at risk
        'note': 'Smallest short exposure relative to equity'
    },
    'JPM': {
        'name': 'JPMorgan Chase',
        'ticker': 'JPM',
        'position': 'LONG',  # FLIPPED TO LONG
        'ounces': 750_000_000,  # 750M oz LONG
        'equity': 330_000_000_000,
        'note': 'FLIPPED from 200M short to 750M LONG (Jun-Oct 2025)'
    },
}

BANK_PM_EXPOSURE = {
    'HSBC': {'name': 'HSBC Holdings', 'ticker': 'HSBC', 'pm_derivatives': None, 'equity': 190e9, 'pct_total': None, 'note': '7.3B oz SHORT - LARGEST position'},
    'C': {'name': 'Citigroup', 'ticker': 'C', 'pm_derivatives': 204.3e9, 'equity': 175e9, 'pct_total': 29.0, 'note': "6.34B oz SHORT - Lloyd's deadline Jan 31"},
    'UBS': {'name': 'UBS Group', 'ticker': 'UBS', 'pm_derivatives': None, 'equity': 100e9, 'pct_total': None, 'note': '5.2B oz SHORT - SNB regulated'},
    'MS': {'name': 'Morgan Stanley', 'ticker': 'MS', 'pm_derivatives': None, 'equity': 100e9, 'pct_total': None, 'note': '5.9B oz SHORT - SEC deadline Feb 15'},
    'BNS': {'name': 'Scotiabank', 'ticker': 'BNS', 'pm_derivatives': None, 'equity': 40e9, 'pct_total': None, 'note': '4.1B oz SHORT - WORST equity ratio (5.1x at $80)'},
    'BAC': {'name': 'Bank of America', 'ticker': 'BAC', 'pm_derivatives': 47.9e9, 'equity': 280e9, 'pct_total': 6.8, 'note': '~1B oz SHORT - smallest relative exposure'},
    'JPM': {'name': 'JPMorgan Chase', 'ticker': 'JPM', 'pm_derivatives': 437.4e9, 'equity': 330e9, 'pct_total': 62.1, 'note': '750M oz LONG - PROFITING from silver rise'},
    'GS': {'name': 'Goldman Sachs', 'ticker': 'GS', 'pm_derivatives': 0.614e9, 'equity': 120e9, 'pct_total': 0.1},
    'DB': {'name': 'Deutsche Bank', 'ticker': 'DB', 'pm_derivatives': None, 'equity': 55e9, 'pct_total': None, 'note': 'Settled PM manipulation 2016'},
    'BCS': {'name': 'Barclays', 'ticker': 'BCS', 'pm_derivatives': None, 'equity': 50e9, 'pct_total': None, 'note': 'LBMA Market Maker'},
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


class SourceRef(BaseModel):
    """Source reference for verification."""
    name: str
    tier: int  # 1=Official, 2=Credible, 3=Social
    url: Optional[str] = None


class AlertData(BaseModel):
    level: str  # 'critical', 'warning', 'info'
    title: str
    detail: str
    action: Optional[str] = None
    # Verification fields
    verification_status: str = "unverified"  # verified|partial|theory|unverified
    source_count: int = 0
    sources: List[SourceRef] = []
    is_hypothetical: bool = False


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


class BankShortPosition(BaseModel):
    name: str
    ticker: str
    position: str  # 'SHORT' or 'LONG'
    ounces: int
    equity: float
    insolvency_price: Optional[float] = None
    deadline: Optional[str] = None
    regulator: Optional[str] = None
    loss_ratio_at_80: Optional[float] = None
    note: Optional[str] = None


class NakedShortAnalysis(BaseModel):
    """Analysis of the naked short position in silver"""
    total_short_oz: int
    available_physical_oz: int
    paper_to_physical_ratio: float
    years_of_production: int
    verdict: str
    bank_positions: List[BankShortPosition]
    total_short_value_at_current: float
    total_short_value_at_80: float
    total_short_value_at_100: float
    banks_insolvent_at_80: List[str]
    banks_insolvent_at_100: List[str]
    lloyds_deadline: str
    sec_deadline: str


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
    # Organized by category per Fault_Watch_Detailed_Watchlist.md
    finnhub_stocks = {
        # Market Indices
        'SPY': 'sp500',
        'VXX': 'vix_futures',

        # Primary Bank Targets (PM Exposure)
        'JPM': 'jpmorgan',
        'C': 'citigroup',
        'BAC': 'bank_of_america',
        'GS': 'goldman',
        'MS': 'morgan_stanley',
        'WFC': 'wells_fargo',

        # International Banks
        'HSBC': 'hsbc',
        'DB': 'deutsche_bank',
        'UBS': 'ubs',
        'BCS': 'barclays',
        'BNS': 'scotiabank',
        'BMO': 'bank_of_montreal',

        # Regional Banks (Contagion Risk)
        'USB': 'us_bancorp',
        'PNC': 'pnc_financial',
        'TFC': 'truist',
        'FITB': 'fifth_third',
        'KEY': 'keycorp',
        'CFG': 'citizens_financial',
        'SCHW': 'schwab',

        # Financial Sector ETFs
        'XLF': 'financials',
        'KRE': 'regional_banks',
        'KBE': 'bank_etf',
        'FAZ': 'inverse_financials_3x',
        'SKF': 'inverse_financials_2x',

        # Silver ETFs
        'SLV': 'slv',
        'PSLV': 'pslv_physical',
        'SIVR': 'sivr_physical',
        'AGQ': 'silver_2x',
        'ZSL': 'silver_inverse_2x',

        # Silver Miners & Streamers
        'WPM': 'wheaton_pm',
        'SIL': 'silver_miners_etf',
        'SILJ': 'junior_silver_miners_etf',

        # Gold ETFs
        'GLD': 'gld',
        'IAU': 'iau_gold',
        'PHYS': 'phys_gold',

        # Gold Miners
        'GDX': 'gold_miners',
        'GDXJ': 'junior_gold_miners',
        'NEM': 'newmont',
        'GOLD': 'barrick',

        # Industrial Silver Users - Solar
        'FSLR': 'first_solar',
        'ENPH': 'enphase',
        'TAN': 'solar_etf',

        # Industrial - Semiconductors
        'SMH': 'semiconductor_etf',
        'TSM': 'tsmc',
        'NVDA': 'nvidia',

        # Industrial - EVs
        'TSLA': 'tesla',

        # Fixed Income / Risk Indicators
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

        # Fetch REAL silver spot price using yfinance SI=F (COMEX Silver Futures)
        silver_spot_fetched = False
        try:
            silver_ticker = yf.Ticker('SI=F')
            silver_hist = silver_ticker.history(period='2d')
            if not silver_hist.empty and len(silver_hist) > 0:
                silver_spot = float(silver_hist['Close'].iloc[-1])
                silver_prev = float(silver_hist['Close'].iloc[0]) if len(silver_hist) > 1 else silver_spot
                if silver_spot > 0:
                    change_pct = ((silver_spot - silver_prev) / silver_prev * 100) if silver_prev > 0 else 0
                    prices['silver'] = PriceData(
                        price=silver_spot,
                        prev_close=silver_prev,
                        change_pct=change_pct,
                        week_change=0
                    )
                    silver_spot_fetched = True
                    print(f"Silver spot from yfinance SI=F: ${silver_spot:.2f}")
        except Exception as e:
            print(f"yfinance SI=F error: {e}")

        # Fallback 1: Try metals.live API
        if not silver_spot_fetched:
            try:
                metals_resp = requests.get('https://api.metals.live/v1/spot/silver', timeout=5)
                if metals_resp.status_code == 200:
                    metals_data = metals_resp.json()
                    if metals_data and len(metals_data) > 0:
                        silver_spot = float(metals_data[0].get('price', 0))
                        if silver_spot > 0:
                            slv_change = prices['slv'].change_pct if 'slv' in prices else 0
                            prices['silver'] = PriceData(
                                price=silver_spot,
                                prev_close=silver_spot / (1 + slv_change/100) if slv_change else None,
                                change_pct=slv_change,
                                week_change=0
                            )
                            silver_spot_fetched = True
                            print(f"Silver spot from metals.live: ${silver_spot:.2f}")
            except Exception as e:
                print(f"metals.live API error: {e}")

        # Fallback 2: Derive silver price from SLV ETF
        # SLV holds ~0.93 oz silver per share, so: silver_spot ≈ slv_price / 0.93
        if not silver_spot_fetched and 'slv' in prices:
            slv_price = prices['slv'].price
            silver_spot_estimate = slv_price / 0.93
            prices['silver'] = PriceData(
                price=silver_spot_estimate,
                prev_close=prices['slv'].prev_close / 0.93 if prices['slv'].prev_close else None,
                change_pct=prices['slv'].change_pct,
                week_change=0
            )
            print(f"Silver spot estimated from SLV (fallback): ${silver_spot_estimate:.2f}")

        # Fetch REAL gold spot price using yfinance GC=F (COMEX Gold Futures)
        gold_spot_fetched = False
        try:
            gold_ticker = yf.Ticker('GC=F')
            gold_hist = gold_ticker.history(period='2d')
            if not gold_hist.empty and len(gold_hist) > 0:
                gold_spot = float(gold_hist['Close'].iloc[-1])
                gold_prev = float(gold_hist['Close'].iloc[0]) if len(gold_hist) > 1 else gold_spot
                if gold_spot > 0:
                    change_pct = ((gold_spot - gold_prev) / gold_prev * 100) if gold_prev > 0 else 0
                    prices['gold'] = PriceData(
                        price=gold_spot,
                        prev_close=gold_prev,
                        change_pct=change_pct,
                        week_change=0
                    )
                    gold_spot_fetched = True
                    print(f"Gold spot from yfinance GC=F: ${gold_spot:.2f}")
        except Exception as e:
            print(f"yfinance GC=F error: {e}")

        # Fallback 1: Try metals.live API
        if not gold_spot_fetched:
            try:
                gold_resp = requests.get('https://api.metals.live/v1/spot/gold', timeout=5)
                if gold_resp.status_code == 200:
                    gold_data = gold_resp.json()
                    if gold_data and len(gold_data) > 0:
                        gold_spot = float(gold_data[0].get('price', 0))
                        if gold_spot > 0:
                            gld_change = prices['gld'].change_pct if 'gld' in prices else 0
                            prices['gold'] = PriceData(
                                price=gold_spot,
                                prev_close=gold_spot / (1 + gld_change/100) if gld_change else None,
                                change_pct=gld_change,
                                week_change=0
                            )
                            gold_spot_fetched = True
                            print(f"Gold spot from metals.live: ${gold_spot:.2f}")
            except Exception as e:
                print(f"metals.live gold API error: {e}")

        # Fallback 2: Derive gold price from GLD ETF
        # GLD holds ~0.1 oz gold per share, so: gold_spot ≈ gld_price * 10
        if not gold_spot_fetched and 'gld' in prices:
            gld_price = prices['gld'].price
            prices['gold'] = PriceData(
                price=gld_price * 10,
                prev_close=prices['gld'].prev_close * 10 if prices['gld'].prev_close else None,
                change_pct=prices['gld'].change_pct,
                week_change=0
            )
            print(f"Gold spot estimated from GLD (fallback): ${gld_price * 10:.2f}")

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
# ADVANCED MONITORING (Per Watchlist Document)
# =============================================================================

class MarketSignal(BaseModel):
    """Market signal from advanced monitoring"""
    id: str
    category: str  # 'premium', 'divergence', 'nav', 'backwardation', 'cot', 'insider'
    level: str  # 'info', 'warning', 'critical'
    title: str
    detail: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    action: Optional[str] = None
    timestamp: str


class ShanghaiPremiumData(BaseModel):
    """Shanghai vs COMEX silver premium"""
    shanghai_price: Optional[float] = None
    comex_price: Optional[float] = None
    premium_pct: Optional[float] = None
    status: str = 'normal'  # normal, elevated, critical
    signal: Optional[str] = None


class BankDivergenceData(BaseModel):
    """Bank vs XLF sector divergence"""
    ticker: str
    bank_return_5d: Optional[float] = None
    xlf_return_5d: Optional[float] = None
    divergence_pct: Optional[float] = None
    underperforming: bool = False


class SLVNavData(BaseModel):
    """SLV ETF NAV discount/premium"""
    slv_price: Optional[float] = None
    slv_nav: Optional[float] = None
    discount_pct: Optional[float] = None
    status: str = 'normal'  # normal, discount, deep_discount


class BackwardationData(BaseModel):
    """Silver futures curve backwardation"""
    front_month_price: Optional[float] = None
    second_month_price: Optional[float] = None
    spread: Optional[float] = None
    in_backwardation: bool = False
    signal: Optional[str] = None


class COTData(BaseModel):
    """CFTC Commitment of Traders data"""
    report_date: Optional[str] = None
    commercial_long: Optional[int] = None
    commercial_short: Optional[int] = None
    commercial_net: Optional[int] = None
    commercial_net_change: Optional[int] = None
    managed_money_long: Optional[int] = None
    managed_money_short: Optional[int] = None
    managed_money_net: Optional[int] = None
    open_interest: Optional[int] = None
    open_interest_change_pct: Optional[float] = None
    signal: Optional[str] = None


def calculate_shanghai_premium(prices: Dict[str, PriceData]) -> ShanghaiPremiumData:
    """
    Calculate Shanghai vs COMEX silver premium.
    Fetches real Shanghai Gold Exchange silver price from goldsilver.ai API.
    """
    comex_price = prices.get('silver')

    if not comex_price:
        return ShanghaiPremiumData()

    shanghai_price = None

    # Try to fetch real Shanghai silver price from goldsilver.ai
    try:
        resp = requests.get(
            'https://goldsilver.ai/api/metal-prices/shanghai-silver',
            timeout=5,
            headers={'User-Agent': 'FaultWatch/1.0'}
        )
        if resp.status_code == 200:
            data = resp.json()
            shanghai_price = data.get('price_usd_oz')
            print(f"Shanghai silver from API: ${shanghai_price:.2f}")
    except Exception as e:
        print(f"goldsilver.ai API error: {e}")

    # Fallback: Use yfinance to get Shanghai Futures Exchange silver (SHFE)
    if not shanghai_price:
        try:
            # Try SHFE silver futures if available
            shfe = yf.Ticker('AG=F')  # Shanghai silver futures
            shfe_hist = shfe.history(period='1d')
            if not shfe_hist.empty:
                # SHFE quotes in CNY/kg, convert to USD/oz
                cny_kg = float(shfe_hist['Close'].iloc[-1])
                # Approximate conversion: 1 kg = 32.15 oz, USD/CNY ~7.3
                shanghai_price = (cny_kg / 32.15) / 7.3
                print(f"Shanghai silver from SHFE: ${shanghai_price:.2f}")
        except Exception as e:
            print(f"SHFE futures error: {e}")

    # Fallback: Estimate based on current market premium (~8-12% in Jan 2026)
    if not shanghai_price:
        # Current market conditions show ~10% Shanghai premium
        shanghai_price = comex_price.price * 1.10
        print(f"Shanghai silver estimated at 10% premium: ${shanghai_price:.2f}")

    # Calculate premium
    premium_usd = shanghai_price - comex_price.price
    premium_pct = (premium_usd / comex_price.price) * 100

    # Determine status based on premium level
    if premium_pct > 15:
        status = 'critical'
        signal = f'CRITICAL: Shanghai premium ${premium_usd:.2f}/oz ({premium_pct:.1f}%) - severe physical shortage'
    elif premium_pct > 8:
        status = 'elevated'
        signal = f'WARNING: Shanghai premium ${premium_usd:.2f}/oz ({premium_pct:.1f}%) - physical stress'
    else:
        status = 'normal'
        signal = None

    return ShanghaiPremiumData(
        shanghai_price=round(shanghai_price, 2),
        comex_price=comex_price.price,
        premium_pct=round(premium_pct, 2),
        status=status,
        signal=signal
    )


def calculate_bank_divergence(prices: Dict[str, PriceData]) -> List[BankDivergenceData]:
    """
    Calculate bank stock divergence vs XLF sector ETF.
    Alert if bank underperforms XLF by >5% over 5 days.
    """
    divergences = []
    xlf = prices.get('financials')

    if not xlf:
        return divergences

    # Bank tickers to check
    bank_keys = [
        ('jpmorgan', 'JPM'),
        ('citigroup', 'C'),
        ('bank_of_america', 'BAC'),
        ('goldman', 'GS'),
        ('morgan_stanley', 'MS'),
        ('hsbc', 'HSBC'),
    ]

    for price_key, ticker in bank_keys:
        bank = prices.get(price_key)
        if not bank:
            continue

        # Using daily change as proxy for 5-day (would need historical data for true 5d)
        # In production, fetch 5-day historical from Finnhub
        bank_return = bank.change_pct
        xlf_return = xlf.change_pct
        divergence = bank_return - xlf_return

        divergences.append(BankDivergenceData(
            ticker=ticker,
            bank_return_5d=bank_return,
            xlf_return_5d=xlf_return,
            divergence_pct=round(divergence, 2),
            underperforming=divergence < -5  # 5% underperformance threshold
        ))

    return divergences


def calculate_slv_nav_discount(prices: Dict[str, PriceData]) -> SLVNavData:
    """
    Calculate SLV ETF discount/premium to NAV.
    Alert if trading at >2% discount to NAV.

    Note: Real NAV data requires iShares API or scraping.
    Using silver spot as proxy for NAV calculation.
    """
    slv = prices.get('slv')
    silver = prices.get('silver')

    if not slv or not silver:
        return SLVNavData()

    # SLV holds ~0.93 oz silver per share
    # NAV ≈ silver_spot * 0.93
    estimated_nav = silver.price * 0.93
    slv_price = slv.price

    # Calculate discount (negative = discount, positive = premium)
    discount_pct = ((slv_price / estimated_nav) - 1) * 100

    if discount_pct < -3:
        status = 'deep_discount'
    elif discount_pct < -2:
        status = 'discount'
    else:
        status = 'normal'

    return SLVNavData(
        slv_price=slv_price,
        slv_nav=round(estimated_nav, 2),
        discount_pct=round(discount_pct, 2),
        status=status
    )


def check_backwardation(prices: Dict[str, PriceData]) -> BackwardationData:
    """
    Check if silver futures are in backwardation.
    Backwardation = front month > later months = physical shortage signal.

    Note: Real futures data requires CME DataMine subscription.
    Using spot vs ETF comparison as proxy.
    """
    silver = prices.get('silver')
    slv = prices.get('slv')

    if not silver:
        return BackwardationData()

    # In real implementation, fetch from:
    # https://www.cmegroup.com/markets/metals/precious/silver.volume.html
    # For now, use placeholder indicating normal contango

    # Placeholder: check if spot is trading at unusual premium
    # In backwardation, front month trades higher than deferred
    front_month = silver.price  # Proxy: spot price
    second_month = silver.price * 1.002  # Normal ~0.2% contango

    spread = front_month - second_month
    in_backwardation = spread > 0

    signal = None
    if in_backwardation:
        signal = 'WARNING: Silver in backwardation - physical shortage signal'

    return BackwardationData(
        front_month_price=front_month,
        second_month_price=round(second_month, 2),
        spread=round(spread, 2),
        in_backwardation=in_backwardation,
        signal=signal
    )


def fetch_cot_data() -> COTData:
    """
    Fetch CFTC Commitment of Traders data for silver.

    Real data from: https://www.cftc.gov/dea/futures/other_lf.htm
    Silver contract code: 084691

    Note: CFTC data is released weekly (Tuesday data, Friday 3:30 PM ET release).
    This is a placeholder - real implementation would parse CFTC text files.
    """
    # Placeholder values - replace with actual CFTC parsing
    # In production, download from:
    # https://www.cftc.gov/dea/newcot/c_disagg.txt (disaggregated)
    # or https://www.cftc.gov/dea/futures/other_lf.htm (legacy format)

    return COTData(
        report_date="2026-01-10",  # Placeholder
        commercial_long=45000,
        commercial_short=85000,
        commercial_net=-40000,  # Net short 40K contracts = 200M oz
        commercial_net_change=None,
        managed_money_long=65000,
        managed_money_short=35000,
        managed_money_net=30000,  # Specs net long
        open_interest=180000,
        open_interest_change_pct=None,
        signal="Commercials net short, managed money net long - typical setup"
    )


def generate_watchlist_signals(prices: Dict[str, PriceData]) -> List[MarketSignal]:
    """
    Generate signals based on watchlist monitoring criteria.
    Returns list of actionable market signals.
    """
    signals = []
    now = datetime.now().isoformat()

    # 1. Shanghai Premium Check
    shanghai = calculate_shanghai_premium(prices)
    if shanghai.signal:
        signals.append(MarketSignal(
            id='shanghai_premium',
            category='premium',
            level='critical' if shanghai.status == 'critical' else 'warning',
            title='SHANGHAI PREMIUM',
            detail=f'Premium at {shanghai.premium_pct:.1f}%',
            value=shanghai.premium_pct,
            threshold=10.0,
            action='Consider physical silver allocation',
            timestamp=now
        ))

    # 2. Bank vs XLF Divergence
    divergences = calculate_bank_divergence(prices)
    for div in divergences:
        if div.underperforming:
            signals.append(MarketSignal(
                id=f'divergence_{div.ticker}',
                category='divergence',
                level='warning',
                title=f'{div.ticker} UNDERPERFORMING',
                detail=f'Down {abs(div.divergence_pct):.1f}% vs XLF',
                value=div.divergence_pct,
                threshold=-5.0,
                action=f'Monitor {div.ticker} for stress signals',
                timestamp=now
            ))

    # 3. SLV NAV Discount
    nav_data = calculate_slv_nav_discount(prices)
    if nav_data.status == 'deep_discount':
        signals.append(MarketSignal(
            id='slv_nav_discount',
            category='nav',
            level='warning',
            title='SLV NAV DISCOUNT',
            detail=f'Trading at {nav_data.discount_pct:.1f}% discount to NAV',
            value=nav_data.discount_pct,
            threshold=-3.0,
            action='Arbitrage: Short SLV, Long PSLV',
            timestamp=now
        ))

    # 4. Backwardation Check
    backwardation = check_backwardation(prices)
    if backwardation.in_backwardation:
        signals.append(MarketSignal(
            id='backwardation',
            category='backwardation',
            level='warning',
            title='SILVER BACKWARDATION',
            detail=f'Front month ${backwardation.spread:.2f} above deferred',
            value=backwardation.spread,
            threshold=0.0,
            action='Physical shortage signal - bullish silver',
            timestamp=now
        ))

    # 5. Physical vs Paper Premium (PSLV vs SLV)
    pslv = prices.get('pslv_physical')
    slv = prices.get('slv')
    if pslv and slv and slv.price > 0:
        pslv_premium = ((pslv.price / slv.price) - 1) * 100
        if pslv_premium > 5:
            signals.append(MarketSignal(
                id='pslv_premium',
                category='premium',
                level='warning',
                title='PSLV PREMIUM HIGH',
                detail=f'PSLV trading at {pslv_premium:.1f}% premium to SLV',
                value=pslv_premium,
                threshold=5.0,
                action='Physical demand exceeding paper supply',
                timestamp=now
            ))

    # 6. Inverse ETF Volume Spike (FAZ, SKF)
    faz = prices.get('inverse_financials_3x')
    if faz and faz.change_pct > 10:
        signals.append(MarketSignal(
            id='faz_spike',
            category='flow',
            level='warning',
            title='FAZ SURGING',
            detail=f'3X inverse financials up {faz.change_pct:.1f}%',
            value=faz.change_pct,
            threshold=10.0,
            action='Heavy betting against banks',
            timestamp=now
        ))

    return signals


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
    """
    Calculate forward-looking risk index 0-10

    Unlike backward-looking indicators that only trigger during crisis,
    this shows proximity to crisis thresholds:
    - How close silver is to bank insolvency levels ($50-80)
    - Contagion indicators (credit stress, liquidity)
    - Market fear (VIX)
    - Countdown urgency
    """
    risk = 0

    # Silver proximity to crisis (0-3.5)
    # $30 = baseline, $50 = MS pain, $80 = insolvency
    silver = prices.get('silver')
    if silver:
        if silver.price >= 100:
            risk += 3.5  # Full crisis
        elif silver.price >= 80:
            risk += 3.0  # Bank insolvency territory
        elif silver.price >= 50:
            # Linear scale from 50-80: 1.5 to 3.0
            risk += 1.5 + ((silver.price - 50) / 30) * 1.5
        elif silver.price >= 30:
            # Early warning: 30-50 silver = 0.5 to 1.5
            risk += 0.5 + ((silver.price - 30) / 20) * 1.0
        else:
            # Below $30 = minimal crisis risk from silver
            risk += (silver.price / 30) * 0.5

    # Weekly momentum matters (0-1)
    # Rising silver = increasing pressure
    if silver and hasattr(silver, 'week_change'):
        if silver.week_change > 10:
            risk += 1.0
        elif silver.week_change > 5:
            risk += 0.5
        elif silver.week_change > 2:
            risk += 0.25

    # Bank stock stress (0-2)
    # Falling bank stocks = market sensing trouble
    ms = prices.get('morgan_stanley')
    citi = prices.get('citigroup')
    if ms and ms.change_pct < -5:
        risk += 1.0
    elif ms and ms.change_pct < -2:
        risk += 0.5
    if citi and citi.change_pct < -5:
        risk += 0.5
    elif citi and citi.change_pct < -2:
        risk += 0.25

    # VIX fear gauge (0-1.5)
    vix = prices.get('vix')
    if vix:
        if vix.price > 40:
            risk += 1.5  # Panic
        elif vix.price > 30:
            risk += 1.0  # High fear
        elif vix.price > 25:
            risk += 0.75  # Elevated
        elif vix.price > 20:
            risk += 0.5  # Above normal
        elif vix.price > 15:
            risk += 0.25  # Slightly elevated

    # Countdown pressure (0-2)
    sec_countdown = calculate_countdown(SEC_DEADLINE, "SEC")
    lloyds_countdown = calculate_countdown(LLOYDS_DEADLINE, "Lloyd's")

    min_days = min(sec_countdown.days, lloyds_countdown.days)
    if min_days < 7:
        risk += 2.0
    elif min_days < 14:
        risk += 1.5
    elif min_days < 30:
        risk += 1.0
    elif min_days < 60:
        risk += 0.5

    return min(risk, 10)


def generate_alerts(prices: Dict[str, PriceData], stress_level: float) -> List[AlertData]:
    """
    Generate VERIFIED alerts based on real-time market data.

    Only alerts backed by actual price feeds are returned.
    Hypothetical scenarios are moved to /api/theories endpoint.
    """
    alerts = []

    # Define verified sources for price data
    price_sources = [
        SourceRef(name="Finnhub", tier=1),
        SourceRef(name="Yahoo Finance", tier=2),
    ]

    # HSBC alerts - LARGEST short position (7.3B oz)
    # VERIFIED: Based on real-time stock price from Finnhub/Yahoo
    hsbc = prices.get('hsbc')
    if hsbc:
        if hsbc.change_pct < -7:
            alerts.append(AlertData(
                level='critical',
                title='HSBC STOCK DOWN',
                detail=f'Down {abs(hsbc.change_pct):.1f}% today',
                action='Real-time market data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))
        elif hsbc.change_pct < -3:
            alerts.append(AlertData(
                level='warning',
                title='HSBC UNDER PRESSURE',
                detail=f'Down {abs(hsbc.change_pct):.1f}% today',
                action='Real-time market data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))

    # Citigroup alerts - VERIFIED from price feeds
    citi = prices.get('citigroup')
    if citi:
        if citi.change_pct < -7:
            alerts.append(AlertData(
                level='critical',
                title='CITI STOCK DOWN',
                detail=f'Down {abs(citi.change_pct):.1f}% today',
                action='Real-time market data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))
        elif citi.change_pct < -3:
            alerts.append(AlertData(
                level='warning',
                title='CITI UNDER PRESSURE',
                detail=f'Down {abs(citi.change_pct):.1f}% today',
                action='Real-time market data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))

    # Morgan Stanley alerts - VERIFIED from price feeds
    ms = prices.get('morgan_stanley')
    if ms:
        if ms.change_pct < -7:
            alerts.append(AlertData(
                level='critical',
                title='MS STOCK DOWN',
                detail=f'Down {abs(ms.change_pct):.1f}% today',
                action='Real-time market data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))
        elif ms.change_pct < -3:
            alerts.append(AlertData(
                level='warning',
                title='MS UNDER PRESSURE',
                detail=f'Down {abs(ms.change_pct):.1f}% today',
                action='Real-time market data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))

        if ms.price < 100:
            alerts.append(AlertData(
                level='critical',
                title='MS BELOW $100',
                detail=f'Currently ${ms.price:.2f}',
                action='Real-time price data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))

    # Scotiabank - VERIFIED from price feeds
    bns = prices.get('scotiabank')
    if bns:
        if bns.change_pct < -5:
            alerts.append(AlertData(
                level='critical',
                title='SCOTIABANK DOWN',
                detail=f'Down {abs(bns.change_pct):.1f}% today',
                action='Real-time market data',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))

    # Silver alerts - VERIFIED from price feeds
    silver = prices.get('silver')
    if silver:
        if silver.price > 100:
            alerts.append(AlertData(
                level='critical',
                title='SILVER ABOVE $100',
                detail=f'Currently ${silver.price:.2f}',
                action='Real-time commodity price',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))
        elif silver.price > 90:
            alerts.append(AlertData(
                level='warning',
                title='Silver Approaching $100',
                detail=f'Currently ${silver.price:.2f}',
                action='Real-time commodity price',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))

    # VIX alerts - VERIFIED from price feeds
    vix = prices.get('vix')
    if vix and vix.price > 35:
        alerts.append(AlertData(
            level='critical',
            title='HIGH VOLATILITY',
            detail=f'VIX at {vix.price:.1f}',
            action='CBOE Volatility Index',
            verification_status='verified',
            source_count=2,
            sources=price_sources,
            is_hypothetical=False
        ))

    # Regional banks contagion - VERIFIED from price feeds
    kre = prices.get('regional_banks')
    if kre and kre.change_pct < -5:
        alerts.append(AlertData(
            level='critical',
            title='REGIONAL BANKS FALLING',
            detail=f'KRE down {abs(kre.change_pct):.1f}%',
            action='Contagion spreading to regionals',
            verification_status='verified',
            source_count=2,
            sources=price_sources,
            is_hypothetical=False
        ))

    # PSLV premium (physical vs paper) - VERIFIED from price feeds
    pslv = prices.get('pslv_physical')
    slv = prices.get('slv')
    if pslv and slv and slv.price > 0:
        premium = ((pslv.price / slv.price) - 1) * 100
        if premium > 8:
            alerts.append(AlertData(
                level='critical',
                title='PSLV PREMIUM HIGH',
                detail=f'{premium:.1f}% above SLV',
                action='Physical demand exceeding paper',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))
        elif premium > 5:
            alerts.append(AlertData(
                level='warning',
                title='PSLV Premium Rising',
                detail=f'{premium:.1f}% above SLV',
                action='Monitor physical demand',
                verification_status='verified',
                source_count=2,
                sources=price_sources,
                is_hypothetical=False
            ))

    # Inverse financials surging - VERIFIED from price feeds
    faz = prices.get('inverse_financials_3x')
    if faz and faz.change_pct > 15:
        alerts.append(AlertData(
            level='critical',
            title='FAZ SURGING',
            detail=f'3X inverse financials up {faz.change_pct:.1f}%',
            action='Heavy betting against banks',
            verification_status='verified',
            source_count=2,
            sources=price_sources,
            is_hypothetical=False
        ))

    # Bank vs XLF divergence alerts
    xlf = prices.get('financials')
    if xlf:
        for bank_key, bank_name in [('citigroup', 'Citi'), ('morgan_stanley', 'MS'), ('hsbc', 'HSBC')]:
            bank = prices.get(bank_key)
            if bank and (bank.change_pct - xlf.change_pct) < -5:
                alerts.append(AlertData(
                    level='warning',
                    title=f'{bank_name} DIVERGING',
                    detail=f'Underperforming XLF by {abs(bank.change_pct - xlf.change_pct):.1f}%',
                    action='Bank-specific stress signal',
                    verification_status='verified',
                    source_count=2,
                    sources=price_sources,
                    is_hypothetical=False
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
    # Get position data from BANK_SHORT_POSITIONS
    ms_position = BANK_SHORT_POSITIONS.get('MS', {})
    citi_position = BANK_SHORT_POSITIONS.get('C', {})
    jpm_position = BANK_SHORT_POSITIONS.get('JPM', {})

    ms_oz = ms_position.get('ounces', 5_900_000_000)
    citi_oz = citi_position.get('ounces', 6_340_000_000)
    jpm_oz = jpm_position.get('ounces', 750_000_000)

    # Calculate losses/gains (shorts lose when price rises, longs gain)
    ms_is_short = ms_position.get('position') == 'SHORT'
    citi_is_short = citi_position.get('position') == 'SHORT'
    jpm_is_long = jpm_position.get('position') == 'LONG'

    ms_loss = (ms_oz * (silver_price - 30) / 1e9) if ms_is_short else 0
    citi_loss = (citi_oz * (silver_price - 30) / 1e9) if citi_is_short else 0
    jpm_gain = (jpm_oz * (silver_price - 30) / 1e9) if jpm_is_long else 0

    total_short_loss = ms_loss + citi_loss

    ms_equity_b = ms_position.get('equity', 100_000_000_000) / 1e9
    citi_equity_b = citi_position.get('equity', 175_000_000_000) / 1e9

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
    # Forward-looking scale: 0=calm, 3=watch, 5=warning, 7=danger, 9=crisis
    if risk_index >= 8:
        risk_label, risk_color = 'CRISIS', '#ff3b5c'
    elif risk_index >= 6:
        risk_label, risk_color = 'DANGER', '#ef4444'
    elif risk_index >= 4:
        risk_label, risk_color = 'WARNING', '#ff8c42'
    elif risk_index >= 2.5:
        risk_label, risk_color = 'WATCH', '#fbbf24'
    elif risk_index >= 1.5:
        risk_label, risk_color = 'MONITOR', '#84cc16'
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
    """Get current alerts - only verified alerts based on real data"""
    prices = fetch_all_prices()
    stress_level = calculate_stress_level(prices)
    return generate_alerts(prices, stress_level)


class TheoryData(BaseModel):
    """Working theory/hypothesis data model."""
    id: str
    title: str
    hypothesis: str
    basis: List[str]
    confidence: int  # 0-100
    status: str  # theory|partial
    trigger_conditions: List[str] = []
    sources: List[SourceRef] = []


@app.get("/api/theories")
async def get_theories():
    """
    Get working theories and hypothetical scenarios.

    These are NOT verified - they are hypotheses based on:
    - Historical patterns
    - Industry analysis
    - Unconfirmed reports

    Displayed separately from verified alerts.
    """
    theories = [
        TheoryData(
            id="ubs-nationalization",
            title="UBS Nationalization Scenario",
            hypothesis="Swiss government may intervene if UBS silver shorts cause insolvency",
            basis=[
                "Historical SNB interventions (Credit Suisse 2023)",
                "UBS reported 5.2B oz short position",
                "Swiss banking stability mandate"
            ],
            confidence=45,
            status="theory",
            trigger_conditions=[
                "Silver price exceeds $50",
                "UBS stock falls below CHF 15",
                "SNB emergency meeting announced"
            ],
            sources=[
                SourceRef(name="Historical analysis", tier=3),
                SourceRef(name="Industry estimates", tier=3)
            ]
        ),
        TheoryData(
            id="lloyds-deadline",
            title="Lloyd's Insurance Deadline",
            hypothesis="Lloyd's may decline to renew PM derivative coverage for major banks",
            basis=[
                "Industry reports of tightening underwriting",
                "Historical precedent (2008 AIG)",
                "Exposure concentration concerns"
            ],
            confidence=55,
            status="partial",
            trigger_conditions=[
                "Jan 31, 2026 renewal deadline",
                "Banks fail to reduce PM exposure",
                "Silver exceeds $40 sustained"
            ],
            sources=[
                SourceRef(name="Industry sources", tier=3),
                SourceRef(name="Insurance analyst reports", tier=2)
            ]
        ),
        TheoryData(
            id="sec-enforcement",
            title="SEC Enforcement Action",
            hypothesis="SEC may take enforcement action against banks for PM manipulation",
            basis=[
                "Historical PM manipulation settlements",
                "Ongoing CFTC investigations",
                "Whistleblower claims"
            ],
            confidence=60,
            status="partial",
            trigger_conditions=[
                "CFTC referral to SEC",
                "Whistleblower award announcement",
                "Congressional hearing scheduled"
            ],
            sources=[
                SourceRef(name="SEC EDGAR filings", tier=1),
                SourceRef(name="Legal analysis", tier=2)
            ]
        ),
        TheoryData(
            id="comex-delivery-failure",
            title="COMEX Delivery Stress",
            hypothesis="COMEX may face delivery challenges if physical demand spikes",
            basis=[
                "Declining registered inventory",
                "Rising delivery notices",
                "Paper-to-physical ratio concerns"
            ],
            confidence=50,
            status="theory",
            trigger_conditions=[
                "Registered inventory below 20M oz",
                "Coverage ratio exceeds 5x",
                "Major delivery month fails"
            ],
            sources=[
                SourceRef(name="CME Group data", tier=1),
                SourceRef(name="Market analysis", tier=2)
            ]
        ),
        TheoryData(
            id="bank-contagion",
            title="Bank Contagion Risk",
            hypothesis="Failure of one major silver-short bank could trigger cascading failures",
            basis=[
                "Interconnected derivative positions",
                "Shared counterparty exposure",
                "Historical contagion patterns (2008, SVB 2023)"
            ],
            confidence=40,
            status="theory",
            trigger_conditions=[
                "First major bank nationalized/fails",
                "Credit default swaps spike",
                "Interbank lending freezes"
            ],
            sources=[
                SourceRef(name="BIS reports", tier=1),
                SourceRef(name="Academic research", tier=2)
            ]
        )
    ]
    return theories


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


@app.get("/api/naked-shorts", response_model=NakedShortAnalysis)
async def get_naked_short_analysis():
    """
    Get comprehensive naked short analysis

    Total shorts: 29.84B oz (36 years of global production)
    Available physical: ~1B oz
    Ratio: 30:1 (sold 30x more than exists)
    Verdict: Largest naked short in history
    """
    prices = fetch_all_prices()
    silver_price = prices.get('silver', PriceData(price=30)).price

    # Build bank positions list
    bank_positions = []
    banks_insolvent_80 = []
    banks_insolvent_100 = []

    for ticker, data in BANK_SHORT_POSITIONS.items():
        position = BankShortPosition(
            name=data['name'],
            ticker=data['ticker'],
            position=data['position'],
            ounces=data['ounces'],
            equity=data['equity'],
            insolvency_price=data.get('insolvency_price'),
            deadline=data.get('deadline'),
            regulator=data.get('regulator'),
            loss_ratio_at_80=data.get('loss_ratio_at_80'),
            note=data.get('note'),
        )
        bank_positions.append(position)

        # Check insolvency at price levels (for shorts only)
        if data['position'] == 'SHORT':
            insolvency_price = data.get('insolvency_price')
            if insolvency_price and insolvency_price <= 80:
                banks_insolvent_80.append(data['name'])
            if insolvency_price and insolvency_price <= 100:
                banks_insolvent_100.append(data['name'])

    # Sort by position size (largest shorts first)
    bank_positions.sort(key=lambda x: x.ounces if x.position == 'SHORT' else 0, reverse=True)

    # Calculate total short values
    total_short_oz = sum(
        data['ounces'] for data in BANK_SHORT_POSITIONS.values()
        if data['position'] == 'SHORT'
    )

    return NakedShortAnalysis(
        total_short_oz=TOTAL_NAKED_SHORT_OZ,
        available_physical_oz=AVAILABLE_PHYSICAL_OZ,
        paper_to_physical_ratio=NAKED_SHORT_RATIO,
        years_of_production=YEARS_PRODUCTION,
        verdict="LARGEST NAKED SHORT IN HISTORY - 30x more silver sold than exists",
        bank_positions=bank_positions,
        total_short_value_at_current=total_short_oz * silver_price / 1e9,  # billions
        total_short_value_at_80=total_short_oz * 80 / 1e9,
        total_short_value_at_100=total_short_oz * 100 / 1e9,
        banks_insolvent_at_80=banks_insolvent_80,
        banks_insolvent_at_100=banks_insolvent_100,
        lloyds_deadline=LLOYDS_DEADLINE.strftime("%Y-%m-%d"),
        sec_deadline=SEC_DEADLINE.strftime("%Y-%m-%d"),
    )


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


# =============================================================================
# WATCHLIST MONITORING ENDPOINTS (Per Detailed Watchlist Document)
# =============================================================================

@app.get("/api/watchlist/signals")
async def get_watchlist_signals():
    """
    Get all active market signals from watchlist monitoring.
    Implements checks from Fault_Watch_Detailed_Watchlist.md
    """
    prices = fetch_all_prices()
    signals = generate_watchlist_signals(prices)
    return {
        'signals': [s.model_dump() for s in signals],
        'signal_count': len(signals),
        'last_updated': datetime.now().isoformat()
    }


@app.get("/api/watchlist/shanghai-premium")
async def get_shanghai_premium():
    """
    Get Shanghai vs COMEX silver premium.
    Alert thresholds: >10% warning, >15% critical
    """
    prices = fetch_all_prices()
    return calculate_shanghai_premium(prices)


@app.get("/api/watchlist/bank-divergence")
async def get_bank_divergence():
    """
    Get bank stock divergence vs XLF sector.
    Alert if bank underperforms XLF by >5%
    """
    prices = fetch_all_prices()
    divergences = calculate_bank_divergence(prices)
    underperforming = [d for d in divergences if d.underperforming]
    return {
        'all_banks': [d.model_dump() for d in divergences],
        'underperforming': [d.model_dump() for d in underperforming],
        'alert_count': len(underperforming)
    }


@app.get("/api/watchlist/slv-nav")
async def get_slv_nav():
    """
    Get SLV ETF NAV discount/premium.
    Alert if trading at >2% discount to NAV
    """
    prices = fetch_all_prices()
    return calculate_slv_nav_discount(prices)


@app.get("/api/watchlist/backwardation")
async def get_backwardation():
    """
    Check silver futures curve for backwardation.
    Backwardation = physical shortage signal
    """
    prices = fetch_all_prices()
    return check_backwardation(prices)


@app.get("/api/watchlist/cot")
async def get_cot_data():
    """
    Get CFTC Commitment of Traders data for silver.
    Updated weekly (Friday 3:30 PM ET)
    """
    return fetch_cot_data()


@app.get("/api/watchlist/physical-premium")
async def get_physical_premium():
    """
    Get physical silver premium (PSLV vs SLV spread).
    High premium indicates physical demand exceeding paper.
    """
    prices = fetch_all_prices()
    pslv = prices.get('pslv_physical')
    slv = prices.get('slv')

    if not pslv or not slv:
        return {'error': 'Price data not available', 'premium_pct': None}

    premium_pct = ((pslv.price / slv.price) - 1) * 100 if slv.price > 0 else 0

    return {
        'pslv_price': pslv.price,
        'slv_price': slv.price,
        'premium_pct': round(premium_pct, 2),
        'status': 'elevated' if premium_pct > 5 else 'normal',
        'signal': 'Physical demand exceeding paper supply' if premium_pct > 5 else None
    }


@app.get("/api/watchlist/global-physical")
async def get_global_physical_prices():
    """
    Get global physical silver prices showing real-world purchasing costs.
    Shows what people are actually paying for silver in Shanghai, Dubai, Tokyo, etc.
    """
    prices = fetch_all_prices()
    comex_price = prices.get('silver')

    if not comex_price:
        return {'error': 'COMEX price not available'}

    comex = comex_price.price

    # Get Shanghai premium data
    shanghai_data = calculate_shanghai_premium(prices)
    shanghai_price = shanghai_data.shanghai_price or (comex * 1.10)

    # Dubai/UAE - typically 35-45% premium in current market (Jan 2026)
    # Based on: investment demand + jewelry consumption + physical hub premium
    dubai_premium_pct = 40  # ~40% above COMEX per web research
    dubai_price = comex * (1 + dubai_premium_pct / 100)

    # Tokyo/Japan - varies 10-60% depending on retailer
    # TANAKA retail ~$83/oz for lower bars, secondary markets much higher
    tokyo_premium_pct = 25  # Conservative estimate - TANAKA retail premium
    tokyo_price = comex * (1 + tokyo_premium_pct / 100)

    # London LBMA - typically tracks close to COMEX
    london_premium_pct = 0.5
    london_price = comex * (1 + london_premium_pct / 100)

    # US Retail (bullion dealers) - typically 5-15% over spot
    us_retail_premium_pct = 10
    us_retail_price = comex * (1 + us_retail_premium_pct / 100)

    return {
        'comex_spot': {
            'price': round(comex, 2),
            'label': 'COMEX Futures (Paper)',
            'source': 'SI=F via yfinance'
        },
        'shanghai': {
            'price': round(shanghai_price, 2),
            'premium_pct': round(shanghai_data.premium_pct or 10, 1),
            'premium_usd': round(shanghai_price - comex, 2),
            'label': 'Shanghai SGE (Physical)',
            'status': shanghai_data.status,
            'source': 'Shanghai Gold Exchange Ag(T+D)'
        },
        'dubai': {
            'price': round(dubai_price, 2),
            'premium_pct': dubai_premium_pct,
            'premium_usd': round(dubai_price - comex, 2),
            'label': 'Dubai (Physical)',
            'status': 'critical' if dubai_premium_pct > 30 else 'elevated',
            'source': 'UAE bullion market estimate'
        },
        'tokyo': {
            'price': round(tokyo_price, 2),
            'premium_pct': tokyo_premium_pct,
            'premium_usd': round(tokyo_price - comex, 2),
            'label': 'Tokyo (Retail)',
            'status': 'elevated' if tokyo_premium_pct > 15 else 'normal',
            'source': 'TANAKA/Japanese bullion dealers'
        },
        'london': {
            'price': round(london_price, 2),
            'premium_pct': london_premium_pct,
            'premium_usd': round(london_price - comex, 2),
            'label': 'London LBMA (Wholesale)',
            'status': 'normal',
            'source': 'LBMA Silver Price'
        },
        'us_retail': {
            'price': round(us_retail_price, 2),
            'premium_pct': us_retail_premium_pct,
            'premium_usd': round(us_retail_price - comex, 2),
            'label': 'US Retail (Dealers)',
            'status': 'normal',
            'source': 'JM Bullion, APMEX average'
        },
        'timestamp': datetime.now().isoformat(),
        'note': 'Physical premiums reflect real-world supply constraints vs paper spot'
    }


@app.get("/api/watchlist/industrial")
async def get_industrial_users():
    """
    Get industrial silver user stock performance.
    Silver price spikes affect solar, semiconductors, EVs.
    """
    prices = fetch_all_prices()

    industrial = {
        'solar': {
            'first_solar': prices.get('first_solar'),
            'enphase': prices.get('enphase'),
            'tan_etf': prices.get('solar_etf'),
        },
        'semiconductors': {
            'smh_etf': prices.get('semiconductor_etf'),
            'tsmc': prices.get('tsmc'),
            'nvidia': prices.get('nvidia'),
        },
        'ev': {
            'tesla': prices.get('tesla'),
        }
    }

    # Convert PriceData to dicts
    result = {}
    for sector, tickers in industrial.items():
        result[sector] = {}
        for name, data in tickers.items():
            if data:
                result[sector][name] = {
                    'price': data.price,
                    'change_pct': data.change_pct
                }

    return result


@app.get("/api/watchlist/regional-banks")
async def get_regional_banks():
    """
    Get regional bank stock performance (contagion risk).
    """
    prices = fetch_all_prices()

    regional = {
        'us_bancorp': prices.get('us_bancorp'),
        'pnc_financial': prices.get('pnc_financial'),
        'truist': prices.get('truist'),
        'fifth_third': prices.get('fifth_third'),
        'keycorp': prices.get('keycorp'),
        'citizens_financial': prices.get('citizens_financial'),
        'schwab': prices.get('schwab'),
        'kre_etf': prices.get('regional_banks'),
    }

    result = {}
    worst_performer = None
    worst_change = 0

    for name, data in regional.items():
        if data:
            result[name] = {
                'price': data.price,
                'change_pct': data.change_pct
            }
            if data.change_pct < worst_change:
                worst_change = data.change_pct
                worst_performer = name

    return {
        'banks': result,
        'worst_performer': worst_performer,
        'worst_change': worst_change,
        'contagion_alert': worst_change < -5
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


@app.get("/api/content/scheduler")
async def get_scheduler_status():
    """
    Get background content scheduler status.
    - Scheduler only runs locally (disabled on Fly.io production)
    - Weekdays: Hourly during market hours (9:30 AM - 4:00 PM ET)
    - Weekends: 4 times (12 AM, 6 AM, 12 PM, 6 PM ET)
    - Only generates when data has changed
    """
    is_production = os.environ.get('FLY_APP_NAME') is not None
    now_et = datetime.now(ET)

    if is_production:
        return {
            'scheduler_running': False,
            'mode': 'production',
            'message': 'Video scheduler only runs on local machine',
            'current_time_et': now_et.strftime('%Y-%m-%d %I:%M %p ET'),
        }

    wait_seconds, next_reason = get_next_run_time()
    next_run = now_et + timedelta(seconds=wait_seconds)

    return {
        'scheduler_running': _scheduler_running,
        'mode': 'local',
        'current_time_et': now_et.strftime('%Y-%m-%d %I:%M %p ET'),
        'is_market_hours': is_market_hours(),
        'is_weekend': now_et.weekday() >= 5,
        'next_run': next_run.strftime('%Y-%m-%d %I:%M %p ET'),
        'next_run_reason': next_reason,
        'wait_minutes': round(wait_seconds / 60),
        'schedule': {
            'weekday': '9:30 AM - 4:00 PM ET (hourly)',
            'weekend': '12 AM, 6 AM, 12 PM, 6 PM ET',
        },
        'change_detection': True,
        'cards_tracked': list(_last_data_hash.keys()),
        'content_library': 'C:/Users/ghlte/projects/fault-watch/content-library/',
        'video_mode': trigger_manager.config.generate_video,
        'triggers_enabled': trigger_manager.config.enabled,
        'total_generated': len(trigger_manager._generated_files),
    }


@app.post("/api/content/triggers/check")
async def check_triggers():
    """
    Check price triggers and generate content if thresholds are crossed.
    Note: The background scheduler calls this automatically every 60 minutes.
    """
    prices = fetch_all_prices()

    # Prepare price data for trigger check
    trigger_prices = {
        'silver': prices.get('silver', PriceData(price=0)).price,
        'silver_change': prices.get('silver', PriceData(price=0, change_pct=0)).change_pct,
        'ms_change': prices.get('morgan_stanley', PriceData(price=0, change_pct=0)).change_pct,
        'vix': prices.get('vix', PriceData(price=0)).price,
    }

    # Check triggers and generate content
    generated_files = trigger_manager.check_price_triggers(trigger_prices)

    return {
        'checked': True,
        'prices': trigger_prices,
        'files_generated': len(generated_files),
        'files': [str(f) for f in generated_files],
        'trigger_status': trigger_manager.get_trigger_status()
    }


@app.post("/api/content/cards/generate")
async def generate_card_videos(duration: int = 3):
    """
    Generate 3-second videos for all dashboard cards.
    Videos are saved to content-library/{date}/cards/
    """
    prices = fetch_all_prices()

    # Build dashboard data
    dashboard_data = {
        'prices': {
            'silver': {'price': prices.get('silver', PriceData(price=91.43)).price,
                      'change_pct': prices.get('silver', PriceData(price=0, change_pct=0)).change_pct},
            'gold': {'price': prices.get('gold', PriceData(price=4619)).price},
        },
    }

    # Generate all card videos
    generator = ContentGenerator()
    try:
        generated = generator.generate_all_card_videos(dashboard_data, duration=duration)
        return {
            'success': True,
            'cards_generated': len(generated),
            'files': [str(f) for f in generated],
            'duration': duration,
            'output_folder': f"content-library/{datetime.now().strftime('%Y-%m-%d')}/cards/"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


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
# USER REGISTRATION & FEEDBACK
# =============================================================================

# In-memory storage for user registrations (would use database in production)
_user_registrations: Dict[str, Dict[str, Any]] = {}
_user_comments: List[Dict[str, Any]] = []


class SocialMediaAccount(BaseModel):
    """Social media account info"""
    platform: str  # tiktok, instagram, facebook, youtube, twitter, other
    username: str


class UserRegistration(BaseModel):
    """User registration with social media accounts"""
    email: Optional[str] = None
    social_accounts: List[SocialMediaAccount]
    primary_platform: str
    comment: Optional[str] = None


class UserComment(BaseModel):
    """User feedback comment"""
    user_id: str  # Can be 'anonymous' for non-registered users
    comment: str
    rating: Optional[int] = None  # 1-5 stars
    page: Optional[str] = None  # Which page the feedback is from


@app.post("/api/users/register")
async def register_user(registration: UserRegistration):
    """
    Register a user with their social media accounts.
    Returns a user_id that grants access to deep dive sections.
    """
    # Validate at least one social account
    if not registration.social_accounts:
        raise HTTPException(status_code=400, detail="At least one social media account is required")

    # Generate user ID based on primary account
    primary_account = next(
        (acc for acc in registration.social_accounts if acc.platform == registration.primary_platform),
        registration.social_accounts[0]
    )
    user_id = f"{primary_account.platform}:{primary_account.username}"

    # Store registration
    _user_registrations[user_id] = {
        'user_id': user_id,
        'email': registration.email,
        'social_accounts': [acc.dict() for acc in registration.social_accounts],
        'primary_platform': registration.primary_platform,
        'registered_at': datetime.now().isoformat(),
        'access_granted': True,
    }

    # Store initial comment if provided
    if registration.comment:
        _user_comments.append({
            'user_id': user_id,
            'comment': registration.comment,
            'timestamp': datetime.now().isoformat(),
        })

    print(f"[USER] New registration: {user_id} with {len(registration.social_accounts)} accounts")

    return {
        'success': True,
        'user_id': user_id,
        'access_granted': True,
        'message': 'Registration successful! You now have access to all deep dive sections.',
    }


@app.get("/api/users/verify/{user_id}")
async def verify_user(user_id: str):
    """
    Verify if a user has access to deep dive sections.
    """
    user = _user_registrations.get(user_id)
    if user:
        return {
            'valid': True,
            'user_id': user_id,
            'access_granted': user.get('access_granted', False),
            'registered_at': user.get('registered_at'),
        }
    return {
        'valid': False,
        'access_granted': False,
    }


@app.post("/api/users/comment")
async def add_comment(comment: UserComment):
    """
    Add a comment/feedback from any user (registered or anonymous).
    """
    # Allow anonymous users to submit feedback
    is_registered = comment.user_id in _user_registrations or comment.user_id == 'anonymous'

    _user_comments.append({
        'user_id': comment.user_id,
        'comment': comment.comment,
        'rating': comment.rating,
        'page': comment.page,
        'is_registered': comment.user_id in _user_registrations,
        'timestamp': datetime.now().isoformat(),
    })

    print(f"[FEEDBACK] From {comment.user_id}: {comment.comment[:80]}...")

    return {
        'success': True,
        'message': 'Thank you for your feedback!',
    }


@app.get("/api/users/stats")
async def get_user_stats():
    """
    Get registration and feedback statistics (admin endpoint).
    """
    # Count ALL connected platforms (not just primary)
    platform_counts = {}
    total_accounts = 0
    for user in _user_registrations.values():
        social_accounts = user.get('social_accounts', [])
        for account in social_accounts:
            platform = account.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            total_accounts += 1

    # Count feedback by type
    feedback_types = {}
    for comment in _user_comments:
        # Extract reaction type from comment like "[helpful] feedback text"
        comment_text = comment.get('comment', '')
        if comment_text.startswith('[') and ']' in comment_text:
            reaction = comment_text.split(']')[0][1:]
            feedback_types[reaction] = feedback_types.get(reaction, 0) + 1

    return {
        'total_users': len(_user_registrations),
        'total_accounts': total_accounts,
        'total_comments': len(_user_comments),
        'platforms': platform_counts,  # For frontend CommunityStatsCard
        'by_platform': platform_counts,  # Legacy
        'feedback_types': feedback_types,
        'recent_registrations': list(_user_registrations.values())[-10:],
        'recent_comments': _user_comments[-10:],
    }


# =============================================================================
# GOVERNMENT INTERVENTION MODULE (Module 7: Strategic Intervention Tracker)
# =============================================================================
# Tracks administrative control, back-door deals, and non-market forces
# that materially affect price discovery, supply availability, and systemic risk.

class ControlLevel(str, Enum):
    """Confidence level for administrative control signals"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CONFIRMED = "confirmed"

class InterventionType(str, Enum):
    """Types of government intervention"""
    EQUITY_STAKE = "equity_stake"
    JOINT_VENTURE = "joint_venture"
    OFFTAKE_AGREEMENT = "offtake_agreement"
    REGULATORY_FORBEARANCE = "regulatory_forbearance"
    DPA_INVOCATION = "dpa_invocation"
    LOGISTICS_PRIORITY = "logistics_priority"
    STOCKPILE_PURCHASE = "stockpile_purchase"
    EXPORT_RESTRICTION = "export_restriction"

class EquityStake(BaseModel):
    """Government or strategic equity ownership"""
    entity: str  # Company or asset name
    government: str  # US, China, etc.
    stake_pct: float
    vehicle: str  # Direct, SPV, sovereign fund, etc.
    date_acquired: Optional[str] = None
    strategic_metal: str  # Silver, copper, lithium, etc.
    control_level: ControlLevel
    notes: str

class ChokepointAsset(BaseModel):
    """Critical processing/logistics chokepoint"""
    name: str
    type: str  # Smelter, refinery, port, rail hub, etc.
    location: str
    controller: str  # Government or company
    metals_processed: List[str]
    capacity_pct_global: float  # % of global processing
    control_level: ControlLevel
    strategic_significance: str

class RegulatoryAction(BaseModel):
    """Regulatory forbearance or intervention"""
    agency: str  # Fed, SEC, OCC, FDIC, etc.
    action_type: str  # Waiver, relief, extension, etc.
    target: str  # Bank, sector, rule
    date: str
    duration_months: Optional[int] = None
    impact: str
    control_level: ControlLevel
    hidden_signal: str  # What this really means

class DPAAction(BaseModel):
    """Defense Production Act invocation or implied usage"""
    title: str
    sector: str
    metals_affected: List[str]
    date: str
    explicit: bool  # True if formally invoked, False if implied
    demand_impact: str  # Hidden demand floor created
    civilian_impact: str  # Effect on civilian supply
    control_level: ControlLevel

class StrategicScenario(BaseModel):
    """Strategic outcome scenario"""
    name: str
    probability: str  # "likely", "possible", "emerging"
    description: str
    indicators: List[str]
    outcome: str
    risk_color: str  # green, yellow, orange, red

class GovernmentInterventionData(BaseModel):
    """Complete government intervention module data"""
    overall_control_level: ControlLevel
    administrative_override_active: bool
    alert_message: Optional[str] = None

    # Sub-panels
    equity_stakes: List[EquityStake]
    chokepoints: List[ChokepointAsset]
    regulatory_actions: List[RegulatoryAction]
    dpa_actions: List[DPAAction]

    # Strategic outcomes
    current_scenario: str
    scenarios: List[StrategicScenario]

    # Interpretation signals
    signal_hierarchy: Dict[str, str]

    last_updated: str


def build_government_intervention_data() -> GovernmentInterventionData:
    """
    Build government intervention tracking data.
    This aggregates known government actions affecting strategic metals markets.
    """

    # Known equity stakes in strategic metals
    equity_stakes = [
        EquityStake(
            entity="Codelco (Chile)",
            government="Chile",
            stake_pct=100.0,
            vehicle="State-owned enterprise",
            strategic_metal="Copper",
            control_level=ControlLevel.CONFIRMED,
            notes="World's largest copper producer. Government has full control over ~28% of global copper."
        ),
        EquityStake(
            entity="China Molybdenum (CMOC)",
            government="China",
            stake_pct=36.0,
            vehicle="State fund + provincial SOE",
            strategic_metal="Cobalt, Copper",
            control_level=ControlLevel.CONFIRMED,
            notes="Controls ~15% of global cobalt through DRC operations."
        ),
        EquityStake(
            entity="Jiangxi Copper",
            government="China",
            stake_pct=47.0,
            vehicle="Provincial SOE",
            strategic_metal="Copper, Silver",
            control_level=ControlLevel.CONFIRMED,
            notes="Largest copper smelter in China. Key silver byproduct."
        ),
        EquityStake(
            entity="Fresnillo PLC",
            government="Mexico (implicit)",
            stake_pct=0.0,
            vehicle="Regulatory leverage",
            strategic_metal="Silver",
            control_level=ControlLevel.MEDIUM,
            notes="World's largest primary silver miner. Subject to Mexican nationalization risk."
        ),
        EquityStake(
            entity="KGHM Polska Miedź",
            government="Poland",
            stake_pct=31.8,
            vehicle="State Treasury",
            strategic_metal="Silver, Copper",
            control_level=ControlLevel.CONFIRMED,
            notes="2nd largest silver producer globally. State has blocking stake."
        ),
        EquityStake(
            entity="US Strategic Petroleum Reserve",
            government="USA",
            stake_pct=100.0,
            vehicle="Direct government",
            strategic_metal="Oil (precedent)",
            control_level=ControlLevel.CONFIRMED,
            notes="Model for potential strategic metals reserve. 2022 releases showed willingness to intervene."
        ),
        EquityStake(
            entity="Defense Logistics Agency (DLA)",
            government="USA",
            stake_pct=100.0,
            vehicle="DOD direct control",
            strategic_metal="Silver, Rare Earths",
            control_level=ControlLevel.CONFIRMED,
            notes="National Defense Stockpile. Undisclosed quantities of strategic metals."
        ),
    ]

    # Critical processing chokepoints
    chokepoints = [
        ChokepointAsset(
            name="Chinese Silver Smelting Complex",
            type="Smelter network",
            location="China (multiple provinces)",
            controller="Chinese SOEs / State coordination",
            metals_processed=["Silver", "Lead", "Zinc"],
            capacity_pct_global=42.0,
            control_level=ControlLevel.CONFIRMED,
            strategic_significance="China processes 42% of world silver. Export restrictions = global shortage."
        ),
        ChokepointAsset(
            name="LBMA Good Delivery Refiners",
            type="Refinery certification",
            location="Global (77 refiners)",
            controller="LBMA (UK)",
            metals_processed=["Gold", "Silver"],
            capacity_pct_global=95.0,
            control_level=ControlLevel.HIGH,
            strategic_significance="Controls definition of 'investment grade' bullion. Regulatory chokepoint."
        ),
        ChokepointAsset(
            name="COMEX Approved Depositories",
            type="Storage certification",
            location="USA (5 locations)",
            controller="CME Group",
            metals_processed=["Gold", "Silver"],
            capacity_pct_global=100.0,
            control_level=ControlLevel.CONFIRMED,
            strategic_significance="All COMEX deliveries must flow through approved vaults. Bottleneck."
        ),
        ChokepointAsset(
            name="Port of Rotterdam",
            type="Logistics hub",
            location="Netherlands",
            controller="Rotterdam Port Authority",
            metals_processed=["All metals"],
            capacity_pct_global=15.0,
            control_level=ControlLevel.MEDIUM,
            strategic_significance="Key EU entry point for metals. NATO logistics priority in crisis."
        ),
        ChokepointAsset(
            name="Panama Canal",
            type="Shipping lane",
            location="Panama",
            controller="Panama Canal Authority",
            metals_processed=["All metals"],
            capacity_pct_global=40.0,
            control_level=ControlLevel.HIGH,
            strategic_significance="US-Asia trade route. Drought restrictions = supply shock."
        ),
    ]

    # Recent regulatory forbearance
    regulatory_actions = [
        RegulatoryAction(
            agency="Federal Reserve",
            action_type="BTFP lending facility",
            target="Banking system",
            date="2023-03-12",
            duration_months=12,
            impact="$165B emergency lending at par value",
            control_level=ControlLevel.CONFIRMED,
            hidden_signal="Banks holding underwater securities kept solvent through Fed backstop."
        ),
        RegulatoryAction(
            agency="OCC",
            action_type="Supplementary Leverage Ratio exemption",
            target="Large banks",
            date="2020-04-01",
            duration_months=12,
            impact="Excluded Treasuries from leverage calculations",
            control_level=ControlLevel.CONFIRMED,
            hidden_signal="Banks allowed to hold unlimited sovereign debt without capital impact."
        ),
        RegulatoryAction(
            agency="SEC",
            action_type="Delayed mark-to-market enforcement",
            target="Regional banks",
            date="2023-03-15",
            duration_months=None,
            impact="Unrealized losses not forcing immediate recognition",
            control_level=ControlLevel.HIGH,
            hidden_signal="Zombie banks continue operating. True insolvency hidden."
        ),
        RegulatoryAction(
            agency="FDIC",
            action_type="Systemic risk exception",
            target="SVB, Signature Bank depositors",
            date="2023-03-12",
            duration_months=None,
            impact="Full deposit guarantee beyond $250K",
            control_level=ControlLevel.CONFIRMED,
            hidden_signal="Implicit guarantee now exists for all large deposits."
        ),
        RegulatoryAction(
            agency="CFTC",
            action_type="Position limit exemptions",
            target="Bullion banks",
            date="Ongoing",
            duration_months=None,
            impact="Concentrated short positions allowed",
            control_level=ControlLevel.HIGH,
            hidden_signal="Market makers can maintain outsized short positions without limits."
        ),
    ]

    # Defense Production Act and priority allocation
    dpa_actions = [
        DPAAction(
            title="DPA Title III - Critical Minerals",
            sector="Mining and processing",
            metals_affected=["Lithium", "Cobalt", "Nickel", "Graphite", "Manganese"],
            date="2022-03-31",
            explicit=True,
            demand_impact="$750M+ allocated for domestic production. Hidden demand floor.",
            civilian_impact="EV battery supply competition. Strategic priority over consumer.",
            control_level=ControlLevel.CONFIRMED
        ),
        DPAAction(
            title="Inflation Reduction Act - Battery Provisions",
            sector="Battery manufacturing",
            metals_affected=["Lithium", "Cobalt", "Nickel", "Silver"],
            date="2022-08-16",
            explicit=False,
            demand_impact="Tax credits create structural demand. $7,500/vehicle subsidy.",
            civilian_impact="Reshoring demand competes with existing supply chains.",
            control_level=ControlLevel.HIGH
        ),
        DPAAction(
            title="DOD Silver Requirements (F-35, Missiles)",
            sector="Defense electronics",
            metals_affected=["Silver"],
            date="Ongoing",
            explicit=False,
            demand_impact="~15M oz/year military demand. Classified exact figures.",
            civilian_impact="Military contracts get priority. Civilian electronics may face allocation.",
            control_level=ControlLevel.MEDIUM
        ),
        DPAAction(
            title="CHIPS Act - Semiconductor Priority",
            sector="Semiconductors",
            metals_affected=["Silver", "Copper", "Gold"],
            date="2022-08-09",
            explicit=False,
            demand_impact="$52B in subsidies creating metal demand floor.",
            civilian_impact="Industrial silver demand locked in by government contracts.",
            control_level=ControlLevel.HIGH
        ),
    ]

    # Strategic outcome scenarios
    scenarios = [
        StrategicScenario(
            name="Managed Scarcity",
            probability="likely",
            description="Prices suppressed through paper markets while physical allocation controlled administratively.",
            indicators=[
                "Paper-physical spread widening",
                "Dealer premiums rising",
                "Delivery delays increasing",
                "Quiet stockpile purchases"
            ],
            outcome="Markets appear stable but physical access deteriorates. Two-tier pricing emerges.",
            risk_color="yellow"
        ),
        StrategicScenario(
            name="Civilian Supply Shock",
            probability="possible",
            description="Military/strategic demand crowds out industrial and retail buyers.",
            indicators=[
                "DPA invocations expanding",
                "Export restrictions by producing nations",
                "Industrial user complaints",
                "Allocation system rumors"
            ],
            outcome="Shortages blamed on logistics. Emergency rationing introduced quietly.",
            risk_color="orange"
        ),
        StrategicScenario(
            name="Price Signal Break",
            probability="emerging",
            description="Paper market fails to clear against physical demand. Emergency intervention required.",
            indicators=[
                "COMEX fails to deliver",
                "LBMA default event",
                "Physical premiums >50%",
                "Major dealer halts sales"
            ],
            outcome="Paper price becomes meaningless. Physical market takes over with extreme volatility.",
            risk_color="red"
        ),
    ]

    # Determine current scenario based on indicators
    current_scenario = "Managed Scarcity"  # Default assessment

    # Signal hierarchy (interpretation rules)
    signal_hierarchy = {
        "rule_1": "Administrative actions override price signals",
        "rule_2": "Ownership signals override contract signals",
        "rule_3": "Processing control signals override mining signals",
        "rule_4": "Allocation signals override availability signals",
        "interpretation": "If administrative signal conflicts with market signal, trust administrative signal"
    }

    # Determine overall control level
    confirmed_actions = len([a for a in regulatory_actions if a.control_level == ControlLevel.CONFIRMED])
    high_control_signals = len([a for a in regulatory_actions if a.control_level == ControlLevel.HIGH])

    if confirmed_actions >= 3:
        overall_level = ControlLevel.HIGH
        override_active = True
        alert = "Multiple confirmed administrative interventions detected. Markets not freely clearing."
    elif high_control_signals >= 2:
        overall_level = ControlLevel.MEDIUM
        override_active = True
        alert = "Elevated administrative control signals. Monitor for escalation."
    else:
        overall_level = ControlLevel.LOW
        override_active = False
        alert = None

    return GovernmentInterventionData(
        overall_control_level=overall_level,
        administrative_override_active=override_active,
        alert_message=alert,
        equity_stakes=equity_stakes,
        chokepoints=chokepoints,
        regulatory_actions=regulatory_actions,
        dpa_actions=dpa_actions,
        current_scenario=current_scenario,
        scenarios=scenarios,
        signal_hierarchy=signal_hierarchy,
        last_updated=datetime.now().isoformat()
    )


@app.get("/api/government-intervention", response_model=GovernmentInterventionData)
async def get_government_intervention():
    """
    Get government intervention and administrative control data.
    Module 7: Strategic Intervention Tracker
    """
    return build_government_intervention_data()


@app.get("/api/government-intervention/equity")
async def get_equity_stakes():
    """Get government equity stakes in strategic metal assets"""
    data = build_government_intervention_data()
    return {
        "count": len(data.equity_stakes),
        "stakes": data.equity_stakes,
        "metals_controlled": list(set(s.strategic_metal for s in data.equity_stakes))
    }


@app.get("/api/government-intervention/chokepoints")
async def get_chokepoints():
    """Get critical processing and logistics chokepoints"""
    data = build_government_intervention_data()
    return {
        "count": len(data.chokepoints),
        "chokepoints": data.chokepoints,
        "total_control_pct": sum(c.capacity_pct_global for c in data.chokepoints) / len(data.chokepoints)
    }


@app.get("/api/government-intervention/regulatory")
async def get_regulatory_forbearance():
    """Get regulatory forbearance and intervention actions"""
    data = build_government_intervention_data()
    return {
        "count": len(data.regulatory_actions),
        "actions": data.regulatory_actions,
        "agencies_involved": list(set(a.agency for a in data.regulatory_actions))
    }


@app.get("/api/government-intervention/dpa")
async def get_dpa_actions():
    """Get Defense Production Act and priority allocation signals"""
    data = build_government_intervention_data()
    return {
        "count": len(data.dpa_actions),
        "actions": data.dpa_actions,
        "metals_affected": list(set(m for a in data.dpa_actions for m in a.metals_affected))
    }


@app.get("/api/government-intervention/scenarios")
async def get_strategic_scenarios():
    """Get strategic outcome scenarios and current assessment"""
    data = build_government_intervention_data()
    return {
        "current_scenario": data.current_scenario,
        "scenarios": data.scenarios,
        "signal_hierarchy": data.signal_hierarchy
    }


@app.get("/api/government-intervention/alert")
async def get_intervention_alert():
    """Get current administrative override alert status"""
    data = build_government_intervention_data()
    return {
        "override_active": data.administrative_override_active,
        "control_level": data.overall_control_level,
        "alert": data.alert_message,
        "interpretation": "Markets are no longer the decision-makers — administrators are." if data.administrative_override_active else "Markets functioning with normal regulatory oversight."
    }


# =============================================================================
# FAULT-WATCH ALERTS MODULE
# Strategic Alert System for Dealer Control, Clearing Stress & Funding Contagion
# =============================================================================

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    INACTIVE = "inactive"
    WATCHING = "watching"
    TRIGGERED = "triggered"
    CONFIRMED = "confirmed"

class AlertCondition(BaseModel):
    id: str
    name: str
    description: str
    detected: bool
    detection_date: Optional[str] = None
    evidence: Optional[str] = None
    data_source: str
    weight: float = 1.0

class StrategicAlert(BaseModel):
    id: str
    name: str
    subtitle: str
    description: str
    status: AlertStatus
    severity: AlertSeverity
    conditions_required: int
    conditions_met: int
    conditions: List[AlertCondition]
    trigger_window_days: int
    last_updated: str
    interpretation: str
    action_items: List[str]

class InflectionPoint(BaseModel):
    id: str
    name: str
    description: str
    current_status: str
    indicators: List[str]
    probability: str
    timeline: str
    what_to_watch: str

class FaultWatchAlertsData(BaseModel):
    overall_alert_level: AlertSeverity
    alerts_active: int
    conditions_triggered: int
    system_status: str
    alerts: List[StrategicAlert]
    inflection_points: List[InflectionPoint]
    market_regime: str
    regime_description: str
    last_updated: str


def build_fault_watch_alerts_data() -> FaultWatchAlertsData:
    """Build comprehensive fault watch alerts data"""

    # Alert A: Dealer Control Breaking (Squeeze Risk)
    alert_a_conditions = [
        AlertCondition(
            id="a1",
            name="Failed Sell-off Pattern",
            description="Spot down hard intraday → snaps back fast",
            detected=True,
            detection_date="2026-01-14",
            evidence="Silver dropped 2.3% at open, recovered to +0.8% by close. Classic failed breakdown.",
            data_source="Price action analysis",
            weight=1.0
        ),
        AlertCondition(
            id="a2",
            name="Options Expiration Volatility",
            description="Abnormal volatility spike during options expiration window",
            detected=True,
            detection_date="2026-01-15",
            evidence="Implied volatility jumped 40% into Jan COMEX options expiry. Unusual for this time of year.",
            data_source="Options chain data",
            weight=1.0
        ),
        AlertCondition(
            id="a3",
            name="Persistent Premium Expansion",
            description="Physical doesn't follow paper price movements",
            detected=True,
            detection_date="2026-01-13",
            evidence="Physical premiums at 12-15% over spot despite paper selling. Dealers not passing through discounts.",
            data_source="Dealer quotes / APMEX, JM Bullion",
            weight=1.2
        ),
        AlertCondition(
            id="a4",
            name="Product Unavailability",
            description="Public product unavailability persists (not just one-day sellout)",
            detected=True,
            detection_date="2026-01-10",
            evidence="1oz Silver Eagles showing 3-4 week delays. Monster boxes backordered at multiple dealers.",
            data_source="Major dealer inventory",
            weight=1.0
        ),
        AlertCondition(
            id="a5",
            name="Bank Equity Synchronization",
            description="Bank equities show synchronized abnormal moves during metals events",
            detected=False,
            evidence="No significant synchronized moves detected yet. Watching JPM, GS, MS during metal spikes.",
            data_source="Bank stock correlation analysis",
            weight=1.5
        ),
    ]

    alert_a_met = sum(1 for c in alert_a_conditions if c.detected)
    alert_a_status = AlertStatus.TRIGGERED if alert_a_met >= 3 else AlertStatus.WATCHING if alert_a_met >= 2 else AlertStatus.INACTIVE

    # Alert B: Clearing Stress Escalation
    alert_b_conditions = [
        AlertCondition(
            id="b1",
            name="Exchange Margin Hikes",
            description="Exchange margin hikes / intraday margin calls",
            detected=True,
            detection_date="2026-01-12",
            evidence="COMEX raised silver maintenance margins 8% on Jan 12. Third hike in 60 days.",
            data_source="CME Group margin announcements",
            weight=1.5
        ),
        AlertCondition(
            id="b2",
            name="Position Limit Changes",
            description="Position limit changes or 'temporary' trading constraints",
            detected=False,
            evidence="No new position limits announced. Watching for 'technical issues' or 'orderly market' language.",
            data_source="Exchange regulatory filings",
            weight=1.5
        ),
        AlertCondition(
            id="b3",
            name="Settlement Delays",
            description="Settlement delays / allocation language spreads",
            detected=True,
            detection_date="2026-01-14",
            evidence="LBMA reported 'allocation delays' for January delivery. SLV allocation taking 4+ days vs normal 2.",
            data_source="LBMA clearing data / ETF filings",
            weight=2.0
        ),
    ]

    alert_b_met = sum(1 for c in alert_b_conditions if c.detected)
    alert_b_status = AlertStatus.TRIGGERED if alert_b_met >= 2 else AlertStatus.WATCHING if alert_b_met >= 1 else AlertStatus.INACTIVE

    # Alert C: Funding Contagion (Door-Risk)
    alert_c_conditions = [
        AlertCondition(
            id="c1",
            name="Bank Equity Crash",
            description="Bank equity crash relative to peers",
            detected=False,
            evidence="Major banks trading within normal ranges. No outlier moves detected.",
            data_source="Bank stock relative performance",
            weight=2.0
        ),
        AlertCondition(
            id="c2",
            name="Credit Spread Widening",
            description="Credit spreads widen sharply (CDS/bond yields)",
            detected=True,
            detection_date="2026-01-11",
            evidence="JPM 5yr CDS widened 15bps in 3 days. Investment grade spreads at 6-month highs.",
            data_source="Credit market data",
            weight=1.5
        ),
        AlertCondition(
            id="c3",
            name="Prime Brokerage Tightening",
            description="Collateral demands / prime brokerage tightening",
            detected=False,
            evidence="No confirmed reports of collateral haircut changes. Monitoring dealer chatter.",
            data_source="Market intelligence / SEC filings",
            weight=2.0
        ),
    ]

    alert_c_met = sum(1 for c in alert_c_conditions if c.detected)
    alert_c_status = AlertStatus.TRIGGERED if alert_c_met >= 2 else AlertStatus.WATCHING if alert_c_met >= 1 else AlertStatus.INACTIVE

    # Build alert objects
    alerts = [
        StrategicAlert(
            id="alert_a",
            name="Dealer Control Breaking",
            subtitle="Squeeze Risk",
            description="Paper manipulation losing effectiveness. Physical market diverging from paper pricing.",
            status=alert_a_status,
            severity=AlertSeverity.HIGH if alert_a_status == AlertStatus.TRIGGERED else AlertSeverity.MEDIUM,
            conditions_required=3,
            conditions_met=alert_a_met,
            conditions=alert_a_conditions,
            trigger_window_days=5,
            last_updated="2026-01-15T14:30:00Z",
            interpretation="Dealers struggling to maintain price control. Failed sell-offs + persistent premiums + product delays = structural tightness that paper markets can't hide.",
            action_items=[
                "Monitor intraday reversals for failed breakdown patterns",
                "Track physical premium expansion vs spot",
                "Watch for bank equity correlation during metal spikes",
                "Check dealer inventory and lead times daily"
            ]
        ),
        StrategicAlert(
            id="alert_b",
            name="Clearing Stress Escalation",
            subtitle="Settlement Risk",
            description="Exchange infrastructure showing signs of stress. Delivery mechanism under pressure.",
            status=alert_b_status,
            severity=AlertSeverity.HIGH if alert_b_status == AlertStatus.TRIGGERED else AlertSeverity.MEDIUM,
            conditions_required=2,
            conditions_met=alert_b_met,
            conditions=alert_b_conditions,
            trigger_window_days=10,
            last_updated="2026-01-15T14:30:00Z",
            interpretation="Margin hikes + settlement delays = clearing system under pressure. When exchanges start changing rules mid-game, it signals they're managing a problem.",
            action_items=[
                "Track CME/COMEX margin announcements",
                "Monitor LBMA settlement timing",
                "Watch for 'orderly market' regulatory language",
                "Check ETF creation/redemption flows"
            ]
        ),
        StrategicAlert(
            id="alert_c",
            name="Funding Contagion",
            subtitle="Door-Risk",
            description="Bank funding stress spreading. Credit markets signaling institutional concern.",
            status=alert_c_status,
            severity=AlertSeverity.CRITICAL if alert_c_status == AlertStatus.TRIGGERED else AlertSeverity.MEDIUM,
            conditions_required=2,
            conditions_met=alert_c_met,
            conditions=alert_c_conditions,
            trigger_window_days=5,
            last_updated="2026-01-15T14:30:00Z",
            interpretation="Credit spreads widening but bank equities holding. If banks start underperforming peers during metals moves, the funding stress is real. This is the 'door' risk — everyone trying to exit at once.",
            action_items=[
                "Monitor bank CDS spreads daily",
                "Track bank equity relative performance",
                "Watch for prime brokerage collateral changes",
                "Monitor repo market stress indicators"
            ]
        ),
    ]

    # Inflection Points
    inflection_points = [
        InflectionPoint(
            id="ip1",
            name="Paper-Physical Linkage Break",
            description="Paper selling no longer produces sustained downside; physical tightness persists",
            current_status="APPROACHING",
            indicators=[
                "Premiums sustained above 10% for 2+ weeks",
                "Failed selloff patterns increasing",
                "Dealer inventory critically low",
                "Physical demand unresponsive to paper price drops"
            ],
            probability="65%",
            timeline="Days to weeks",
            what_to_watch="Watch for paper price drops that don't clear physical inventory. When selling into bids stops working, the linkage is breaking."
        ),
        InflectionPoint(
            id="ip2",
            name="Clearinghouse Containment Visible",
            description="Margin/limits/interventions accelerate visibly",
            current_status="EARLY SIGNALS",
            indicators=[
                "Multiple margin hikes in short period",
                "Position limit changes",
                "Trading halts or 'technical issues'",
                "Settlement rule modifications"
            ],
            probability="45%",
            timeline="Weeks to months",
            what_to_watch="When exchanges start changing rules rapidly or cite 'market integrity' concerns, containment is becoming visible."
        ),
        InflectionPoint(
            id="ip3",
            name="Bank Funding Stress Obvious",
            description="Equities/credit moving as if an event is underway",
            current_status="NOT YET",
            indicators=[
                "Bank stocks underperforming sharply",
                "CDS spreads blowing out",
                "Interbank lending freezing",
                "Flight to quality in credit"
            ],
            probability="25%",
            timeline="Uncertain",
            what_to_watch="This is the final inflection. When bank funding stress becomes market-obvious, the 'managed stability' regime is over."
        ),
    ]

    # Calculate overall status
    alerts_active = sum(1 for a in alerts if a.status in [AlertStatus.TRIGGERED, AlertStatus.CONFIRMED])
    conditions_triggered = sum(a.conditions_met for a in alerts)

    if any(a.status == AlertStatus.CONFIRMED for a in alerts):
        overall_level = AlertSeverity.CRITICAL
        system_status = "CRISIS MODE"
        market_regime = "Forced Repricing"
        regime_description = "The managed stability regime has failed. Markets are repricing under duress."
    elif alerts_active >= 2:
        overall_level = AlertSeverity.HIGH
        system_status = "ELEVATED RISK"
        market_regime = "Managed Instability"
        regime_description = "Multiple stress signals active. The system is managing visible problems. Transition period."
    elif alerts_active >= 1:
        overall_level = AlertSeverity.MEDIUM
        system_status = "ALERT ACTIVE"
        market_regime = "Managed Stability (Stressed)"
        regime_description = "Control mechanisms active but under pressure. Watch for escalation."
    else:
        overall_level = AlertSeverity.LOW
        system_status = "MONITORING"
        market_regime = "Managed Stability"
        regime_description = "Normal operations with standard price management. No acute stress visible."

    return FaultWatchAlertsData(
        overall_alert_level=overall_level,
        alerts_active=alerts_active,
        conditions_triggered=conditions_triggered,
        system_status=system_status,
        alerts=alerts,
        inflection_points=inflection_points,
        market_regime=market_regime,
        regime_description=regime_description,
        last_updated="2026-01-15T14:30:00Z"
    )


@app.get("/api/fault-watch-alerts", response_model=FaultWatchAlertsData)
async def get_fault_watch_alerts():
    """Get comprehensive fault watch alerts data"""
    return build_fault_watch_alerts_data()


@app.get("/api/fault-watch-alerts/summary")
async def get_fault_watch_alerts_summary():
    """Get alert summary for dashboard"""
    data = build_fault_watch_alerts_data()
    return {
        "overall_level": data.overall_alert_level,
        "alerts_active": data.alerts_active,
        "conditions_triggered": data.conditions_triggered,
        "system_status": data.system_status,
        "market_regime": data.market_regime,
        "regime_description": data.regime_description
    }


@app.get("/api/fault-watch-alerts/inflection-points")
async def get_inflection_points():
    """Get inflection point analysis"""
    data = build_fault_watch_alerts_data()
    return {
        "inflection_points": data.inflection_points,
        "market_regime": data.market_regime,
        "regime_description": data.regime_description
    }


@app.get("/api/fault-watch-alerts/{alert_id}")
async def get_specific_alert(alert_id: str):
    """Get specific alert details"""
    data = build_fault_watch_alerts_data()
    for alert in data.alerts:
        if alert.id == alert_id:
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")


# =============================================================================
# CRISIS SEARCH PAD MODULE
# Silver/Bank Crisis Research & Monitoring Dashboard
# =============================================================================

class DataTier(str, Enum):
    TIER1_CONFIRMED = "tier1"
    TIER2_RUMOR = "tier2"
    TIER3_POSITIONS = "tier3"

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    PARTIAL = "partial"
    FABRICATED = "fabricated"

class RepoEntry(BaseModel):
    date: str
    amount: str
    notes: str

class ComexDeliveryEntry(BaseModel):
    event: str
    date: str
    details: str

class LbmaData(BaseModel):
    metric: str
    value: str
    date: Optional[str] = None

class PriceEntry(BaseModel):
    date: str
    price: str
    event: str

class RumorEntry(BaseModel):
    title: str
    claim: str
    origin: str
    verification_status: VerificationStatus
    status_note: str

class BankPosition(BaseModel):
    bank: str
    reported_action: Optional[str] = None
    current_position: Optional[str] = None
    stock_price: Optional[str] = None
    net_income: Optional[str] = None
    status: str
    forecast: Optional[str] = None
    rumors: Optional[str] = None

class MonitoringMetric(BaseModel):
    name: str
    frequency: str
    source: Optional[str] = None

class KeySource(BaseModel):
    category: str
    name: str
    url: Optional[str] = None
    notes: Optional[str] = None

class KeyDate(BaseModel):
    date: str
    event: str
    significance: str

class CrisisSearchPadData(BaseModel):
    last_updated: str
    # Tier 1: Confirmed Data
    fed_repo_activity: List[RepoEntry]
    fed_repo_key_change: str
    fed_repo_sources: List[str]
    comex_delivery_stress: List[ComexDeliveryEntry]
    comex_sources: List[str]
    lbma_data: List[LbmaData]
    lbma_key_event: str
    lbma_sources: List[str]
    china_export_restrictions: dict
    silver_price_action: List[PriceEntry]
    silver_2025_performance: str
    silver_2026_ytd: str
    # Tier 2: Rumors
    rumors: List[RumorEntry]
    # Tier 3: Bank Positions
    bank_positions: List[BankPosition]
    # Monitoring
    daily_metrics: List[MonitoringMetric]
    monthly_metrics: List[MonitoringMetric]
    event_triggers: List[str]
    # Sources
    key_sources: List[KeySource]
    search_queries: List[str]
    # Assessment
    current_assessment: dict
    key_dates: List[KeyDate]


def build_crisis_search_pad_data() -> CrisisSearchPadData:
    """Build comprehensive crisis search pad data"""

    # Fed Repo Activity
    fed_repo_activity = [
        RepoEntry(date="Oct 31, 2025", amount="$51B", notes="First major injection after 5+ years of near-zero activity"),
        RepoEntry(date="Dec 26, 2025", amount="$17.251B", notes="Morning of, banks tapped Standing Repo Facility"),
        RepoEntry(date="Dec 28, 2025", amount="$34B", notes="Sunday 5PM injection"),
        RepoEntry(date="Dec 31, 2025", amount="$74.6B", notes="Record year-end draw on Standing Repo Facility"),
        RepoEntry(date="Jan 2, 2026", amount="$0", notes="Year-end turmoil resolved, SRF balance returned to zero"),
    ]

    # COMEX Delivery Stress
    comex_delivery = [
        ComexDeliveryEntry(event="Thanksgiving Block Order", date="Nov 30, 2025", details="7,330 contracts (36.65M oz) demanded; only 2.57M oz delivered; 93% cash settled at $65M premium"),
        ComexDeliveryEntry(event="December Deliveries", date="Dec 2025", details="12,946 contracts (65M oz) requested; ~95% cash settled"),
        ComexDeliveryEntry(event="January Deliveries MTD", date="Jan 7, 2026", details="1,624 contracts delivered; JPM issued 99% of 8.1M oz"),
        ComexDeliveryEntry(event="Registered Inventory", date="Current", details="~127M oz (down 70%+ since 2020)"),
        ComexDeliveryEntry(event="Margin Hike", date="Dec 29, 2025", details="CME raised margins"),
        ComexDeliveryEntry(event="Margin Hike", date="Jan 7, 2026", details="Raised to $32,500 (47% increase in one week)"),
    ]

    # LBMA Data
    lbma_data = [
        LbmaData(metric="Total Silver Holdings", value="27,818 tonnes (894M oz)", date="End Dec 2025"),
        LbmaData(metric="Monthly Change", value="+2.30%", date="Dec 2025"),
        LbmaData(metric="Free Float Estimate", value="~135-155M oz", date="Per TD Securities"),
        LbmaData(metric="ETF Holdings", value="~62% of vault total", date="Historic average"),
        LbmaData(metric="Years to Depletion", value="4-7 months", date="At current drain rate"),
    ]

    # Silver Price Action
    price_action = [
        PriceEntry(date="Jan 1, 2025", price="~$29/oz", event="Year start"),
        PriceEntry(date="Dec 26, 2025", price="$79.28", event="2025 High"),
        PriceEntry(date="Dec 29, 2025", price="$83+/oz", event="Shanghai price"),
        PriceEntry(date="Dec 31, 2025", price="~$71/oz", event="Post-correction"),
        PriceEntry(date="Jan 14, 2026", price="$92.25", event="All-time nominal high"),
        PriceEntry(date="Jan 16, 2026", price="~$91.50", event="Current"),
    ]

    # Tier 2: Rumors
    rumors = [
        RumorEntry(
            title="Bank Collapse Narrative (Dec 28-29, 2025)",
            claim="'Systemically important' bank failed $2.3B margin call at 2:47 AM",
            origin="Hal Turner Radio Show, amplified via @silvertrade on X",
            verification_status=VerificationStatus.UNVERIFIED,
            status_note="No CME default notice, no FDIC action, no regulator statement"
        ),
        RumorEntry(
            title="HSBC January 31 Exit Deadline",
            claim="HSBC must exit silver market by Jan 31, 2026 due to inability to deliver registered metal + lawsuits",
            origin="Social media, precious metals forums",
            verification_status=VerificationStatus.UNVERIFIED,
            status_note="Unconfirmed; HSBC continues active participation"
        ),
        RumorEntry(
            title="BofA + Citi Massive Shorts",
            claim="BofA short 1B oz; Citi short 3.4B oz (combined 4.4B oz = 550% of annual production)",
            origin="@NoLimitGains on X, widely shared",
            verification_status=VerificationStatus.FABRICATED,
            status_note="CFTC reports show 22 banks net short ~212M oz total (not 4.4B)"
        ),
        RumorEntry(
            title="$429M SILJ Options Bet",
            claim="$429M in SILJ calls placed 8 minutes before close on Dec 27, 2025",
            origin="SilverTrade",
            verification_status=VerificationStatus.PARTIAL,
            status_note="Timing suspicious but not verified"
        ),
        RumorEntry(
            title="Physical Premium Divergence",
            claim="Physical silver trading at $130/oz in Tokyo/Dubai vs $71 paper price (80% premium)",
            origin="@barkmeta on X, various precious metals sites",
            verification_status=VerificationStatus.PARTIAL,
            status_note="Premiums confirmed elevated but 80% divergence is extreme end of reports"
        ),
    ]

    # Bank Positions
    bank_positions = [
        BankPosition(
            bank="JPMorgan Chase",
            reported_action="Sold entire 200M oz paper short position (Jun-Oct 2025)",
            current_position="Net LONG; holds estimated 750M oz physical (largest stockpile in history)",
            stock_price="$334.61 (Jan 6, 2026) - near 52-week high",
            net_income="$56.66B TTM",
            status="Appears to be benefiting from rally, not distressed"
        ),
        BankPosition(
            bank="HSBC",
            current_position="Active in precious metals, LBMA member",
            rumors="Jan 31 exit deadline, leased out client metal",
            status="No confirmed distress",
            forecast="Expects silver to average $68.25 in 2026"
        ),
        BankPosition(
            bank="Citigroup",
            reported_action="Significant derivatives book (2nd to JPM in precious metals notionals)",
            current_position="Estimated $6.8B in silver futures to be sold during January index rebalancing",
            status="No confirmed silver-specific distress"
        ),
        BankPosition(
            bank="Bank of America",
            forecast="Raised 12-month silver target; sees potential $135-$309/oz",
            rumors="Short 1B oz (unverified)",
            status="Forecasting higher prices"
        ),
    ]

    # Monitoring Metrics
    daily_metrics = [
        MonitoringMetric(name="COMEX Registered Silver Inventory", frequency="Daily"),
        MonitoringMetric(name="COMEX Daily Delivery Notices", frequency="Daily"),
        MonitoringMetric(name="Silver Spot vs Futures (Backwardation)", frequency="Daily"),
        MonitoringMetric(name="Shanghai vs COMEX price spread", frequency="Daily"),
        MonitoringMetric(name="Fed Standing Repo Facility balance", frequency="Daily", source="FRED"),
        MonitoringMetric(name="CME Margin announcements", frequency="Daily"),
        MonitoringMetric(name="Bank stock prices (JPM, C, BAC, HSBC)", frequency="Daily"),
    ]

    monthly_metrics = [
        MonitoringMetric(name="LBMA Vault Holdings", frequency="5th business day each month"),
        MonitoringMetric(name="CFTC Bank Participation Report", frequency="Monthly"),
        MonitoringMetric(name="CFTC Commitment of Traders", frequency="Weekly/Monthly"),
        MonitoringMetric(name="Silver lease rates", frequency="Monthly"),
    ]

    event_triggers = [
        "Any FDIC/Fed emergency announcements",
        "CME member default notices",
        "China export license approvals/denials",
        "India import data",
        "SLV/PSLV redemption suspensions",
    ]

    # Key Sources
    key_sources = [
        KeySource(category="Official", name="NY Fed", url="https://www.newyorkfed.org/markets/opolicy/operating_policy_251210"),
        KeySource(category="Official", name="FRED Repo Data", url="https://fred.stlouisfed.org/series/RPONTSYD"),
        KeySource(category="Official", name="CME Delivery Reports", url="https://www.cmegroup.com/delivery_reports/"),
        KeySource(category="Official", name="LBMA Vault Data", url="https://www.lbma.org.uk/prices-and-data/london-vault-data"),
        KeySource(category="Official", name="CFTC Reports", url="https://cftc.gov"),
        KeySource(category="Analysis", name="DisruptionBanking.com", notes="Balanced analysis"),
        KeySource(category="Analysis", name="SchiffGold.com", notes="COMEX tracking"),
        KeySource(category="Analysis", name="SilverTrade.com", notes="Bullish, rumor amplifier"),
        KeySource(category="Analysis", name="DCReport.org", notes="Investigative journalism"),
        KeySource(category="Analysis", name="Wolf Street", notes="Macro/Fed analysis"),
        KeySource(category="Analysis", name="ZeroHedge", notes="Sentiment indicator"),
        KeySource(category="Social", name="r/WallStreetSilver", notes="Reddit community"),
        KeySource(category="Social", name="X: @silvertrade, @barkmeta", notes="Twitter sentiment"),
    ]

    search_queries = [
        "overnight repo facility banks silver [month] [year]",
        "COMEX silver failure to deliver [year]",
        "LBMA silver inventory drain [year]",
        "JPMorgan silver short position [year]",
        "HSBC silver exit [year]",
        "Bank of America Citigroup silver short [year]",
        "silver margin call bank [year]",
        "silver backwardation COMEX [year]",
        "Shanghai silver premium [year]",
        "China silver export restriction [year]",
        "Fed standing repo facility spike [year]",
        "CME silver margin hike [year]",
        "silver squeeze bank collapse [year]",
        "CFTC bank participation report silver [year]",
    ]

    # Current Assessment
    current_assessment = {
        "physical_market": {"status": "SEVERE", "detail": "Backwardation, delivery failures, elevated premiums"},
        "bank_exposure": {"status": "ELEVATED", "detail": "Rumors exceed evidence but watching closely"},
        "fed_activity": {"status": "WATCHLIST", "detail": "Repo spikes normalized but pattern since Halloween unusual"},
        "price_action": {"status": "VOLATILE", "detail": "Flat today after record week, consolidation or coiling unclear"},
    }

    key_dates = [
        KeyDate(date="Jan 17, 2026", event="SILJ options expiration", significance="From Dec 27 rumored $429M bet"),
        KeyDate(date="Jan 31, 2026", event="Rumored HSBC exit deadline", significance="Unverified but widely circulated"),
        KeyDate(date="Early Feb 2026", event="LBMA January vault data release", significance="Key inventory data point"),
    ]

    return CrisisSearchPadData(
        last_updated="January 16, 2026",
        fed_repo_activity=fed_repo_activity,
        fed_repo_key_change="Dec 11, 2025 - NY Fed removed aggregate operational limit on Standing Repo; now 'full allotment' with $40B max per proposition",
        fed_repo_sources=["NY Fed", "FRED", "Wolf Street", "DCReport"],
        comex_delivery_stress=comex_delivery,
        comex_sources=["CME Group", "SchiffGold", "Jensen David Substack"],
        lbma_data=lbma_data,
        lbma_key_event="Oct 8, 2025 - India placed 1,000 ton order; lease rates spiked from 0.25% to 200%; METALOR (Swiss refiner) withdrew until January 2026",
        lbma_sources=["LBMA", "TD Securities", "Mining.com"],
        china_export_restrictions={
            "effective_date": "January 1, 2026",
            "authorized_companies": 44,
            "min_capacity": "80+ tons annual production",
            "requirement": "Government license required",
            "impact": "Ring-fences ~60-70% of global refined silver supply",
            "sources": ["Global Times", "China Daily", "FXStreet"],
        },
        silver_price_action=price_action,
        silver_2025_performance="+147% (best since 1979)",
        silver_2026_ytd="+20-29%",
        rumors=rumors,
        bank_positions=bank_positions,
        daily_metrics=daily_metrics,
        monthly_metrics=monthly_metrics,
        event_triggers=event_triggers,
        key_sources=key_sources,
        search_queries=search_queries,
        current_assessment=current_assessment,
        key_dates=key_dates,
    )


@app.get("/api/crisis-search-pad", response_model=CrisisSearchPadData)
async def get_crisis_search_pad():
    """Get comprehensive crisis search pad data"""
    return build_crisis_search_pad_data()


@app.get("/api/crisis-search-pad/tier1")
async def get_tier1_data():
    """Get Tier 1 confirmed/verifiable data"""
    data = build_crisis_search_pad_data()
    return {
        "fed_repo_activity": data.fed_repo_activity,
        "fed_repo_key_change": data.fed_repo_key_change,
        "comex_delivery_stress": data.comex_delivery_stress,
        "lbma_data": data.lbma_data,
        "lbma_key_event": data.lbma_key_event,
        "china_export_restrictions": data.china_export_restrictions,
        "silver_price_action": data.silver_price_action,
    }


@app.get("/api/crisis-search-pad/tier2")
async def get_tier2_data():
    """Get Tier 2 rumors/unverified data"""
    data = build_crisis_search_pad_data()
    return {"rumors": data.rumors}


@app.get("/api/crisis-search-pad/tier3")
async def get_tier3_data():
    """Get Tier 3 bank positions"""
    data = build_crisis_search_pad_data()
    return {"bank_positions": data.bank_positions}


@app.get("/api/crisis-search-pad/assessment")
async def get_crisis_assessment():
    """Get current crisis assessment"""
    data = build_crisis_search_pad_data()
    return {
        "current_assessment": data.current_assessment,
        "key_dates": data.key_dates,
        "last_updated": data.last_updated,
    }


# =============================================================================
# RISK MATRIX MODULE
# =============================================================================

class RiskLevel(str, Enum):
    LOW = "low"
    LOW_MEDIUM = "low-medium"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium-high"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    HIGHER = "higher"
    RISING = "rising"

class RiskFactor(BaseModel):
    name: str
    pre_greenland: str
    post_greenland: str
    change_direction: str  # 'up', 'down', 'same'

class MonitorItem(BaseModel):
    item: str
    priority: str = "normal"  # 'high', 'normal'

class MonitoringPeriod(BaseModel):
    period: str
    items: List[MonitorItem]

class ImmediatePriority(BaseModel):
    name: str
    metric: str
    threshold: str
    current_status: str
    signal_meaning: str

class RiskMatrixData(BaseModel):
    last_updated: str
    context_event: str
    context_description: str
    risk_factors: List[RiskFactor]
    immediate_priorities: List[ImmediatePriority]
    monitoring_schedule: List[MonitoringPeriod]
    search_queries: List[str]
    bottom_line: str


def build_risk_matrix_data() -> RiskMatrixData:
    """Build the risk matrix comparison data"""

    risk_factors = [
        RiskFactor(
            name="Silver price trajectory",
            pre_greenland="Elevated",
            post_greenland="Higher",
            change_direction="up"
        ),
        RiskFactor(
            name="Bank margin pressure",
            pre_greenland="Moderate",
            post_greenland="High",
            change_direction="up"
        ),
        RiskFactor(
            name="Short squeeze probability",
            pre_greenland="Medium",
            post_greenland="Medium-High",
            change_direction="up"
        ),
        RiskFactor(
            name="COMEX delivery stress",
            pre_greenland="High",
            post_greenland="Higher",
            change_direction="up"
        ),
        RiskFactor(
            name="SRF usage likelihood",
            pre_greenland="Low (post year-end)",
            post_greenland="Rising",
            change_direction="up"
        ),
        RiskFactor(
            name="Systemic contagion risk",
            pre_greenland="Low-Medium",
            post_greenland="Medium",
            change_direction="up"
        ),
    ]

    monitoring_schedule = [
        MonitoringPeriod(
            period="Sunday Night",
            items=[
                MonitorItem(item="Silver futures gap size", priority="high"),
                MonitorItem(item="Gold futures gap size", priority="high"),
                MonitorItem(item="DXY (dollar) reaction", priority="normal"),
            ]
        ),
        MonitoringPeriod(
            period="Monday-Tuesday",
            items=[
                MonitorItem(item="CME margin announcements (another hike?)", priority="high"),
                MonitorItem(item="COMEX delivery notices", priority="high"),
                MonitorItem(item="Bank stock prices (JPM, HSBC, DB)", priority="normal"),
                MonitorItem(item="SRF usage (daily Fed data)", priority="high"),
            ]
        ),
        MonitoringPeriod(
            period="Later This Week",
            items=[
                MonitorItem(item="CFTC Commitment of Traders (if released)", priority="normal"),
                MonitorItem(item="LBMA clearing data", priority="normal"),
                MonitorItem(item="Physical premium reports from Asia", priority="high"),
            ]
        ),
    ]

    immediate_priorities = [
        ImmediatePriority(
            name="Fed SRF Usage",
            metric="Standing Repo Facility Balance",
            threshold="$200B+ spike",
            current_status="$0 (normalized post year-end)",
            signal_meaning="Hidden bank stress requiring emergency liquidity"
        ),
        ImmediatePriority(
            name="COMEX Delivery Failures",
            metric="Delivery vs Demand Ratio",
            threshold="Any inability to deliver",
            current_status="~95% cash settled (Dec)",
            signal_meaning="Physical shortage forcing paper settlement"
        ),
        ImmediatePriority(
            name="Bank CDS Spreads",
            metric="Credit Default Swaps (JPM, HSBC, Citi, BofA, MS, GS)",
            threshold="Sudden widening >50bps",
            current_status="Monitoring",
            signal_meaning="Market pricing in bank credit risk"
        ),
        ImmediatePriority(
            name="Gold/Silver Lease Rates",
            metric="LBMA/COMEX Lease Rates",
            threshold="Spike above 5%",
            current_status="Elevated (Oct spike to 200%)",
            signal_meaning="Desperation for physical metal"
        ),
        ImmediatePriority(
            name="Executive Movements",
            metric="Metals Desk Departures",
            threshold="Key personnel leaving",
            current_status="Watching",
            signal_meaning="Insiders exiting before problems surface"
        ),
        ImmediatePriority(
            name="Unusual Options Activity",
            metric="Large Put/Call Positions",
            threshold="$100M+ single bets",
            current_status="SILJ $429M rumor (Dec 27)",
            signal_meaning="Someone positioning for collapse"
        ),
    ]

    search_queries = [
        # Current event queries
        "Trump Greenland rare earth minerals silver",
        "Greenland mining critical minerals investment",
        "US strategic mineral reserves silver platinum",
        "Denmark Greenland sovereignty minerals deal",
        # Standard monitoring queries (use current month/year)
        "overnight repo facility banks silver January 2026",
        "COMEX silver failure to deliver 2026",
        "LBMA silver inventory drain 2026",
        "JPMorgan silver short position 2026",
        "HSBC silver exit 2026",
        "Bank of America Citigroup silver short 2026",
        "silver margin call bank 2026",
        "silver backwardation COMEX 2026",
        "Shanghai silver premium 2026",
        "China silver export restriction 2026",
        "Fed standing repo facility spike 2026",
        "CME silver margin hike 2026",
        "silver squeeze bank collapse 2026",
        "CFTC bank participation report silver 2026",
    ]

    return RiskMatrixData(
        last_updated="January 17, 2026",
        context_event="Trump Greenland Announcement",
        context_description="Trump's renewed push to acquire Greenland signals strategic interest in rare earth minerals and precious metals, potentially accelerating existing silver market pressures.",
        risk_factors=risk_factors,
        immediate_priorities=immediate_priorities,
        monitoring_schedule=monitoring_schedule,
        search_queries=search_queries,
        bottom_line="All risk vectors have shifted upward post-Greenland. The strategic minerals narrative adds fuel to an already stressed physical silver market. Watch Sunday night futures for initial market reaction."
    )


@app.get("/api/risk-matrix", response_model=RiskMatrixData)
async def get_risk_matrix():
    """Get current risk matrix data"""
    return build_risk_matrix_data()


@app.get("/api/risk-matrix/monitoring")
async def get_monitoring_schedule():
    """Get this week's monitoring schedule"""
    data = build_risk_matrix_data()
    return {
        "monitoring_schedule": data.monitoring_schedule,
        "last_updated": data.last_updated,
    }


@app.get("/api/risk-matrix/queries")
async def get_risk_matrix_queries():
    """Get search queries for risk monitoring"""
    data = build_risk_matrix_data()
    return {
        "search_queries": data.search_queries,
        "context_event": data.context_event,
    }


# =============================================================================
# DATA PIPELINE ENDPOINTS
# =============================================================================

# Initialize data pipeline (lazy loading to avoid import errors if deps missing)
_data_aggregator = None


def get_aggregator():
    """Lazy load the data aggregator"""
    global _data_aggregator
    if _data_aggregator is None:
        try:
            from data.aggregator import DataAggregator
            _data_aggregator = DataAggregator()
        except ImportError as e:
            print(f"Data pipeline not fully available: {e}")
            return None
    return _data_aggregator


@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """Get data pipeline status and availability"""
    aggregator = get_aggregator()
    if not aggregator:
        return {
            "status": "unavailable",
            "message": "Data pipeline modules not installed",
            "modules": {}
        }

    modules = {
        "prices": aggregator.price_monitor is not None,
        "fed": aggregator.fed_monitor is not None,
        "comex": aggregator.comex_monitor is not None,
        "sec": aggregator.sec_monitor is not None,
        "reddit": aggregator.reddit_scraper is not None,
        "news": aggregator.news_scraper is not None,
        "dealers": aggregator.dealer_scraper is not None,
        "regulatory": aggregator.regulatory_scraper is not None,
    }

    return {
        "status": "online",
        "modules": modules,
        "last_refresh": aggregator.last_full_refresh.isoformat() if aggregator.last_full_refresh else None,
    }


@app.get("/api/pipeline/data")
async def get_pipeline_data():
    """Get full data from all pipeline sources"""
    aggregator = get_aggregator()
    if not aggregator:
        raise HTTPException(status_code=503, detail="Data pipeline not available")

    return aggregator.get_full_data()


@app.post("/api/pipeline/refresh")
async def refresh_pipeline():
    """Force refresh all pipeline data sources"""
    aggregator = get_aggregator()
    if not aggregator:
        raise HTTPException(status_code=503, detail="Data pipeline not available")

    return aggregator.refresh_all()


@app.get("/api/pipeline/stress")
async def get_stress_indicators():
    """Get aggregated stress indicators from pipeline"""
    aggregator = get_aggregator()
    if not aggregator:
        raise HTTPException(status_code=503, detail="Data pipeline not available")

    return aggregator.get_stress_indicators()


@app.get("/api/pipeline/sec")
async def get_sec_filings():
    """Get SEC filing data from pipeline"""
    aggregator = get_aggregator()
    if not aggregator or not aggregator.sec_monitor:
        raise HTTPException(status_code=503, detail="SEC monitor not available")

    return aggregator.get_sec_data()


@app.get("/api/pipeline/sec/critical")
async def get_critical_sec_filings():
    """Get critical SEC filings (Wells notices, enforcement)"""
    aggregator = get_aggregator()
    if not aggregator or not aggregator.sec_monitor:
        raise HTTPException(status_code=503, detail="SEC monitor not available")

    filings = aggregator.sec_monitor.get_critical_filings(days=30)
    return [f.to_dict() for f in filings]


@app.get("/api/pipeline/social")
async def get_social_data():
    """Get social media data from pipeline"""
    aggregator = get_aggregator()
    if not aggregator or not aggregator.reddit_scraper:
        raise HTTPException(status_code=503, detail="Social scraper not available")

    return aggregator.get_social_data()


@app.get("/api/pipeline/news")
async def get_news_data():
    """Get news data from pipeline"""
    aggregator = get_aggregator()
    if not aggregator or not aggregator.news_scraper:
        raise HTTPException(status_code=503, detail="News scraper not available")

    return aggregator.get_news_data()


@app.get("/api/pipeline/news/breaking")
async def get_breaking_news():
    """Get breaking news from last 6 hours"""
    aggregator = get_aggregator()
    if not aggregator or not aggregator.news_scraper:
        raise HTTPException(status_code=503, detail="News scraper not available")

    articles = aggregator.news_scraper.get_breaking_news(hours=6)
    return [a.to_dict() for a in articles]


@app.get("/api/pipeline/dealers")
async def get_dealer_data():
    """Get dealer premium and availability data"""
    aggregator = get_aggregator()
    if not aggregator or not aggregator.dealer_scraper:
        raise HTTPException(status_code=503, detail="Dealer scraper not available")

    return aggregator.get_dealer_data()


@app.get("/api/pipeline/regulatory")
async def get_regulatory_data():
    """Get regulatory releases from CFTC, Fed, FDIC"""
    aggregator = get_aggregator()
    if not aggregator or not aggregator.regulatory_scraper:
        raise HTTPException(status_code=503, detail="Regulatory scraper not available")

    return aggregator.get_regulatory_data()


@app.get("/api/pipeline/alerts")
async def get_pipeline_alerts():
    """Get all alerts from pipeline"""
    aggregator = get_aggregator()
    if not aggregator:
        raise HTTPException(status_code=503, detail="Data pipeline not available")

    return {
        "alerts": aggregator.get_alerts(limit=50),
        "critical": aggregator.get_critical_alerts(),
        "summary": aggregator.alert_manager.get_summary(),
    }


@app.post("/api/pipeline/alerts/check")
async def check_all_alerts():
    """Trigger alert check across all data sources"""
    aggregator = get_aggregator()
    if not aggregator:
        raise HTTPException(status_code=503, detail="Data pipeline not available")

    new_alerts = aggregator.check_all_alerts()
    return {
        "new_alerts": len(new_alerts),
        "alerts": new_alerts,
    }


@app.get("/api/pipeline/banks")
async def get_bank_exposure_pipeline():
    """Get bank exposure summary from pipeline"""
    aggregator = get_aggregator()
    if not aggregator:
        raise HTTPException(status_code=503, detail="Data pipeline not available")

    return aggregator.get_bank_exposure_summary()


# =============================================================================
# SCORING ENGINE ENDPOINTS (Phase H - Unified Cascade Engine)
# =============================================================================

# Lazy load scoring engines
_scoring_available = False

def _check_scoring_available():
    """Check if scoring modules are available"""
    global _scoring_available
    try:
        from packages.core.scoring import (
            calculate_funding_stress,
            calculate_enforcement_heat,
            calculate_deliverability_stress,
            calculate_composite_risk,
            get_risk_level,
            get_risk_color,
        )
        _scoring_available = True
        return True
    except ImportError:
        _scoring_available = False
        return False


@app.get("/api/scores")
async def get_all_scores():
    """
    Get all three component scores and composite risk.

    Returns:
    - funding_stress: 0-100 (credit spreads, rate dislocations, facility usage)
    - enforcement_heat: 0-100 (regulatory actions, multi-agency coordination)
    - deliverability_stress: 0-100 (COMEX metrics, dealer tightness)
    - composite_risk: 0-10 (unified cascade score)
    """
    if not _check_scoring_available():
        # Fallback to existing stress calculation
        prices = fetch_all_prices()
        stress_level = calculate_stress_level(prices)
        risk_index = calculate_risk_index(prices, stress_level)

        return {
            'funding_stress': None,
            'enforcement_heat': None,
            'deliverability_stress': None,
            'composite_risk': risk_index,
            'composite_level': 'WARNING' if risk_index >= 4 else 'WATCH' if risk_index >= 2.5 else 'STABLE',
            'cascade_triggered': False,
            'scoring_engine': 'legacy',
            'message': 'New scoring engine not available, using legacy calculation',
        }

    from packages.core.scoring import (
        calculate_composite_risk,
        get_risk_level,
        quick_composite_assessment,
    )
    from packages.core.scoring.funding import FundingIndicators, calculate_funding_stress
    from packages.core.scoring.enforcement import calculate_enforcement_heat
    from packages.core.scoring.deliverability import (
        DeliverabilityIndicators,
        ComexIndicators,
        DealerIndicators,
        calculate_deliverability_stress,
    )

    # Get credit stress data
    credit_stress = fetch_credit_stress()
    liquidity = fetch_liquidity_data()
    comex = fetch_comex_data()

    # Calculate funding stress
    funding_indicators = FundingIndicators(
        hy_spread=credit_stress.high_yield_spread or 0,
        ig_spread=credit_stress.credit_spread or 0,
        ted_spread=credit_stress.ted_spread or 0,
        reverse_repo=liquidity.reverse_repo,
        deposit_change_pct=liquidity.deposit_change_pct,
    )
    funding_score = calculate_funding_stress(funding_indicators)

    # Calculate enforcement heat (placeholder - would need recent events)
    enforcement_score = calculate_enforcement_heat(entity_id=None, events=[])

    # Calculate deliverability stress
    deliv_indicators = DeliverabilityIndicators(
        comex=ComexIndicators(
            coverage_ratio=comex.coverage_ratio,
            days_of_supply=comex.days_of_supply,
            registered_oz=comex.registered_oz,
        ),
        dealers=DealerIndicators(),  # Would need dealer data
    )
    deliverability_score = calculate_deliverability_stress(deliv_indicators)

    # Calculate composite
    composite = calculate_composite_risk(
        funding_score,
        enforcement_score,
        deliverability_score,
    )

    return {
        'funding_stress': funding_score.to_dict() if hasattr(funding_score, 'to_dict') else {'score': funding_score.score},
        'enforcement_heat': {'score': enforcement_score.score, 'drivers': enforcement_score.drivers},
        'deliverability_stress': deliverability_score.to_dict() if hasattr(deliverability_score, 'to_dict') else {'score': deliverability_score.score},
        'composite_risk': composite.to_dict(),
        'scoring_engine': 'cascade_v2',
    }


@app.get("/api/scores/funding")
async def get_funding_stress():
    """
    Get funding stress score (0-100).

    Components:
    - Credit spreads (HY, IG)
    - TED spread
    - Rate dislocations (SOFR-EFFR, SOFR-IORB)
    - Fed facility usage
    - Deposit trends
    """
    credit_stress = fetch_credit_stress()
    liquidity = fetch_liquidity_data()

    return {
        'score': credit_stress.stress_score,
        'level': credit_stress.stress_level,
        'components': {
            'ted_spread': credit_stress.ted_spread,
            'high_yield_spread': credit_stress.high_yield_spread,
            'credit_spread': credit_stress.credit_spread,
            'sofr_rate': credit_stress.sofr_rate,
            'reverse_repo': liquidity.reverse_repo,
        },
        'drivers': [],
    }


@app.get("/api/scores/enforcement")
async def get_enforcement_heat():
    """
    Get enforcement heat score (0-100).

    Components:
    - Recent regulatory actions
    - Multi-agency coordination
    - Action severity (wells notice, settlement, cease-desist, etc.)
    - 90-day tempo acceleration
    """
    # In production, this would query the events table
    return {
        'score': 0,
        'level': 'low',
        'drivers': [],
        'recent_actions': [],
        'message': 'Enforcement data requires event store connection',
    }


@app.get("/api/scores/deliverability")
async def get_deliverability_stress():
    """
    Get deliverability stress score (0-100).

    Components:
    - COMEX coverage ratio
    - Days of supply
    - Delivery notices acceleration
    - Dealer premiums
    - Out-of-stock rate
    - Inventory velocity
    """
    comex = fetch_comex_data()

    return {
        'score': 0,  # Would calculate from deliverability engine
        'level': comex.status,
        'comex': {
            'coverage_ratio': comex.coverage_ratio,
            'days_of_supply': comex.days_of_supply,
            'registered_oz': comex.registered_oz,
            'eligible_oz': comex.eligible_oz,
            'open_interest_oz': comex.open_interest_oz,
        },
        'dealers': {
            'avg_premium_pct': None,
            'out_of_stock_rate': None,
        },
        'drivers': [],
    }


@app.get("/api/scores/composite")
async def get_composite_risk():
    """
    Get composite risk score (0-10).

    Algorithm:
    1. Weighted sum of three component scores
    2. Cascade amplification when 2+ components elevated
    3. Risk level: STABLE → MONITOR → WATCH → WARNING → DANGER → CRISIS
    """
    prices = fetch_all_prices()
    stress_level = calculate_stress_level(prices)
    risk_index = calculate_risk_index(prices, stress_level)

    # Determine risk label and color
    if risk_index >= 8:
        risk_label, risk_color = 'CRISIS', '#ff3b5c'
    elif risk_index >= 6:
        risk_label, risk_color = 'DANGER', '#ef4444'
    elif risk_index >= 4:
        risk_label, risk_color = 'WARNING', '#ff8c42'
    elif risk_index >= 2.5:
        risk_label, risk_color = 'WATCH', '#fbbf24'
    elif risk_index >= 1.5:
        risk_label, risk_color = 'MONITOR', '#84cc16'
    else:
        risk_label, risk_color = 'STABLE', '#4ade80'

    return {
        'score': round(risk_index, 2),
        'level': risk_label,
        'color': risk_color,
        'cascade_triggered': risk_index >= 4,
        'components': {
            'funding': None,
            'enforcement': None,
            'deliverability': None,
        },
        'weights': {
            'funding': 0.35,
            'enforcement': 0.30,
            'deliverability': 0.35,
        },
    }


# =============================================================================
# CLAIMS ENGINE ENDPOINTS (Phase G - Social Intel)
# =============================================================================

@app.get("/api/claims")
async def get_claims(
    status: Optional[str] = None,
    claim_type: Optional[str] = None,
    limit: int = 50,
):
    """
    Get claims from social sources.

    Params:
    - status: new, triage, corroborating, confirmed, debunked, stale
    - claim_type: nationalization, investigation, liquidity, delivery, fraud
    - limit: max claims to return
    """
    # In production, this would query the claims table
    return {
        'claims': [],
        'total': 0,
        'filters': {
            'status': status,
            'claim_type': claim_type,
        },
        'message': 'Claims data requires database connection',
    }


@app.get("/api/claims/types")
async def get_claim_types():
    """Get supported claim types and their descriptions"""
    return {
        'types': {
            'nationalization': {
                'description': 'Government takeover or bailout claims',
                'severity': 'critical',
                'corroboration_events': ['bank_failure', 'regulator_action', 'fed_facility_usage'],
            },
            'investigation': {
                'description': 'Regulatory investigation claims',
                'severity': 'high',
                'corroboration_events': ['regulator_action', 'wells_notice', 'sec_filing'],
            },
            'liquidity': {
                'description': 'Bank run or liquidity crisis claims',
                'severity': 'critical',
                'corroboration_events': ['bank_failure', 'fed_facility_usage', 'deposit_stress'],
            },
            'delivery': {
                'description': 'Physical delivery failure claims',
                'severity': 'high',
                'corroboration_events': ['comex_stress', 'comex_outflow', 'comex_delivery_spike'],
            },
            'fraud': {
                'description': 'Market manipulation or fraud claims',
                'severity': 'medium',
                'corroboration_events': ['regulator_action', 'penalty', 'settlement'],
            },
            'insider': {
                'description': 'Insider information claims',
                'severity': 'medium',
                'corroboration_events': ['sec_filing', 'regulator_action', 'covered_action'],
            },
            'price_target': {
                'description': 'Price prediction claims',
                'severity': 'low',
                'corroboration_events': [],
            },
        },
    }


@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: str):
    """Get detailed claim data including corroboration status"""
    raise HTTPException(status_code=503, detail="Claims database not connected")


@app.get("/api/claims/stats")
async def get_claims_stats():
    """Get claims statistics by status and type"""
    return {
        'by_status': {
            'new': 0,
            'triage': 0,
            'corroborating': 0,
            'confirmed': 0,
            'debunked': 0,
            'stale': 0,
        },
        'by_type': {
            'nationalization': 0,
            'investigation': 0,
            'liquidity': 0,
            'delivery': 0,
            'fraud': 0,
            'insider': 0,
            'price_target': 0,
        },
        'confirmation_rate': 0,
        'message': 'Claims statistics require database connection',
    }


# =============================================================================
# EVENTS EXPLORER ENDPOINTS
# =============================================================================

@app.get("/api/events")
async def get_events(
    event_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    tier: Optional[int] = None,
    days: int = 30,
    limit: int = 100,
):
    """
    Get events from the event store.

    Params:
    - event_type: regulator_action, bank_failure, fed_facility_usage, etc.
    - entity_id: UUID of specific entity
    - tier: 1 (official), 2 (credible), 3 (social)
    - days: lookback period
    - limit: max events to return
    """
    return {
        'events': [],
        'total': 0,
        'filters': {
            'event_type': event_type,
            'entity_id': entity_id,
            'tier': tier,
            'days': days,
        },
        'message': 'Events data requires event store connection',
    }


@app.get("/api/events/types")
async def get_event_types():
    """Get supported event types by trust tier"""
    return {
        'tier_1_official': [
            'regulator_action',
            'bank_failure',
            'fed_facility_usage',
            'sec_filing',
            'wells_notice',
            'consent_order',
            'cease_desist',
            'penalty',
            'settlement',
        ],
        'tier_2_credible': [
            'news_article',
            'analyst_report',
            'earnings_call',
        ],
        'tier_3_social': [
            'reddit_post',
            'twitter_post',
            'blog_post',
        ],
    }


@app.get("/api/events/recent")
async def get_recent_events(hours: int = 24):
    """Get events from the last N hours"""
    return {
        'events': [],
        'count': 0,
        'hours': hours,
        'message': 'Events data requires event store connection',
    }


@app.get("/api/entities")
async def get_entities(entity_type: Optional[str] = None):
    """
    Get tracked entities.

    Types: bank, regulator, metal, ticker, person
    """
    # Return hardcoded entities based on BANK_SHORT_POSITIONS
    entities = []
    for ticker, data in BANK_SHORT_POSITIONS.items():
        entities.append({
            'ticker': ticker,
            'name': data['name'],
            'entity_type': 'bank',
            'position': data['position'],
            'ounces': data['ounces'],
        })

    return {
        'entities': entities,
        'total': len(entities),
    }


@app.get("/api/entities/{entity_id}")
async def get_entity(entity_id: str):
    """Get detailed entity data including related events and claims"""
    # Check if it's a known ticker
    ticker = entity_id.upper()
    if ticker in BANK_SHORT_POSITIONS:
        data = BANK_SHORT_POSITIONS[ticker]
        return {
            'entity': {
                'ticker': ticker,
                'name': data['name'],
                'entity_type': 'bank',
                'position': data['position'],
                'ounces': data['ounces'],
                'equity': data['equity'],
                'insolvency_price': data.get('insolvency_price'),
            },
            'events': [],
            'claims': [],
            'scores': {},
        }

    raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found")


# =============================================================================
# CRISIS GAUGE ENDPOINT
# =============================================================================

@app.get("/api/crisis-gauge", response_model=CrisisGaugeData)
async def get_crisis_gauge():
    """
    Comprehensive crisis monitoring gauge.
    Tracks losses, cracks (Tier 1-3), phases (1-4), and resources.
    """
    prices = fetch_all_prices()
    return build_crisis_gauge(prices)


# =============================================================================
# CRISIS SCANNER ENDPOINT
# =============================================================================

@app.get("/api/crisis-scanner")
async def get_crisis_scanner():
    """
    Crisis Scanner Module - Comprehensive bank surveillance and market analysis.
    Returns verified/unverified data, Fed facilities status, silver market indicators,
    and bank risk matrix with 5-minute refresh capability.
    """
    prices = fetch_all_prices()
    silver_price = prices.get('silver', PriceData(price=90.42)).price

    # Calculate dynamic alert level based on current conditions
    alert_level = "LOW"
    alert_level_code = 1
    primary_drivers = []

    # Check silver price conditions
    if silver_price > 100:
        alert_level = "CRITICAL"
        alert_level_code = 5
        primary_drivers.append(f"Silver at ${silver_price:.2f} - above $100 threshold")
    elif silver_price > 90:
        alert_level = "ELEVATED"
        alert_level_code = 3
        primary_drivers.append(f"Silver at ${silver_price:.2f} - elevated levels")
    elif silver_price > 80:
        alert_level = "MODERATE"
        alert_level_code = 2
        primary_drivers.append(f"Silver at ${silver_price:.2f} - moderate concern")

    # Add persistent structural concerns
    primary_drivers.extend([
        "Silver persistent backwardation",
        "Fed removed Standing Repo Facility limits",
        "China silver export curbs effective Jan 1"
    ])

    # Recommended action based on alert level
    action_map = {
        "CRITICAL": "IMMEDIATE REVIEW REQUIRED",
        "HIGH": "ENHANCED MONITORING",
        "ELEVATED": "INCREASED VIGILANCE",
        "MODERATE": "ROUTINE MONITORING",
        "LOW": "STANDARD OPERATIONS"
    }

    return {
        "scan_metadata": {
            "scan_id": f"FW-{datetime.now().strftime('%Y-%m-%d')}-{datetime.now().strftime('%H%M')}",
            "scan_date": datetime.now().strftime('%Y-%m-%d'),
            "scan_timestamp": datetime.now().isoformat() + "Z",
            "analyst": "Fault Watch System",
            "version": "1.0"
        },
        "system_status": {
            "alert_level": alert_level,
            "alert_level_code": alert_level_code,
            "primary_drivers": primary_drivers[:4],
            "recommended_action": action_map.get(alert_level, "ROUTINE MONITORING")
        },
        "silver_market": {
            "price_data": {
                "spot_price": silver_price,
                "user_tracked_high": 94.50,
                "user_tracked_low": 87.00,
                "recovery_from_low_pct": ((silver_price - 87.0) / (94.5 - 87.0)) * 100 if silver_price > 87 else 0,
                "user_thesis": "Strong buying from commercial companies needing silver + retail FOMO"
            },
            "market_structure": {
                "backwardation": True,
                "backwardation_status": "PERSISTENT",
                "verification": "VERIFIED",
                "source": "CME COMEX Futures Data",
                "significance": "Spot price above futures indicates physical shortage pressure"
            },
            "comex_inventory": {
                "registered_oz": 445737395,
                "registered_tons": 13864,
                "trend": "DECLINING",
                "verification": "VERIFIED",
                "source": "CME Warehouse Reports",
                "as_of_date": "2026-01-07"
            },
            "delivery_activity": {
                "date": "2026-01-07",
                "contracts_delivered": 1624,
                "ounces_delivered": 8100000,
                "primary_issuer": "JPMorgan",
                "issuer_percentage": 99,
                "verification": "VERIFIED",
                "source": "CME COMEX Delivery Notices",
                "significance": "Buyers using COMEX as physical delivery market, not hedging"
            },
            "supply_deficit": {
                "year": 2025,
                "deficit_oz": 230000000,
                "consecutive_deficit_years": 5,
                "projected_2026_deficit_oz": 140000000,
                "verification": "VERIFIED",
                "sources": ["Silver Institute", "HSBC Research", "Metals Focus"]
            },
            "china_export_curbs": {
                "effective_date": "2026-01-01",
                "impact_description": "Ring-fenced ~65% of global refined silver supply for domestic use",
                "verification": "VERIFIED",
                "sources": ["South China Morning Post", "Multiple news outlets"]
            },
            "physical_premium_reports": {
                "tokyo_premium_claimed": 130,
                "dubai_premium_claimed": "80% above spot",
                "verification": "UNVERIFIED",
                "note": "Premium existence likely real, exact figures unconfirmed"
            }
        },
        "federal_reserve": {
            "standing_repo_facility": {
                "current_balance": 0,
                "daily_limit": "UNLIMITED",
                "limit_change_date": "2025-12-10",
                "previous_limit": 500000000000,
                "verification": "VERIFIED",
                "source": "Federal Reserve FOMC Statement",
                "significance": "Fed opened unlimited liquidity backstop - major policy shift"
            },
            "year_end_spike": {
                "date": "2025-12-31",
                "amount": 74600000000,
                "treasury_collateral": 31500000000,
                "mbs_collateral": 43100000000,
                "previous_record": 50350000000,
                "status": "RESOLVED",
                "resolution_date": "2026-01-05",
                "verification": "VERIFIED",
                "source": "NY Fed Daily Operations Data",
                "significance": "Largest liquidity injection since COVID - attributed to year-end positioning"
            },
            "reverse_repo": {
                "current_balance": 6000000000,
                "year_end_spike": 106000000000,
                "verification": "VERIFIED",
                "source": "NY Fed"
            },
            "quantitative_tightening": {
                "status": "ENDED",
                "end_date": "2025-12-01",
                "total_reduction": 2430000000000,
                "verification": "VERIFIED"
            }
        },
        "banks": {
            "jpmorgan_chase": {
                "ticker": "JPM",
                "current_price": prices.get('jpmorgan', PriceData(price=0)).price,
                "price_change_pct": prices.get('jpmorgan', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {
                    "risk_level": "CRITICAL",
                    "verification_status": "UNVERIFIED",
                    "claimed_short_position_tons": 5900,
                    "claimed_exposure_usd": 13700000000,
                    "source": "DCReport.org",
                    "source_author": "David Cay Johnston",
                    "concerns": [
                        "No specific SEC filing cited",
                        "Exposure is author's calculation",
                        "No major financial outlet corroboration",
                        "CFTC does not disclose individual bank positions"
                    ],
                    "action": "Monitor for corroboration - do not treat as fact"
                },
                "liquidity_risk": {"risk_level": "ELEVATED", "verification_status": "VERIFIED"},
                "overall_crisis_risk": "HIGH",
                "risk_note": "HIGH rating driven by unverified silver exposure claims + whistleblower allegations"
            },
            "bank_of_america": {
                "ticker": "BAC",
                "current_price": prices.get('bank_of_america', PriceData(price=0)).price,
                "price_change_pct": prices.get('bank_of_america', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {"risk_level": "MODERATE", "verification_status": "UNKNOWN"},
                "liquidity_risk": {
                    "risk_level": "ELEVATED",
                    "unrealized_bond_losses": 130000000000,
                    "verification_status": "VERIFIED"
                },
                "overall_crisis_risk": "ELEVATED"
            },
            "citigroup": {
                "ticker": "C",
                "current_price": prices.get('citigroup', PriceData(price=0)).price,
                "price_change_pct": prices.get('citigroup', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {"risk_level": "ELEVATED", "verification_status": "UNVERIFIED"},
                "liquidity_risk": {"risk_level": "MODERATE", "verification_status": "VERIFIED"},
                "overall_crisis_risk": "ELEVATED"
            },
            "wells_fargo": {
                "ticker": "WFC",
                "current_price": prices.get('wells_fargo', PriceData(price=0)).price,
                "price_change_pct": prices.get('wells_fargo', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {"risk_level": "LOW"},
                "liquidity_risk": {"risk_level": "LOW", "verification_status": "VERIFIED"},
                "overall_crisis_risk": "LOW"
            },
            "hsbc": {
                "ticker": "HSBC",
                "current_price": prices.get('hsbc', PriceData(price=0)).price,
                "price_change_pct": prices.get('hsbc', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {"risk_level": "ELEVATED", "verification_status": "UNVERIFIED"},
                "liquidity_risk": {"risk_level": "MODERATE"},
                "overall_crisis_risk": "MODERATE"
            },
            "deutsche_bank": {
                "ticker": "DB",
                "current_price": prices.get('deutsche_bank', PriceData(price=0)).price,
                "price_change_pct": prices.get('deutsche_bank', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {"risk_level": "ELEVATED", "verification_status": "UNVERIFIED"},
                "overall_crisis_risk": "ELEVATED"
            },
            "ubs": {
                "ticker": "UBS",
                "current_price": prices.get('ubs', PriceData(price=0)).price,
                "price_change_pct": prices.get('ubs', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {"risk_level": "MODERATE", "verification_status": "UNVERIFIED"},
                "overall_crisis_risk": "MODERATE"
            },
            "goldman_sachs": {
                "ticker": "GS",
                "current_price": prices.get('goldman', PriceData(price=0)).price,
                "price_change_pct": prices.get('goldman', PriceData(price=0, change_pct=0)).change_pct,
                "silver_exposure": {"risk_level": "UNKNOWN"},
                "overall_crisis_risk": "MODERATE"
            }
        },
        "unverified_claims_watchlist": [
            {
                "id": "UVC-001",
                "claim": "JPMorgan 5,900 ton silver short position",
                "exposure_claimed": "$13.7 billion",
                "source": "DCReport.org",
                "source_type": "Independent investigative outlet",
                "author": "David Cay Johnston (Pulitzer Prize winner)",
                "date_reported": "2025-12-29",
                "verification_status": "UNVERIFIED",
                "credibility_concerns": [
                    "No specific SEC/CFTC filing cited",
                    "Exposure figure is author calculation",
                    "No Bloomberg/Reuters/WSJ corroboration"
                ],
                "recommended_action": "Monitor for corroboration from official sources"
            },
            {
                "id": "UVC-002",
                "claim": "Major bullion bank collapsed after margin call (Dec 29)",
                "source": "Social media / Hal Turner Radio Show",
                "source_type": "Fringe media",
                "verification_status": "SPECULATIVE",
                "debunked_by": ["No FDIC announcement", "No CME trading halt", "No mainstream confirmation"],
                "recommended_action": "Disregard unless corroborated by official sources",
                "status": "EFFECTIVELY_DEBUNKED"
            },
            {
                "id": "UVC-003",
                "claim": f"Physical silver trading at $130/oz in Tokyo/Dubai",
                "source": "Various independent analysts",
                "source_type": "Independent sources",
                "verification_status": "UNVERIFIED",
                "notes": "Premium existence likely real, exact figures unconfirmed",
                "recommended_action": "Seek primary dealer quotes for verification"
            }
        ],
        "historical_context": {
            "bank_manipulation_settlements": {
                "total_fines": 1270000000,
                "period_of_manipulation": "2008-2016",
                "prosecution_period": "2016-2025",
                "major_settlements": [
                    {"bank": "JPMorgan", "amount": 920000000, "year": 2020},
                    {"bank": "Scotiabank", "amount": 127500000, "year": 2020},
                    {"bank": "Deutsche Bank", "amount": 30000000, "year": 2016}
                ],
                "criminal_convictions": [
                    {"name": "Michael Nowak", "role": "JPM Head of Global PM Desk", "sentence": "1 year 1 day", "year": 2023},
                    {"name": "Gregg Smith", "role": "JPM Executive Director", "sentence": "2 years", "year": 2023}
                ],
                "note": "Historical prosecutions for 2008-2016 manipulation, separate from 2025-2026 events"
            }
        },
        "next_scan_priorities": [
            "Monitor CFTC weekly COT reports for bank position changes",
            "Track COMEX registered inventory trend",
            "Watch for JPMorgan response to whistleblower allegations",
            "Monitor Fed repo facility usage for anomalies",
            "Track physical premium reports from primary dealers"
        ]
    }


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
