"""
FAULT.WATCH v4.0 - COMPLETE CRISIS MONITOR
===========================================
Adaptive Systemic Risk Monitoring System
With Morgan Stanley Silver Short Tracking

TABS:
1. Dashboard - Main overview with all indicators
2. MS Collapse - Morgan Stanley tracking & countdown
3. Bank Exposure - All at-risk banks PM derivatives
4. Fed Response - Emergency lending tracker
5. Domino Effects - Cascade tracker
6. My Positions - Trade tracking & P/L calculator
7. Scenarios - Detailed scenario analysis
8. Content - TikTok content generation & export

Run with: streamlit run fault_watch_v4.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf
import requests
import json
import time

from content_generator import ContentGenerator, TemplateType
from content_triggers import TriggerManager, TriggerConfig

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(page_title="fault.watch", page_icon="⚠️", layout="wide")

# =============================================================================
# CONSTANTS
# =============================================================================
SEC_DEADLINE = datetime(2026, 2, 15, 16, 0, 0)
LLOYDS_DEADLINE = datetime(2026, 1, 31, 23, 59, 59)  # Lloyd's stops insuring Citi

# Bank Silver Short Positions (in ounces)
MS_SHORT_POSITION_OZ = 5_900_000_000      # Morgan Stanley
CITI_SHORT_POSITION_OZ = 6_340_000_000    # Citigroup - LARGER than MS!
JPM_LONG_POSITION_OZ = 750_000_000        # JPMorgan FLIPPED to LONG (was 200M short)

# Bank Short Position Details
BANK_SHORT_POSITIONS = {
    'C': {
        'name': 'Citigroup',
        'position': 'SHORT',
        'ounces': 6_340_000_000,
        'equity': 175_000_000_000,
        'insolvency_price': 80,  # Price at which they become insolvent
        'note': 'LARGEST short - Lloyd\'s insurance deadline Jan 31'
    },
    'MS': {
        'name': 'Morgan Stanley',
        'position': 'SHORT',
        'ounces': 5_900_000_000,
        'equity': 100_000_000_000,
        'insolvency_price': 47,
        'note': 'SEC deadline Feb 15'
    },
    'JPM': {
        'name': 'JPMorgan',
        'position': 'LONG',
        'ounces': 750_000_000,
        'equity': 330_000_000_000,
        'note': 'FLIPPED from 200M short to 750M LONG (Jun-Oct 2025)'
    },
}

# Bank PM Derivatives Exposure (Q3 2025 OCC Data)
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

# Fed Emergency Lending History - UPDATED TO $51B
FED_REPO_HISTORY = [
    {'date': '2025-12-26', 'amount': 17.25, 'note': 'Dec 26-27 repo'},
    {'date': '2025-12-27', 'amount': 34.0, 'note': 'Dec 27-28 overnight - MASSIVE'},
    {'date': '2025-12-30', 'amount': 0, 'note': 'Holiday week'},
]
FED_REPO_TOTAL = 51.25  # Total: $17.25B + $34B = ~$51B

# Historical Bailout Comparisons
BAILOUT_HISTORY = [
    {'event': 'Bear Stearns 2008', 'amount': 30, 'outcome': 'Sold to JPM'},
    {'event': 'AIG 2008', 'amount': 182, 'outcome': 'Nationalized'},
    {'event': 'Citigroup 2008', 'amount': 45, 'outcome': 'Survived + $306B guarantees'},
    {'event': 'Bank of America 2008', 'amount': 45, 'outcome': 'Survived + $118B guarantees'},
    {'event': 'TARP Total 2008', 'amount': 700, 'outcome': 'System stabilized'},
    {'event': 'Fed QE 2008-2014', 'amount': 3500, 'outcome': 'Markets recovered'},
    {'event': 'Fed QE 2020', 'amount': 4500, 'outcome': 'COVID recovery'},
]

THRESHOLDS = {
    'vix': {'warning': 25, 'critical': 35},
    'silver': {'warning': 90, 'critical': 100},
    'gold': {'warning': 4700, 'critical': 5000},
    'kre_weekly': {'warning': -5, 'critical': -10},
    'hyg_weekly': {'warning': -3, 'critical': -5},
    'dollar_index': {'warning': 100, 'critical': 95},
    'gold_silver_ratio': {'warning': 50, 'critical': 40},
    'bitcoin': {'buy_zone': 80000, 'strong_buy': 60000},
    'ms_daily': {'warning': -3, 'critical': -7},
    'ms_price': {'warning': 100, 'critical': 80},
    'fed_repo': {'warning': 20, 'critical': 50},  # billions
}

# =============================================================================
# CUSTOM CSS - NEWS/MEDIA DESIGN SYSTEM
# =============================================================================
st.markdown("""
<style>
    /* ===========================================
       NEWS/MEDIA DESIGN SYSTEM - CNN/Bloomberg Style
       =========================================== */

    /* Base Theme - Deep Black with High Contrast */
    .stApp { background-color: #0d0d0d; }
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #b0b0b0 !important; text-transform: uppercase; letter-spacing: 1px; font-size: 11px !important; }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 700 !important; }

    /* ===========================================
       TYPOGRAPHY HIERARCHY
       =========================================== */
    .text-hero {
        font-size: 72px;
        font-weight: 900;
        color: #ffffff;
        line-height: 1;
    }
    .text-headline {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .text-subhead {
        font-size: 20px;
        font-weight: 600;
        color: #e0e0e0;
    }
    .text-body {
        font-size: 16px;
        font-weight: 400;
        color: #cccccc;
    }
    .text-caption {
        font-size: 12px;
        font-weight: 400;
        color: #888888;
    }
    .text-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #666666;
    }

    /* ===========================================
       BREAKING NEWS BANNER
       =========================================== */
    .breaking-banner {
        background: linear-gradient(90deg, #e31837 0%, #b71c1c 100%);
        padding: 12px 20px;
        margin: -20px -20px 20px -20px;
        display: flex;
        align-items: center;
        gap: 15px;
        animation: pulse-banner 2s ease-in-out infinite;
        box-shadow: 0 4px 20px rgba(227, 24, 55, 0.4);
    }
    .breaking-label {
        background: #ffffff;
        color: #e31837;
        padding: 6px 12px;
        font-weight: 900;
        font-size: 14px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .breaking-text {
        color: #ffffff;
        font-size: 16px;
        font-weight: 600;
        flex: 1;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    @keyframes pulse-banner {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }

    /* ===========================================
       ALERT CLASSES - DRAMATIC STYLING
       =========================================== */
    .alert-critical {
        background: linear-gradient(135deg, rgba(227,24,55,0.25) 0%, rgba(183,28,28,0.15) 100%);
        border: 2px solid #e31837;
        border-left: 6px solid #e31837;
        padding: 18px 20px;
        margin: 15px 0;
        animation: alert-pulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 20px rgba(227,24,55,0.3);
    }
    .alert-critical strong {
        color: #ff4d6a;
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .alert-warning {
        background: linear-gradient(135deg, rgba(255,195,0,0.2) 0%, rgba(255,140,0,0.1) 100%);
        border: 2px solid #ffc300;
        border-left: 6px solid #ffc300;
        padding: 18px 20px;
        margin: 15px 0;
    }
    .alert-warning strong {
        color: #ffc300;
        font-size: 15px;
        text-transform: uppercase;
    }
    .alert-info {
        background: linear-gradient(135deg, rgba(0,102,204,0.2) 0%, rgba(0,71,171,0.1) 100%);
        border: 2px solid #0066cc;
        border-left: 6px solid #0066cc;
        padding: 18px 20px;
        margin: 15px 0;
    }
    @keyframes alert-pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(227,24,55,0.3); }
        50% { box-shadow: 0 0 35px rgba(227,24,55,0.5); }
    }

    /* ===========================================
       HEADLINES - NEWS TYPOGRAPHY
       =========================================== */
    .headline-primary {
        font-size: 32px;
        font-weight: 900;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 1px;
        line-height: 1.2;
        margin-bottom: 10px;
    }
    .headline-secondary {
        font-size: 24px;
        font-weight: 700;
        color: #e0e0e0;
        letter-spacing: 0.5px;
    }
    .headline-ticker {
        font-size: 14px;
        font-weight: 600;
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 2px;
        white-space: nowrap;
        overflow: hidden;
    }

    /* ===========================================
       COUNTDOWN BOX - NEWS URGENCY STYLE
       =========================================== */
    .countdown-box {
        background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
        border: 3px solid #e31837;
        padding: 30px;
        text-align: center;
        margin: 25px 0;
        position: relative;
        box-shadow: 0 0 40px rgba(227,24,55,0.3), inset 0 0 60px rgba(227,24,55,0.1);
    }
    .countdown-box::before {
        content: 'DEADLINE';
        position: absolute;
        top: -14px;
        left: 50%;
        transform: translateX(-50%);
        background: #e31837;
        color: #ffffff;
        padding: 5px 20px;
        font-weight: 900;
        font-size: 12px;
        letter-spacing: 3px;
    }
    .countdown-number {
        font-size: 72px;
        font-weight: 900;
        color: #ffffff;
        text-shadow: 0 0 30px rgba(227,24,55,0.8);
        letter-spacing: 4px;
        animation: countdown-glow 2s ease-in-out infinite;
    }
    .countdown-label {
        color: #b0b0b0;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-top: 5px;
    }
    .countdown-urgent {
        color: #ff4d6a;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 15px;
        animation: flash 1s ease-in-out infinite;
    }
    @keyframes countdown-glow {
        0%, 100% { text-shadow: 0 0 30px rgba(227,24,55,0.8); }
        50% { text-shadow: 0 0 50px rgba(227,24,55,1), 0 0 80px rgba(227,24,55,0.6); }
    }
    @keyframes flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* ===========================================
       CARDS - SHARP NEWS STYLE
       =========================================== */
    .metric-card {
        background: #141414;
        border: 1px solid #2a2a2a;
        border-left: 4px solid #e31837;
        padding: 18px;
        margin: 8px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .scenario-card {
        text-align: center;
        padding: 18px;
        background: #141414;
        border: 1px solid #2a2a2a;
        margin: 8px;
        transition: all 0.3s ease;
    }
    .scenario-card:hover {
        border-color: #e31837;
        box-shadow: 0 0 20px rgba(227,24,55,0.2);
    }
    .bank-card {
        background: #141414;
        padding: 18px;
        margin: 12px 0;
        border: 1px solid #2a2a2a;
        border-left: 5px solid #e31837;
        box-shadow: 0 2px 15px rgba(0,0,0,0.3);
    }
    .fed-card {
        background: linear-gradient(135deg, #141414 0%, #1a2a3a 100%);
        padding: 25px;
        margin: 15px 0;
        border: 2px solid #0066cc;
        box-shadow: 0 4px 20px rgba(0,102,204,0.2);
    }
    .domino-box {
        background: #141414;
        padding: 15px;
        margin: 8px 0;
        border: 1px solid #2a2a2a;
        border-left: 5px solid #0066cc;
    }

    /* ===========================================
       STRESS METER - DRAMATIC
       =========================================== */
    .stress-meter {
        background: #141414;
        border: 1px solid #2a2a2a;
        padding: 20px;
        margin: 15px 0;
    }

    /* ===========================================
       PROGRESS BARS
       =========================================== */
    .bailout-bar {
        background: #1a1a1a;
        height: 28px;
        margin: 8px 0;
        overflow: hidden;
        border: 1px solid #2a2a2a;
    }

    /* ===========================================
       UTILITY ANIMATIONS
       =========================================== */
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# BREAKING NEWS HEADER
# =============================================================================

def render_breaking_header(alerts, risk_index, countdown):
    """Render CNN-style breaking news banner at the top of the app"""
    # Calculate Lloyd's countdown
    lloyds_countdown = calculate_lloyds_countdown()

    # Determine if we should show breaking banner
    has_critical = any(a['level'] == 'critical' for a in alerts)
    sec_deadline_urgent = countdown['days'] < 7 and not countdown['expired']
    lloyds_deadline_urgent = lloyds_countdown['days'] < 7 and not lloyds_countdown['expired']
    deadline_urgent = sec_deadline_urgent or lloyds_deadline_urgent

    if risk_index >= 7 or has_critical or deadline_urgent:
        # Get the most critical alert message
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        if critical_alerts:
            headline = critical_alerts[0]['title'].replace('🚨 ', '').replace('⚠️ ', '')
        elif lloyds_deadline_urgent:
            headline = f"LLOYD'S DEADLINE IN {lloyds_countdown['days']} DAYS - CITI LOSES INSURANCE JAN 31"
        elif sec_deadline_urgent:
            headline = f"SEC DEADLINE IN {countdown['days']} DAYS - 12.24B OZ SILVER SHORTS MUST CLOSE"
        else:
            headline = "SYSTEMIC RISK ELEVATED - CITI + MS COMBINED 12.24B OZ SHORT"

        label = "BREAKING" if risk_index >= 8 or has_critical else "ALERT"

        st.markdown(f'''
        <div class="breaking-banner">
            <span class="breaking-label">{label}</span>
            <span class="breaking-text">{headline}</span>
        </div>
        ''', unsafe_allow_html=True)

# =============================================================================
# DATA FETCHING
# =============================================================================

@st.cache_data(ttl=60)
def fetch_all_prices():
    """Fetch real-time prices from multiple sources"""
    prices = {}
    
    yf_tickers = {
        # Market indices
        'SPY': 'sp500',
        '^VIX': 'vix',
        'TLT': 'long_treasury',
        'DX-Y.NYB': 'dollar_index',
        
        # Precious metals
        'GC=F': 'gold',
        'SI=F': 'silver',
        'GDX': 'gold_miners',
        'SILJ': 'silver_miners',
        'SLV': 'slv',
        
        # US Banks
        'MS': 'morgan_stanley',
        'JPM': 'jpmorgan',
        'C': 'citibank',
        'BAC': 'bank_of_america',
        'GS': 'goldman',
        'WFC': 'wells_fargo',
        
        # European Banks
        'HSBC': 'hsbc',
        'DB': 'deutsche_bank',
        'UBS': 'ubs',
        'BCS': 'barclays',
        'BNS': 'scotiabank',
        
        # Stress indicators
        'KRE': 'regional_banks',
        'XLF': 'financials',
        'HYG': 'high_yield',
        
        # Other
        'XLE': 'energy',
        '^TNX': 'treasury_10y',
    }
    
    for ticker, name in yf_tickers.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period='5d')
            if not hist.empty and len(hist) >= 1:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                first = hist['Close'].iloc[0]
                prices[name] = {
                    'price': current,
                    'prev_close': prev,
                    'change_pct': ((current / prev) - 1) * 100 if prev != 0 else 0,
                    'week_change': ((current / first) - 1) * 100 if first != 0 else 0,
                }
        except:
            continue
    
    # CoinGecko for crypto
    try:
        resp = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin,ethereum', 'vs_currencies': 'usd', 'include_24hr_change': 'true'},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if 'bitcoin' in data:
                prices['bitcoin'] = {
                    'price': data['bitcoin']['usd'],
                    'change_pct': data['bitcoin'].get('usd_24h_change', 0),
                    'week_change': 0
                }
    except:
        prices['bitcoin'] = {'price': 91000, 'change_pct': 0, 'week_change': 0}
    
    # Gold/Silver Ratio
    if 'gold' in prices and 'silver' in prices and prices['silver']['price'] > 0:
        prices['gold_silver_ratio'] = {
            'price': prices['gold']['price'] / prices['silver']['price'],
            'change_pct': 0
        }
    
    return prices

# =============================================================================
# CALCULATION FUNCTIONS
# =============================================================================

def calculate_countdown():
    """Calculate time remaining to SEC deadline"""
    now = datetime.now()
    remaining = SEC_DEADLINE - now
    if remaining.total_seconds() <= 0:
        return {'days': 0, 'hours': 0, 'minutes': 0, 'expired': True}
    return {
        'days': remaining.days,
        'hours': remaining.seconds // 3600,
        'minutes': (remaining.seconds % 3600) // 60,
        'expired': False
    }

def calculate_lloyds_countdown():
    """Calculate time remaining to Lloyd's insurance deadline (Jan 31, 2026)"""
    now = datetime.now()
    remaining = LLOYDS_DEADLINE - now
    if remaining.total_seconds() <= 0:
        return {'days': 0, 'hours': 0, 'minutes': 0, 'expired': True}
    return {
        'days': remaining.days,
        'hours': remaining.seconds // 3600,
        'minutes': (remaining.seconds % 3600) // 60,
        'expired': False
    }

def calculate_citi_exposure(silver_price, entry_price=30):
    """Calculate Citigroup theoretical exposure and losses from short position"""
    position_oz = CITI_SHORT_POSITION_OZ
    current_value = position_oz * silver_price
    entry_value = position_oz * entry_price
    paper_loss = current_value - entry_value
    citi_equity = 175_000_000_000
    return {
        'position_oz': position_oz,
        'current_value': current_value,
        'paper_loss': paper_loss,
        'loss_vs_equity': paper_loss / citi_equity,
        'insolvent': paper_loss > citi_equity,
        'insolvency_multiple': paper_loss / citi_equity if paper_loss > citi_equity else 0
    }

def calculate_ms_exposure(silver_price, entry_price=30):
    """Calculate MS theoretical exposure and losses"""
    position_oz = MS_SHORT_POSITION_OZ
    current_value = position_oz * silver_price
    entry_value = position_oz * entry_price
    paper_loss = current_value - entry_value
    ms_equity = 100_000_000_000
    return {
        'position_oz': position_oz,
        'current_value': current_value,
        'paper_loss': paper_loss,
        'loss_vs_equity': paper_loss / ms_equity,
        'insolvent': paper_loss > ms_equity,
        'insolvency_multiple': paper_loss / ms_equity if paper_loss > ms_equity else 0
    }

def calculate_ms_stress_level(prices):
    """Calculate MS stress level 0-100"""
    stress = 0
    
    ms = prices.get('morgan_stanley', {})
    ms_daily = ms.get('change_pct', 0)
    ms_weekly = ms.get('week_change', 0)
    
    if ms_daily < -10: stress += 30
    elif ms_daily < -5: stress += 20
    elif ms_daily < -3: stress += 10
    elif ms_daily < 0: stress += 5
    
    if ms_weekly < -15: stress += 25
    elif ms_weekly < -10: stress += 15
    elif ms_weekly < -5: stress += 10
    
    silver = prices.get('silver', {}).get('price', 80)
    if silver > 120: stress += 25
    elif silver > 100: stress += 20
    elif silver > 90: stress += 10
    elif silver > 85: stress += 5
    
    vix = prices.get('vix', {}).get('price', 15)
    if vix > 40: stress += 15
    elif vix > 30: stress += 10
    elif vix > 25: stress += 5
    
    kre_weekly = prices.get('regional_banks', {}).get('week_change', 0)
    if kre_weekly < -10: stress += 15
    elif kre_weekly < -5: stress += 10
    
    return min(stress, 100)

def calculate_bank_risk_scores(prices):
    """Calculate risk score for each bank"""
    risk_scores = {}
    
    for key, bank in BANK_PM_EXPOSURE.items():
        ticker_key = bank['ticker'].lower()
        if ticker_key == 'jpm':
            ticker_key = 'jpmorgan'
        elif ticker_key == 'c':
            ticker_key = 'citibank'
        elif ticker_key == 'bac':
            ticker_key = 'bank_of_america'
        elif ticker_key == 'gs':
            ticker_key = 'goldman'
        elif ticker_key == 'db':
            ticker_key = 'deutsche_bank'
        
        price_data = prices.get(ticker_key, {})
        daily_change = price_data.get('change_pct', 0)
        weekly_change = price_data.get('week_change', 0)
        current_price = price_data.get('price', 0)
        
        # Calculate risk score
        score = 50  # Base score
        
        # PM exposure factor
        if bank['pm_derivatives']:
            exposure_ratio = bank['pm_derivatives'] / bank['equity']
            score += min(exposure_ratio * 20, 30)
        elif bank.get('note') and 'manipulation' in bank.get('note', '').lower():
            score += 15  # History of issues
        
        # Price action
        if daily_change < -10:
            score += 25
        elif daily_change < -5:
            score += 15
        elif daily_change < -3:
            score += 10
        
        if weekly_change < -15:
            score += 20
        elif weekly_change < -10:
            score += 10
        
        risk_scores[key] = {
            'score': min(score, 100),
            'daily_change': daily_change,
            'weekly_change': weekly_change,
            'price': current_price,
        }
    
    return risk_scores

def calculate_fed_response_adequacy(silver_price):
    """Calculate if Fed response is adequate for the crisis"""
    # Current known Fed repo - UPDATED TO $51B
    current_repo = FED_REPO_TOTAL  # $51.25B

    # Calculate what's needed - now including CITI SHORT
    ms_loss = MS_SHORT_POSITION_OZ * (silver_price - 30)
    citi_short_loss = CITI_SHORT_POSITION_OZ * (silver_price - 30)  # Citi's 6.34B oz short
    jpm_gain = JPM_LONG_POSITION_OZ * (silver_price - 30)  # JPM is LONG now - they PROFIT

    # Total short losses (MS + Citi shorts)
    total_short_loss = ms_loss + citi_short_loss
    total_potential_loss_b = total_short_loss / 1e9

    coverage_pct = (current_repo / total_potential_loss_b) * 100 if total_potential_loss_b > 0 else 0

    return {
        'current_repo': current_repo,
        'ms_need': ms_loss / 1e9,
        'citi_need': citi_short_loss / 1e9,  # Citi's short position loss
        'jpm_gain': jpm_gain / 1e9,  # JPM profits (they're long now)
        'total_need': total_potential_loss_b,
        'coverage_pct': coverage_pct,
        'gap': total_potential_loss_b - current_repo,
        'adequate': coverage_pct >= 100,
    }

def calculate_domino_status(prices):
    """Calculate status of each domino"""
    dominoes = {}
    
    # Domino 1: MS Stock
    ms = prices.get('morgan_stanley', {})
    ms_price = ms.get('price', 135)
    ms_daily = ms.get('change_pct', 0)
    if ms_price < 80: dominoes['ms_stock'] = {'status': 'CRITICAL', 'color': '#ff3b5c', 'detail': f'${ms_price:.0f}'}
    elif ms_price < 100 or ms_daily < -5: dominoes['ms_stock'] = {'status': 'WARNING', 'color': '#ff8c42', 'detail': f'${ms_price:.0f}'}
    elif ms_daily < -2: dominoes['ms_stock'] = {'status': 'ELEVATED', 'color': '#fbbf24', 'detail': f'${ms_price:.0f}'}
    else: dominoes['ms_stock'] = {'status': 'STABLE', 'color': '#4ade80', 'detail': f'${ms_price:.0f}'}
    
    # Domino 2: Silver
    silver = prices.get('silver', {}).get('price', 80)
    if silver > 150: dominoes['silver'] = {'status': 'EXPLODING', 'color': '#ff3b5c', 'detail': f'${silver:.0f}'}
    elif silver > 100: dominoes['silver'] = {'status': 'SQUEEZING', 'color': '#ff8c42', 'detail': f'${silver:.0f}'}
    elif silver > 90: dominoes['silver'] = {'status': 'RISING', 'color': '#fbbf24', 'detail': f'${silver:.0f}'}
    else: dominoes['silver'] = {'status': 'STABLE', 'color': '#4ade80', 'detail': f'${silver:.0f}'}
    
    # Domino 3: Other Banks
    jpm = prices.get('jpmorgan', {}).get('change_pct', 0)
    c = prices.get('citibank', {}).get('change_pct', 0)
    bac = prices.get('bank_of_america', {}).get('change_pct', 0)
    bank_avg = (jpm + c + bac) / 3
    if bank_avg < -8: dominoes['other_banks'] = {'status': 'CRITICAL', 'color': '#ff3b5c', 'detail': f'{bank_avg:.1f}%'}
    elif bank_avg < -5: dominoes['other_banks'] = {'status': 'WARNING', 'color': '#ff8c42', 'detail': f'{bank_avg:.1f}%'}
    elif bank_avg < -2: dominoes['other_banks'] = {'status': 'ELEVATED', 'color': '#fbbf24', 'detail': f'{bank_avg:.1f}%'}
    else: dominoes['other_banks'] = {'status': 'STABLE', 'color': '#4ade80', 'detail': f'{bank_avg:.1f}%'}
    
    # Domino 4: Credit
    hyg = prices.get('high_yield', {}).get('week_change', 0)
    if hyg < -5: dominoes['credit'] = {'status': 'FREEZING', 'color': '#ff3b5c', 'detail': f'{hyg:.1f}%wk'}
    elif hyg < -3: dominoes['credit'] = {'status': 'STRESSED', 'color': '#ff8c42', 'detail': f'{hyg:.1f}%wk'}
    elif hyg < -1: dominoes['credit'] = {'status': 'ELEVATED', 'color': '#fbbf24', 'detail': f'{hyg:.1f}%wk'}
    else: dominoes['credit'] = {'status': 'STABLE', 'color': '#4ade80', 'detail': f'{hyg:.1f}%wk'}
    
    # Domino 5: VIX/Fear
    vix = prices.get('vix', {}).get('price', 15)
    if vix > 40: dominoes['fear'] = {'status': 'EXTREME', 'color': '#ff3b5c', 'detail': f'{vix:.0f}'}
    elif vix > 30: dominoes['fear'] = {'status': 'HIGH', 'color': '#ff8c42', 'detail': f'{vix:.0f}'}
    elif vix > 25: dominoes['fear'] = {'status': 'ELEVATED', 'color': '#fbbf24', 'detail': f'{vix:.0f}'}
    else: dominoes['fear'] = {'status': 'NORMAL', 'color': '#4ade80', 'detail': f'{vix:.0f}'}
    
    # Domino 6: Dollar
    dxy = prices.get('dollar_index', {}).get('price', 102)
    if dxy < 95: dominoes['dollar'] = {'status': 'CRISIS', 'color': '#ff3b5c', 'detail': f'{dxy:.1f}'}
    elif dxy < 98: dominoes['dollar'] = {'status': 'WEAK', 'color': '#ff8c42', 'detail': f'{dxy:.1f}'}
    elif dxy < 100: dominoes['dollar'] = {'status': 'DECLINING', 'color': '#fbbf24', 'detail': f'{dxy:.1f}'}
    else: dominoes['dollar'] = {'status': 'STABLE', 'color': '#4ade80', 'detail': f'{dxy:.1f}'}
    
    # Domino 7: Fed Response
    fed = calculate_fed_response_adequacy(silver)
    if fed['coverage_pct'] < 5: dominoes['fed'] = {'status': 'INADEQUATE', 'color': '#ff3b5c', 'detail': f"{fed['coverage_pct']:.1f}%"}
    elif fed['coverage_pct'] < 20: dominoes['fed'] = {'status': 'INSUFFICIENT', 'color': '#ff8c42', 'detail': f"{fed['coverage_pct']:.1f}%"}
    elif fed['coverage_pct'] < 50: dominoes['fed'] = {'status': 'PARTIAL', 'color': '#fbbf24', 'detail': f"{fed['coverage_pct']:.1f}%"}
    else: dominoes['fed'] = {'status': 'ADEQUATE', 'color': '#4ade80', 'detail': f"{fed['coverage_pct']:.1f}%"}
    
    # Domino 8: COMEX
    if silver > 120: dominoes['comex'] = {'status': 'FAILING', 'color': '#ff3b5c', 'detail': 'Delivery stress'}
    elif silver > 100: dominoes['comex'] = {'status': 'STRESSED', 'color': '#ff8c42', 'detail': 'High demand'}
    else: dominoes['comex'] = {'status': 'NORMAL', 'color': '#4ade80', 'detail': 'Functioning'}
    
    return dominoes

def calculate_scenarios(indicators):
    """Calculate scenario probabilities based on current indicators"""
    probs = {
        'slow_burn': 0.35,
        'credit_crunch': 0.25,
        'inflation_spike': 0.15,
        'deflation_bust': 0.15,
        'monetary_reset': 0.10
    }
    
    vix = indicators.get('vix', 15)
    silver = indicators.get('silver', 80)
    gold = indicators.get('gold', 4500)
    kre = indicators.get('kre_weekly', 0)
    hyg = indicators.get('hyg_weekly', 0)
    dxy = indicators.get('dollar_index', 102)
    gs_ratio = indicators.get('gold_silver_ratio', 56)
    ms_daily = indicators.get('ms_daily', 0)
    
    # MS-specific adjustments
    if ms_daily < -10:
        probs['credit_crunch'] += 0.25
        probs['slow_burn'] -= 0.20
    elif ms_daily < -5:
        probs['credit_crunch'] += 0.15
        probs['slow_burn'] -= 0.10
    
    # VIX adjustments
    if vix > 35:
        probs['credit_crunch'] += 0.15
        probs['deflation_bust'] += 0.10
        probs['slow_burn'] -= 0.20
    elif vix > 25:
        probs['credit_crunch'] += 0.08
        probs['slow_burn'] -= 0.08
    
    # Silver adjustments
    if silver > 150:
        probs['monetary_reset'] += 0.30
        probs['slow_burn'] -= 0.25
    elif silver > 100:
        probs['monetary_reset'] += 0.15
        probs['inflation_spike'] += 0.05
        probs['slow_burn'] -= 0.15
    elif silver > 90:
        probs['monetary_reset'] += 0.05
        probs['inflation_spike'] += 0.03
    
    # Bank stress
    if kre < -10:
        probs['credit_crunch'] += 0.20
        probs['deflation_bust'] += 0.10
        probs['slow_burn'] -= 0.25
    elif kre < -5:
        probs['credit_crunch'] += 0.10
        probs['slow_burn'] -= 0.10
    
    # Dollar weakness
    if dxy < 95:
        probs['monetary_reset'] += 0.15
        probs['inflation_spike'] += 0.05
        probs['slow_burn'] -= 0.15
    elif dxy < 100:
        probs['monetary_reset'] += 0.05
    
    # Normalize
    probs = {k: max(0, v) for k, v in probs.items()}
    total = sum(probs.values())
    return {k: v/total for k, v in probs.items()} if total > 0 else probs

def calculate_allocation(probs):
    """Calculate target allocation based on scenario probabilities"""
    allocs = {
        'slow_burn': {
            'Physical Gold': 0.15, 'Physical Silver': 0.10, 'Gold Miners (GDX)': 0.10,
            'Silver Miners (SILJ)': 0.10, 'Long Treasuries (TLT)': 0.15, 'Energy (XLE)': 0.10,
            'Quality Stocks': 0.10, 'Cash': 0.15, 'Bitcoin': 0.05
        },
        'credit_crunch': {
            'Physical Gold': 0.15, 'Physical Silver': 0.10, 'Gold Miners (GDX)': 0.15,
            'Silver Miners (SILJ)': 0.15, 'Long Treasuries (TLT)': 0.15, 'Energy (XLE)': 0.05,
            'Quality Stocks': 0.00, 'Cash': 0.10, 'Bitcoin': 0.05, 'Bank Shorts': 0.10
        },
        'inflation_spike': {
            'Physical Gold': 0.10, 'Physical Silver': 0.15, 'Gold Miners (GDX)': 0.10,
            'Silver Miners (SILJ)': 0.10, 'Long Treasuries (TLT)': 0.00, 'Energy (XLE)': 0.20,
            'Quality Stocks': 0.05, 'Cash': 0.05, 'Bitcoin': 0.10, 'TIPS': 0.15
        },
        'deflation_bust': {
            'Physical Gold': 0.20, 'Physical Silver': 0.05, 'Gold Miners (GDX)': 0.05,
            'Silver Miners (SILJ)': 0.00, 'Long Treasuries (TLT)': 0.30, 'Energy (XLE)': 0.00,
            'Quality Stocks': 0.00, 'Cash': 0.35, 'Bitcoin': 0.00, 'Bank Shorts': 0.05
        },
        'monetary_reset': {
            'Physical Gold': 0.25, 'Physical Silver': 0.20, 'Gold Miners (GDX)': 0.15,
            'Silver Miners (SILJ)': 0.20, 'Long Treasuries (TLT)': 0.00, 'Energy (XLE)': 0.05,
            'Quality Stocks': 0.00, 'Cash': 0.00, 'Bitcoin': 0.15
        },
    }
    
    all_assets = set()
    for a in allocs.values():
        all_assets.update(a.keys())
    
    target = {}
    for asset in all_assets:
        target[asset] = sum(probs.get(s, 0) * allocs.get(s, {}).get(asset, 0) for s in probs)
    
    return {k: v for k, v in sorted(target.items(), key=lambda x: -x[1]) if v > 0.02}

def generate_all_alerts(indicators, prices, countdown, stress_level):
    """Generate all alerts"""
    alerts = []
    lloyds_countdown = calculate_lloyds_countdown()

    # CITIGROUP alerts (LARGEST SHORT)
    citi = prices.get('citibank', {})
    citi_daily = citi.get('change_pct', 0)
    citi_price = citi.get('price', 75)

    if citi_daily < -10:
        alerts.append({'level': 'critical', 'title': '🚨 CITI STOCK CRASHING',
            'msg': f'Citigroup down {citi_daily:.1f}% today. 6.34B oz short position at risk.',
            'action': 'Monitor for trading halt. Citi puts may explode.'})
    elif citi_daily < -5:
        alerts.append({'level': 'warning', 'title': '⚠️ CITI UNDER PRESSURE',
            'msg': f'Citigroup down {citi_daily:.1f}% today. LARGEST silver short.',
            'action': 'Watch for Lloyd\'s insurance deadline impact.'})

    # Lloyd's Insurance Deadline (BEFORE SEC deadline!)
    if lloyds_countdown['days'] < 7 and not lloyds_countdown['expired']:
        alerts.append({'level': 'critical', 'title': '⏰ LLOYD\'S DEADLINE IMMINENT',
            'msg': f"Only {lloyds_countdown['days']} days until Lloyd's stops insuring Citi (Jan 31).",
            'action': 'Citi must close 6.34B oz short or lose insurance.'})
    elif lloyds_countdown['days'] < 14 and not lloyds_countdown['expired']:
        alerts.append({'level': 'warning', 'title': '⏰ LLOYD\'S DEADLINE APPROACHING',
            'msg': f"{lloyds_countdown['days']} days until Lloyd's insurance deadline.",
            'action': 'Watch for Citi covering activity before Jan 31.'})

    # MS-specific alerts
    ms = prices.get('morgan_stanley', {})
    ms_daily = ms.get('change_pct', 0)
    ms_price = ms.get('price', 135)

    if ms_daily < -10:
        alerts.append({'level': 'critical', 'title': '🚨 MS STOCK CRASHING',
            'msg': f'Morgan Stanley down {ms_daily:.1f}% today. Collapse may be imminent.',
            'action': 'Monitor for trading halt. Check MS puts value.'})
    elif ms_daily < -5:
        alerts.append({'level': 'warning', 'title': '⚠️ MS UNDER PRESSURE',
            'msg': f'Morgan Stanley down {ms_daily:.1f}% today.',
            'action': 'Watch for acceleration. Set tight alerts.'})

    if ms_price < 100:
        alerts.append({'level': 'critical', 'title': '🚨 MS BELOW $100',
            'msg': f'Morgan Stanley at ${ms_price:.2f}. Critical support broken.',
            'action': 'MS puts deep ITM. Consider taking profits.'})

    # SEC Countdown alerts
    if countdown['days'] < 7 and not countdown['expired']:
        alerts.append({'level': 'critical', 'title': '⏰ SEC DEADLINE IMMINENT',
            'msg': f"Only {countdown['days']} days until SEC Feb 15 deadline.",
            'action': 'Maximum alert. MS must act soon.'})
    elif countdown['days'] < 14 and not countdown['expired']:
        alerts.append({'level': 'warning', 'title': '⏰ SEC DEADLINE APPROACHING',
            'msg': f"{countdown['days']} days until SEC Feb 15 deadline.",
            'action': 'Watch for MS covering activity.'})
    
    # Silver alerts
    silver = indicators.get('silver', 80)
    if silver > THRESHOLDS['silver']['critical']:
        alerts.append({'level': 'critical', 'title': '🔴 SILVER BREAKOUT - $100+',
            'msg': f'Silver at ${silver:.2f} - Squeeze accelerating!',
            'action': 'HOLD physical, trail stops on paper'})
    elif silver > THRESHOLDS['silver']['warning']:
        alerts.append({'level': 'warning', 'title': '🟠 Silver Approaching Critical',
            'msg': f'Silver at ${silver:.2f} - Nearing breakout zone.',
            'action': 'Review miner positions'})
    
    # Fed response alert
    fed = calculate_fed_response_adequacy(silver)
    if fed['coverage_pct'] < 10:
        alerts.append({'level': 'critical', 'title': '🏛️ FED RESPONSE INADEQUATE',
            'msg': f"Fed repo ${fed['current_repo']:.1f}B covers only {fed['coverage_pct']:.1f}% of potential losses.",
            'action': f"Gap of ${fed['gap']:.0f}B needed. Watch for emergency measures."})
    
    # VIX alerts
    vix = indicators.get('vix', 15)
    if vix > THRESHOLDS['vix']['critical']:
        alerts.append({'level': 'critical', 'title': '🔴 EXTREME VOLATILITY',
            'msg': f'VIX at {vix:.1f} - Risk-off event in progress.',
            'action': 'Activate hedges'})
    
    return alerts

# =============================================================================
# TAB RENDER FUNCTIONS
# =============================================================================

def render_dashboard_tab(prices, indicators, scenarios, allocation, alerts, risk_index):
    """Render main dashboard tab with 4-level visual hierarchy"""

    risk_color = '#ff3b5c' if risk_index >= 7 else '#ff8c42' if risk_index >= 5 else '#4ade80'
    risk_label = 'CRITICAL' if risk_index >= 7 else 'ELEVATED' if risk_index >= 5 else 'STABLE'
    n_crit = len([a for a in alerts if a['level'] == 'critical'])

    # =========================================================================
    # LEVEL 1: HERO SECTION - Risk Index as centerpiece
    # =========================================================================
    st.markdown(f'''
    <div style="text-align:center;padding:30px 0 20px 0;">
        <div class="text-label" style="margin-bottom:10px;">SYSTEMIC RISK INDEX</div>
        <div class="text-hero" style="color:{risk_color};line-height:1;">{risk_index:.1f}</div>
        <div class="text-subhead" style="color:{risk_color};margin-top:5px;">{risk_label}</div>
        <div class="text-caption" style="margin-top:15px;">
            {f'⚠️ {n_crit} CRITICAL ALERT{"S" if n_crit != 1 else ""} ACTIVE' if n_crit > 0 else '✓ No critical alerts'}
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # =========================================================================
    # LEVEL 2: KEY METRICS - Only 4 most critical
    # =========================================================================
    st.markdown('<div class="text-label" style="text-align:center;margin:20px 0 15px 0;">KEY INDICATORS</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        s = prices.get('silver', {})
        silver_price = s.get('price', 0)
        silver_color = '#ff3b5c' if silver_price > 100 else '#ff8c42' if silver_price > 90 else '#ffffff'
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">SILVER</div>
            <div class="text-headline" style="color:{silver_color};">${silver_price:.2f}</div>
            <div class="text-caption">{s.get('change_pct', 0):+.2f}% today</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        ms = prices.get('morgan_stanley', {})
        ms_price = ms.get('price', 0)
        ms_change = ms.get('change_pct', 0)
        ms_color = '#ff3b5c' if ms_change < -5 or ms_price < 100 else '#ff8c42' if ms_change < -2 else '#ffffff'
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">MS STOCK</div>
            <div class="text-headline" style="color:{ms_color};">${ms_price:.2f}</div>
            <div class="text-caption">{ms_change:+.2f}% today</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        v = prices.get('vix', {})
        vix_val = v.get('price', 0)
        vix_color = '#ff3b5c' if vix_val > 35 else '#ff8c42' if vix_val > 25 else '#ffffff'
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">VIX FEAR</div>
            <div class="text-headline" style="color:{vix_color};">{vix_val:.1f}</div>
            <div class="text-caption">{v.get('change_pct', 0):+.1f}% today</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        kre = prices.get('regional_banks', {})
        kre_week = kre.get('week_change', 0)
        kre_color = '#ff3b5c' if kre_week < -10 else '#ff8c42' if kre_week < -5 else '#ffffff'
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">BANKS (KRE)</div>
            <div class="text-headline" style="color:{kre_color};">{kre_week:+.1f}%</div>
            <div class="text-caption">weekly change</div>
        </div>''', unsafe_allow_html=True)

    # =========================================================================
    # LEVEL 3: SCENARIO BAR - Compact horizontal display
    # =========================================================================
    st.markdown('<div class="text-label" style="text-align:center;margin:30px 0 15px 0;">SCENARIO OUTLOOK</div>', unsafe_allow_html=True)

    scenario_config = {
        'slow_burn': {'name': 'Slow Burn', 'color': '#4ade80'},
        'credit_crunch': {'name': 'Credit Crunch', 'color': '#ff3b5c'},
        'inflation_spike': {'name': 'Inflation', 'color': '#ff8c42'},
        'deflation_bust': {'name': 'Deflation', 'color': '#3b82f6'},
        'monetary_reset': {'name': 'Reset', 'color': '#a855f7'},
    }

    # Build horizontal scenario bar
    bar_html = '<div style="display:flex;height:40px;border:1px solid #2a2a2a;overflow:hidden;">'
    for key, prob in scenarios.items():
        cfg = scenario_config.get(key, {'name': key, 'color': '#888'})
        width_pct = prob * 100
        if width_pct > 5:  # Only show label if wide enough
            bar_html += f'<div style="width:{width_pct}%;background:{cfg["color"]};display:flex;align-items:center;justify-content:center;"><span style="font-size:11px;font-weight:700;color:#000;">{cfg["name"]} {prob*100:.0f}%</span></div>'
        else:
            bar_html += f'<div style="width:{width_pct}%;background:{cfg["color"]};"></div>'
    bar_html += '</div>'
    st.markdown(bar_html, unsafe_allow_html=True)

    # =========================================================================
    # LEVEL 4: EXPANDABLE DETAILS
    # =========================================================================
    st.markdown("---")

    # Alerts expander
    if alerts:
        with st.expander(f"🚨 Active Alerts ({len(alerts)})", expanded=n_crit > 0):
            for a in alerts[:5]:
                css_class = f"alert-{a['level']}" if a['level'] != 'info' else 'alert-info'
                st.markdown(f'<div class="{css_class}"><strong>{a["title"]}</strong><br>{a["msg"]}<br><em style="color:#aaa;">→ {a["action"]}</em></div>', unsafe_allow_html=True)

    # All prices expander
    with st.expander("📈 All Market Prices", expanded=False):
        st.markdown("##### Precious Metals")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            g = prices.get('gold', {})
            st.metric("Gold", f"${g.get('price', 0):,.0f}", f"{g.get('change_pct', 0):+.2f}%")
        with c2:
            s = prices.get('silver', {})
            st.metric("Silver", f"${s.get('price', 0):.2f}", f"{s.get('change_pct', 0):+.2f}%")
        with c3:
            x = prices.get('gold_miners', {})
            st.metric("GDX", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")
        with c4:
            x = prices.get('silver_miners', {})
            st.metric("SILJ", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")

        st.markdown("##### Market Indicators")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            x = prices.get('sp500', {})
            st.metric("SPY", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")
        with c2:
            x = prices.get('long_treasury', {})
            st.metric("TLT", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")
        with c3:
            d = prices.get('dollar_index', {})
            st.metric("DXY", f"{d.get('price', 0):.1f}", f"{d.get('change_pct', 0):+.1f}%")
        with c4:
            b = prices.get('bitcoin', {})
            st.metric("Bitcoin", f"${b.get('price', 0):,.0f}", f"{b.get('change_pct', 0):+.1f}%")

        st.markdown("##### Stress Indicators")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            x = prices.get('regional_banks', {})
            st.metric("KRE", f"${x.get('price', 0):.2f}", f"{x.get('week_change', 0):+.1f}%wk")
        with c2:
            x = prices.get('high_yield', {})
            st.metric("HYG", f"${x.get('price', 0):.2f}", f"{x.get('week_change', 0):+.1f}%wk")
        with c3:
            r = prices.get('gold_silver_ratio', {})
            st.metric("G/S Ratio", f"{r.get('price', 0):.1f}", "")
        with c4:
            v = prices.get('vix', {})
            st.metric("VIX", f"{v.get('price', 0):.1f}", f"{v.get('change_pct', 0):+.1f}%")

def render_ms_collapse_tab(prices, countdown, stress_level, ms_exposure):
    """Render Silver Shorts Crisis tab with dual countdowns and bank positions"""

    # Calculate Lloyd's countdown
    lloyds_countdown = calculate_lloyds_countdown()
    silver_price = prices.get('silver', {}).get('price', 80)
    citi_exposure = calculate_citi_exposure(silver_price)

    # =========================================================================
    # HERO: DUAL COUNTDOWN TIMERS
    # =========================================================================
    st.markdown('<div class="text-label" style="text-align:center;margin-bottom:15px;">⚠️ TWO CRITICAL DEADLINES</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Lloyd's Deadline (FIRST - Jan 31)
    with col1:
        lloyds_urgent = lloyds_countdown['days'] < 7 and not lloyds_countdown['expired']
        lloyds_critical = lloyds_countdown['days'] < 3 and not lloyds_countdown['expired']

        if lloyds_countdown['expired']:
            lloyds_msg = "INSURANCE CANCELLED"
        elif lloyds_critical:
            lloyds_msg = "CITI UNINSURED IN DAYS"
        elif lloyds_urgent:
            lloyds_msg = "LLOYD'S DEADLINE IMMINENT"
        else:
            lloyds_msg = "CITI MUST CLOSE SHORTS"

        st.markdown(f"""
        <div class="countdown-box" style="border-color:#ff8c42;{'animation: alert-pulse 1s ease-in-out infinite;' if lloyds_urgent else ''}">
            <div style="position:absolute;top:-14px;left:50%;transform:translateX(-50%);background:#ff8c42;color:#000;padding:5px 15px;font-weight:900;font-size:11px;letter-spacing:2px;">LLOYD'S</div>
            <div class="countdown-number" style="font-size:56px;text-shadow:0 0 30px rgba(255,140,66,0.8);">{lloyds_countdown['days']}</div>
            <div class="countdown-label">DAYS</div>
            <div style="font-size:20px;color:#ffffff;font-weight:700;margin:10px 0;">
                {lloyds_countdown['hours']:02d}:{lloyds_countdown['minutes']:02d}:00
            </div>
            <div style="color:#ff8c42;font-size:12px;text-transform:uppercase;letter-spacing:1px;">
                January 31, 2026
            </div>
            <div class="countdown-urgent" style="color:#ff8c42;">{lloyds_msg}</div>
            <div style="color:#888;font-size:11px;margin-top:8px;">
                Lloyd's stops insuring Citigroup
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SEC Deadline (Feb 15)
    with col2:
        sec_urgent = countdown['days'] < 7 and not countdown['expired']
        sec_critical = countdown['days'] < 3 and not countdown['expired']

        if countdown['expired']:
            sec_msg = "DEADLINE PASSED"
        elif sec_critical:
            sec_msg = "FORCED COVERING IMMINENT"
        elif sec_urgent:
            sec_msg = "SEC DEADLINE IMMINENT"
        else:
            sec_msg = "MS MUST CLOSE SHORTS"

        st.markdown(f"""
        <div class="countdown-box" {'style="animation: alert-pulse 1s ease-in-out infinite;"' if sec_urgent else ''}>
            <div class="countdown-number" style="font-size:56px;">{countdown['days']}</div>
            <div class="countdown-label">DAYS</div>
            <div style="font-size:20px;color:#ffffff;font-weight:700;margin:10px 0;">
                {countdown['hours']:02d}:{countdown['minutes']:02d}:00
            </div>
            <div style="color:#e31837;font-size:12px;text-transform:uppercase;letter-spacing:1px;">
                February 15, 2026
            </div>
            <div class="countdown-urgent">{sec_msg}</div>
            <div style="color:#888;font-size:11px;margin-top:8px;">
                SEC disclosure deadline for MS
            </div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # BANK SHORT POSITIONS TABLE
    # =========================================================================
    st.markdown("---")
    st.markdown('<div class="text-label" style="text-align:center;margin:20px 0 15px 0;">BANK SILVER POSITIONS</div>', unsafe_allow_html=True)

    # Table header
    st.markdown("""
    <div style="display:grid;grid-template-columns:2fr 1fr 1.5fr 1.5fr 1fr;gap:10px;padding:12px;background:#1a1a1a;border:1px solid #2a2a2a;font-weight:700;">
        <div class="text-label">BANK</div>
        <div class="text-label" style="text-align:center;">POSITION</div>
        <div class="text-label" style="text-align:right;">OUNCES</div>
        <div class="text-label" style="text-align:right;">EXPOSURE @ $80</div>
        <div class="text-label" style="text-align:center;">STATUS</div>
    </div>
    """, unsafe_allow_html=True)

    # Citigroup Row (LARGEST)
    citi_loss_80 = CITI_SHORT_POSITION_OZ * (80 - 30) / 1e9
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:2fr 1fr 1.5fr 1.5fr 1fr;gap:10px;padding:15px 12px;background:#141414;border:1px solid #2a2a2a;border-left:4px solid #ff3b5c;">
        <div style="color:#ffffff;font-weight:600;">🏦 Citigroup</div>
        <div style="text-align:center;"><span style="background:#ff3b5c;color:#fff;padding:2px 8px;font-size:11px;font-weight:700;">SHORT</span></div>
        <div style="text-align:right;color:#ff3b5c;font-weight:700;">6.34B oz</div>
        <div style="text-align:right;color:#ff3b5c;font-weight:700;">${citi_loss_80:.0f}B loss</div>
        <div style="text-align:center;color:#ff3b5c;font-weight:700;">1.8x INSOLVENT</div>
    </div>
    """, unsafe_allow_html=True)

    # Morgan Stanley Row
    ms_loss_80 = MS_SHORT_POSITION_OZ * (80 - 30) / 1e9
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:2fr 1fr 1.5fr 1.5fr 1fr;gap:10px;padding:15px 12px;background:#141414;border:1px solid #2a2a2a;border-left:4px solid #ff3b5c;">
        <div style="color:#ffffff;font-weight:600;">🎯 Morgan Stanley</div>
        <div style="text-align:center;"><span style="background:#ff3b5c;color:#fff;padding:2px 8px;font-size:11px;font-weight:700;">SHORT</span></div>
        <div style="text-align:right;color:#ff3b5c;font-weight:700;">5.9B oz</div>
        <div style="text-align:right;color:#ff3b5c;font-weight:700;">${ms_loss_80:.0f}B loss</div>
        <div style="text-align:center;color:#ff3b5c;font-weight:700;">2.9x INSOLVENT</div>
    </div>
    """, unsafe_allow_html=True)

    # JPMorgan Row (LONG - PROFITS)
    jpm_gain_80 = JPM_LONG_POSITION_OZ * (80 - 30) / 1e9
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:2fr 1fr 1.5fr 1.5fr 1fr;gap:10px;padding:15px 12px;background:#141414;border:1px solid #2a2a2a;border-left:4px solid #4ade80;">
        <div style="color:#ffffff;font-weight:600;">🏛️ JPMorgan</div>
        <div style="text-align:center;"><span style="background:#4ade80;color:#000;padding:2px 8px;font-size:11px;font-weight:700;">LONG</span></div>
        <div style="text-align:right;color:#4ade80;font-weight:700;">750M oz</div>
        <div style="text-align:right;color:#4ade80;font-weight:700;">+${jpm_gain_80:.0f}B gain</div>
        <div style="text-align:center;color:#4ade80;font-weight:700;">PROFITS ✓</div>
    </div>
    """, unsafe_allow_html=True)

    # JPM flip note
    st.markdown("""
    <div class="alert-info" style="margin-top:15px;">
        <strong>🔄 JPM FLIPPED POSITION</strong><br>
        JPMorgan went from 200M oz SHORT to 750M oz LONG between June-October 2025.<br>
        <em style="color:#aaa;">First time in history JPM is long both physical AND paper silver. They will PROFIT from the squeeze.</em>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # STRESS METER (simplified, full width)
    # =========================================================================
    stress_color = '#4ade80' if stress_level < 30 else '#fbbf24' if stress_level < 50 else '#ff8c42' if stress_level < 70 else '#ff3b5c'
    stress_label = 'LOW' if stress_level < 30 else 'MODERATE' if stress_level < 50 else 'HIGH' if stress_level < 70 else 'CRITICAL'

    st.markdown(f'''
    <div class="stress-meter" style="margin-top:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <span class="text-label">BANK STRESS LEVEL</span>
            <span style="color:{stress_color};font-size:28px;font-weight:900;">{stress_level}<span style="font-size:14px;color:#888;">/100</span></span>
        </div>
        <div style="background:#1a1a1a;height:12px;overflow:hidden;border:1px solid #2a2a2a;">
            <div style="background:linear-gradient(90deg, {stress_color}, {stress_color});width:{stress_level}%;height:100%;"></div>
        </div>
        <div class="text-caption" style="text-align:right;margin-top:5px;">{stress_label}</div>
    </div>
    ''', unsafe_allow_html=True)

    # =========================================================================
    # KEY METRICS: Stock Prices (compact row)
    # =========================================================================
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        citi = prices.get('citibank', {})
        citi_change = citi.get('change_pct', 0)
        citi_color = '#ff3b5c' if citi_change < -5 else '#ff8c42' if citi_change < -2 else '#4ade80' if citi_change > 0 else '#ffffff'
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">CITI STOCK</div>
            <div class="text-headline" style="color:{citi_color};">${citi.get('price', 0):.2f}</div>
            <div class="text-caption">{citi_change:+.2f}%</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        ms = prices.get('morgan_stanley', {})
        ms_change = ms.get('change_pct', 0)
        ms_color = '#ff3b5c' if ms_change < -5 else '#ff8c42' if ms_change < -2 else '#4ade80' if ms_change > 0 else '#ffffff'
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">MS STOCK</div>
            <div class="text-headline" style="color:{ms_color};">${ms.get('price', 0):.2f}</div>
            <div class="text-caption">{ms_change:+.2f}%</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        jpm = prices.get('jpmorgan', {})
        jpm_change = jpm.get('change_pct', 0)
        jpm_color = '#4ade80' if jpm_change > 0 else '#ff8c42' if jpm_change > -2 else '#ff3b5c'
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">JPM STOCK</div>
            <div class="text-headline" style="color:{jpm_color};">${jpm.get('price', 0):.2f}</div>
            <div class="text-caption">{jpm_change:+.2f}%</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        silver = prices.get('silver', {})
        st.markdown(f'''
        <div class="metric-card" style="text-align:center;">
            <div class="text-label">SILVER</div>
            <div class="text-headline">${silver.get('price', 0):.2f}</div>
            <div class="text-caption">{silver.get('change_pct', 0):+.2f}%</div>
        </div>''', unsafe_allow_html=True)

    # =========================================================================
    # EXPANDABLE: Detailed Calculations
    # =========================================================================
    with st.expander("📊 Detailed Exposure Calculations", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Citigroup Short Position:**
            - Position Size: {citi_exposure['position_oz']/1e9:.2f} billion oz
            - Current Value: ${citi_exposure['current_value']/1e12:.2f}T
            - Paper Loss: ${citi_exposure['paper_loss']/1e9:.0f}B
            - Citi Equity: $175B
            - Loss/Equity: {citi_exposure['loss_vs_equity']:.2f}x
            - Status: {'🔴 INSOLVENT' if citi_exposure['insolvent'] else '🟡 At Risk'}
            """)
        with col2:
            st.markdown(f"""
            **Morgan Stanley Short Position:**
            - Position Size: {ms_exposure['position_oz']/1e9:.1f} billion oz
            - Current Value: ${ms_exposure['current_value']/1e12:.2f}T
            - Paper Loss: ${ms_exposure['paper_loss']/1e9:.0f}B
            - MS Equity: $100B
            - Loss/Equity: {ms_exposure['loss_vs_equity']:.2f}x
            - Status: {'🔴 INSOLVENT' if ms_exposure['insolvent'] else '🟡 At Risk'}
            """)

def render_bank_exposure_tab(prices, bank_risk_scores):
    """Render Bank Exposure tab with visual hierarchy"""

    # =========================================================================
    # HERO: Summary Stats
    # =========================================================================
    total_pm = 437.4 + 204.3 + 47.9 + 0.6

    st.markdown(f'''
    <div style="text-align:center;padding:20px 0;">
        <div class="text-label">TOTAL US BANK PM DERIVATIVES EXPOSURE</div>
        <div class="text-hero" style="color:#ff3b5c;">${total_pm:.0f}B</div>
        <div class="text-caption" style="margin-top:10px;">JPM + Citi control 91.1% • Data: OCC Q3 2025</div>
    </div>
    ''', unsafe_allow_html=True)

    # =========================================================================
    # TIER 1: Extreme Risk (Always visible)
    # =========================================================================
    st.markdown('<div class="text-label" style="margin:20px 0 15px 0;">TIER 1: EXTREME RISK</div>', unsafe_allow_html=True)

    for key in ['JPM', 'C', 'MS']:
        bank = BANK_PM_EXPOSURE[key]
        risk = bank_risk_scores.get(key, {})
        score = risk.get('score', 50)
        score_color = '#ff3b5c' if score >= 70 else '#ff8c42' if score >= 50 else '#4ade80'

        pm_display = f"${bank['pm_derivatives']/1e9:.1f}B" if bank['pm_derivatives'] else "HIDDEN"
        pct_display = f"{bank['pct_total']:.1f}%" if bank['pct_total'] else "N/A"

        st.markdown(f"""
        <div class="bank-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span class="text-subhead" style="color:#ffffff;">{bank['name']}</span>
                    <span class="text-caption" style="margin-left:10px;">({bank['ticker']})</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:{score_color};font-size:24px;font-weight:bold;">{score}</span>
                    <span class="text-caption">/100 RISK</span>
                </div>
            </div>
            <div style="display:flex;gap:30px;margin-top:10px;flex-wrap:wrap;">
                <div><span class="text-caption">PM Derivatives:</span> <span style="color:#ffffff;font-weight:600;">{pm_display}</span></div>
                <div><span class="text-caption">Share:</span> <span style="color:#ffffff;">{pct_display}</span></div>
                <div><span class="text-caption">Equity:</span> <span style="color:#ffffff;">${bank['equity']/1e9:.0f}B</span></div>
                <div><span class="text-caption">Price:</span> <span style="color:#ffffff;">${risk.get('price', 0):.2f}</span> <span style="color:{'#ff3b5c' if risk.get('daily_change', 0) < 0 else '#4ade80'};">{risk.get('daily_change', 0):+.2f}%</span></div>
            </div>
            {f'<div style="color:#ff8c42;font-size:12px;margin-top:8px;">⚠️ {bank.get("note", "")}</div>' if bank.get('note') else ''}
        </div>
        """, unsafe_allow_html=True)

    # =========================================================================
    # TIER 2 & 3: Collapsible
    # =========================================================================
    with st.expander("🟠 Tier 2: High Risk (US Banks)", expanded=False):
        col1, col2 = st.columns(2)
        for i, key in enumerate(['BAC', 'GS']):
            bank = BANK_PM_EXPOSURE[key]
            risk = bank_risk_scores.get(key, {})
            with col1 if i == 0 else col2:
                pm_display = f"${bank['pm_derivatives']/1e9:.1f}B" if bank['pm_derivatives'] else "N/A"
                st.markdown(f"""
                <div class="bank-card" style="border-left-color:#ff8c42;">
                    <div class="text-subhead" style="color:#e8e8f0;">{bank['name']}</div>
                    <div class="text-caption">PM: {pm_display} | Equity: ${bank['equity']/1e9:.0f}B</div>
                    <div class="text-caption">Price: ${risk.get('price', 0):.2f} ({risk.get('daily_change', 0):+.2f}%)</div>
                </div>
                """, unsafe_allow_html=True)

    with st.expander("🟡 Tier 3: European Banks (LBMA)", expanded=False):
        for key in ['HSBC', 'DB', 'UBS', 'BCS', 'BNS']:
            bank = BANK_PM_EXPOSURE[key]
            risk = bank_risk_scores.get(key, {})
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #2a2a2a;">
                <div>
                    <span style="color:#e0e0e0;font-weight:600;">{bank['name']}</span>
                    <span class="text-caption" style="margin-left:8px;">{bank['ticker']}</span>
                </div>
                <div>
                    <span style="color:#ffffff;">${risk.get('price', 0):.2f}</span>
                    <span style="color:{'#ff3b5c' if risk.get('daily_change', 0) < 0 else '#4ade80'};">{risk.get('daily_change', 0):+.2f}%</span>
                </div>
            </div>
            <div class="text-caption" style="color:#ff8c42;padding-bottom:5px;">{bank.get('note', '')}</div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # TRADING IDEAS: Collapsible
    # =========================================================================
    with st.expander("🎯 Trading Ideas (Put Options)", expanded=False):
        st.markdown("*Suggested contagion plays - NOT financial advice*")
        puts_data = [
            {"Bank": "Morgan Stanley", "Ticker": "MS", "Current": "$135", "Strike": "$60", "Exp": "Mar 21", "Premium": "$0.01", "Payout @$0": "$6M"},
            {"Bank": "Citigroup", "Ticker": "C", "Current": "$75", "Strike": "$40", "Exp": "Mar 21", "Premium": "$0.03", "Payout @$20": "$400K"},
            {"Bank": "JPMorgan", "Ticker": "JPM", "Current": "$250", "Strike": "$150", "Exp": "Mar 21", "Premium": "$0.05", "Payout @$100": "$500K"},
            {"Bank": "Deutsche Bank", "Ticker": "DB", "Current": "$18", "Strike": "$10", "Exp": "Apr 17", "Premium": "$0.05", "Payout @$5": "$100K"},
            {"Bank": "Barclays", "Ticker": "BCS", "Current": "$13", "Strike": "$8", "Exp": "Apr 17", "Premium": "$0.03", "Payout @$4": "$80K"},
        ]
        st.table(pd.DataFrame(puts_data))

def render_fed_response_tab(prices, silver_price):
    """Render Fed Response Tracker tab"""

    st.markdown("### 🏛️ Federal Reserve Response Tracker")
    st.markdown("*Monitoring Fed emergency lending and bailout capacity*")

    fed = calculate_fed_response_adequacy(silver_price)

    st.markdown("---")

    # Big numbers - UPDATED
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Known Fed Repo", f"${fed['current_repo']:.1f}B", "Dec 26-28 total")
    with col2:
        coverage_color = "inverse" if fed['coverage_pct'] < 20 else "normal"
        st.metric("Coverage", f"{fed['coverage_pct']:.1f}%", "of short losses", delta_color=coverage_color)
    with col3:
        st.metric("Gap Needed", f"${fed['gap']:.0f}B", "to cover losses")
    with col4:
        st.metric("Adequate?", "NO ❌" if not fed['adequate'] else "YES ✅", "")

    st.markdown("---")

    # Visual comparison - UPDATED FOR CITI + MS SHORTS
    st.markdown("### 📊 Fed Response vs Bank Short Losses")

    st.markdown(f"""
    <div class="fed-card">
        <div style="margin-bottom:15px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:#e8e8f0;">Fed Repo Deployed</span>
                <span style="color:#3b82f6;font-weight:bold;">${fed['current_repo']:.1f}B</span>
            </div>
            <div class="bailout-bar">
                <div style="background:#3b82f6;width:{min(fed['current_repo']/500*100, 100):.1f}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>

        <div style="margin-bottom:15px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:#e8e8f0;">⚠️ Citigroup Short Loss (6.34B oz)</span>
                <span style="color:#ff3b5c;font-weight:bold;">${fed['citi_need']:.0f}B</span>
            </div>
            <div class="bailout-bar">
                <div style="background:#ff3b5c;width:{min(fed['citi_need']/500*100, 100):.1f}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>

        <div style="margin-bottom:15px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:#e8e8f0;">⚠️ Morgan Stanley Short Loss (5.9B oz)</span>
                <span style="color:#ff8c42;font-weight:bold;">${fed['ms_need']:.0f}B</span>
            </div>
            <div class="bailout-bar">
                <div style="background:#ff8c42;width:{min(fed['ms_need']/500*100, 100):.1f}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>

        <div style="margin-bottom:15px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:#e8e8f0;">✅ JPMorgan GAIN (750M oz LONG)</span>
                <span style="color:#4ade80;font-weight:bold;">+${fed['jpm_gain']:.0f}B</span>
            </div>
            <div class="bailout-bar">
                <div style="background:#4ade80;width:{min(fed['jpm_gain']/100*100, 100):.1f}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>

        <div style="border-top:1px solid #444;padding-top:15px;margin-top:15px;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#e8e8f0;font-weight:bold;">TOTAL SHORT LOSSES (CITI + MS)</span>
                <span style="color:#ff3b5c;font-weight:bold;font-size:20px;">${fed['total_need']:.0f}B</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # JPM Profits Note
    st.markdown("""
    <div class="alert-info" style="margin-top:15px;">
        <strong>📈 JPMorgan Profits From Crisis</strong><br>
        JPM flipped from 200M oz SHORT to 750M oz LONG (Jun-Oct 2025). They will PROFIT while Citi and MS face insolvency.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Historical comparison
    st.markdown("### 📜 Historical Bailout Comparison")
    
    st.markdown("*How does current crisis compare to past interventions?*")
    
    for bailout in BAILOUT_HISTORY:
        pct_of_current = (bailout['amount'] / fed['total_need']) * 100 if fed['total_need'] > 0 else 0
        bar_width = min(bailout['amount'] / 5000 * 100, 100)
        
        st.markdown(f"""
        <div style="margin:10px 0;">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                <span style="color:#e8e8f0;font-size:13px;">{bailout['event']}</span>
                <span style="color:#888;font-size:12px;">${bailout['amount']}B ({pct_of_current:.0f}% of current need)</span>
            </div>
            <div class="bailout-bar">
                <div style="background:linear-gradient(90deg, #3b82f6, #8b5cf6);width:{bar_width}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # What Fed can/can't do
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ What the Fed CAN Do")
        st.markdown("""
        - Print unlimited dollars
        - Buy unlimited Treasuries/MBS
        - Provide unlimited repo lending
        - Create emergency lending facilities
        - Backstop failing banks temporarily
        - Lower interest rates to zero
        - Invoke Section 13(3) emergency powers
        """)
    
    with col2:
        st.markdown("### ❌ What the Fed CAN'T Do")
        st.markdown("""
        - **Create physical silver**
        - Force shorts to cover at lower prices
        - Stop a short squeeze
        - Make silver price go down
        - Prevent insolvency if losses are real
        - Inject capital without Congress
        - Make 5.9B oz of silver appear
        """)
    
    st.markdown("---")
    
    # Key insight
    st.markdown("""
    <div class="alert-critical">
        <strong>🔑 KEY INSIGHT</strong><br>
        The Fed can provide LIQUIDITY (cash loans), but it cannot provide SOLVENCY (capital to cover losses).<br><br>
        <strong>COMBINED SHORT EXPOSURE:</strong> Citigroup (6.34B oz) + Morgan Stanley (5.9B oz) = <strong>12.24 BILLION OUNCES</strong><br><br>
        At $300 silver, they owe $3.67 TRILLION combined. The Fed cannot print silver. The Fed cannot make that debt disappear.<br><br>
        <em>Meanwhile, JPMorgan flipped LONG (750M oz) and will PROFIT from the squeeze.</em>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Fed repo data source
    st.markdown("### 📡 Data Sources")
    st.markdown("""
    - [NY Fed Repo Operations](https://www.newyorkfed.org/markets/desk-operations)
    - [Fed H.4.1 Weekly Report](https://www.federalreserve.gov/releases/h41/)
    - [Fed Emergency Lending (Section 13(3))](https://www.federalreserve.gov/monetarypolicy/bst_recenttrends.htm)
    """)

def render_domino_tab(prices, dominoes):
    """Render Domino Effects tab"""
    
    st.markdown("### 🎯 Domino Effect Monitor")
    
    domino_config = [
        ('ms_stock', 'Domino 1: MS Stock', '🏦', 'Morgan Stanley stock collapse'),
        ('silver', 'Domino 2: Silver', '🥈', 'Silver price explosion'),
        ('other_banks', 'Domino 3: Other Banks', '🏛️', 'Contagion to JPM, Citi, BAC'),
        ('credit', 'Domino 4: Credit Markets', '📉', 'High yield spreads explode'),
        ('fear', 'Domino 5: VIX/Fear', '😰', 'Market panic'),
        ('dollar', 'Domino 6: Dollar', '💵', 'Dollar weakness'),
        ('fed', 'Domino 7: Fed Response', '🏛️', 'Emergency measures'),
        ('comex', 'Domino 8: COMEX', '🏪', 'Exchange delivery failures'),
    ]
    
    for key, title, icon, desc in domino_config:
        d = dominoes.get(key, {'status': 'UNKNOWN', 'color': '#666', 'detail': ''})
        st.markdown(f"""
        <div class="domino-box" style="border-left-color:{d['color']};padding:15px;margin:10px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-size:24px;margin-right:10px;">{icon}</span>
                    <span style="color:#e8e8f0;font-size:16px;font-weight:bold;">{title}</span>
                    <span style="color:#666;font-size:12px;margin-left:15px;">{desc}</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:{d['color']};font-size:18px;font-weight:bold;">{d['status']}</span>
                    <span style="color:#888;font-size:12px;margin-left:10px;">{d['detail']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_positions_tab(prices):
    """Render My Positions tab"""
    
    st.markdown("### 💰 Your Position Tracker")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SLV $145 Call (Feb 20, 2026)")
        slv_price = prices.get('slv', {}).get('price', 72)
        st.markdown(f"**Current SLV:** ${slv_price:.2f}")
        st.markdown(f"**Strike:** $145.00 | **Contracts:** 200 | **Cost:** $2,200")
        if slv_price >= 145:
            itm_value = (slv_price - 145) * 200 * 100
            st.success(f"✅ ITM! Value: ${itm_value:,.0f}")
        else:
            st.info(f"⏳ ${145 - slv_price:.2f} to strike")
    
    with col2:
        st.markdown("#### MS $60 Put (Mar 21, 2026)")
        ms_price = prices.get('morgan_stanley', {}).get('price', 135)
        st.markdown(f"**Current MS:** ${ms_price:.2f}")
        st.markdown(f"**Strike:** $60.00 | **Contracts:** 1,000 | **Cost:** $1,000")
        if ms_price <= 60:
            itm_value = (60 - ms_price) * 1000 * 100
            st.success(f"✅ ITM! Value: ${itm_value:,.0f}")
        else:
            st.info(f"⏳ ${ms_price - 60:.2f} above strike")
    
    st.markdown("---")
    
    # P&L Calculator
    st.markdown("### 📊 P&L Calculator")
    col1, col2 = st.columns(2)
    with col1:
        silver_input = st.number_input("Silver Price at Exit", 80, 500, 289)
    with col2:
        ms_input = st.number_input("MS Stock Price at Exit", 0, 150, 0)
    
    slv_at_exit = silver_input * 0.897 * 1.02
    slv_call_value = max(0, (slv_at_exit - 145)) * 200 * 100
    slv_profit = slv_call_value - 2200
    
    ms_put_value = max(0, (60 - ms_input)) * 1000 * 100
    ms_profit = ms_put_value - 1000
    
    total_profit = slv_profit + ms_profit
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("SLV Call P&L", f"${slv_profit:,.0f}")
    with c2:
        st.metric("MS Put P&L", f"${ms_profit:,.0f}")
    with c3:
        st.metric("TOTAL P&L", f"${total_profit:,.0f}")

def render_scenarios_tab(scenarios, allocation):
    """Render Scenarios tab"""
    
    st.markdown("### 📊 Scenario Analysis")
    
    scenario_details = {
        'slow_burn': {'name': 'Slow Burn', 'color': '#4ade80', 'desc': 'Status quo continues'},
        'credit_crunch': {'name': 'Credit Crunch', 'color': '#ff3b5c', 'desc': 'Banking crisis triggered by MS'},
        'inflation_spike': {'name': 'Inflation Spike', 'color': '#ff8c42', 'desc': 'Inflation reaccelerates'},
        'deflation_bust': {'name': 'Deflation Bust', 'color': '#3b82f6', 'desc': 'Credit collapse'},
        'monetary_reset': {'name': 'Monetary Reset', 'color': '#a855f7', 'desc': 'Dollar crisis, gold reprices'},
    }
    
    for key, prob in scenarios.items():
        details = scenario_details.get(key, {})
        with st.expander(f"{details.get('name', key)} - {prob*100:.0f}%", expanded=(prob > 0.20)):
            st.markdown(f"**Probability:** {prob*100:.1f}%")
            st.markdown(f"**Description:** {details.get('desc', '')}")


def render_content_tab(prices, countdown):
    """Render Content Export tab for TikTok content generation"""

    st.markdown("### 📱 Content Export")
    st.markdown("Generate TikTok-ready content from market data")

    # Initialize trigger manager in session state
    if 'trigger_manager' not in st.session_state:
        st.session_state.trigger_manager = TriggerManager()

    trigger_manager = st.session_state.trigger_manager

    # Section 1: Manual Generation
    st.markdown("#### 🎬 Manual Generation")

    col1, col2 = st.columns([3, 1])
    with col2:
        generate_video = st.toggle("Generate Video", value=False, help="Generate video instead of image (slower)")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📈 Price Alert", use_container_width=True):
            silver_price = prices.get('silver', {}).get('price', 0)
            silver_change = prices.get('silver', {}).get('change_pct', 0)
            data = {'asset': 'SILVER', 'price': silver_price, 'change': silver_change}
            path = trigger_manager.manual_generate(TemplateType.PRICE_ALERT, data, generate_video)
            st.success(f"Generated: {path.name}")

    with col2:
        if st.button("⏰ Countdown", use_container_width=True):
            days = countdown.get('comex', {}).get('days', 0)
            data = {
                'days': days,
                'event': 'COMEX Deadline',
                'date': 'March 27, 2026'
            }
            path = trigger_manager.manual_generate(TemplateType.COUNTDOWN, data, generate_video)
            st.success(f"Generated: {path.name}")

    with col3:
        if st.button("🏦 Bank Crisis", use_container_width=True):
            ms_price = prices.get('morgan_stanley', {}).get('price', 0)
            ms_change = prices.get('morgan_stanley', {}).get('change_pct', 0)
            data = {
                'bank': 'Morgan Stanley',
                'price': ms_price,
                'change': ms_change,
                'exposure': '$18.5B',
                'loss': '$12.3B'
            }
            path = trigger_manager.manual_generate(TemplateType.BANK_CRISIS, data, generate_video)
            st.success(f"Generated: {path.name}")

    with col4:
        if st.button("📊 Daily Summary", use_container_width=True):
            data = {
                'silver': prices.get('silver', {}).get('price', 0),
                'gold': prices.get('gold', {}).get('price', 0),
                'ms': prices.get('morgan_stanley', {}).get('price', 0),
                'vix': prices.get('vix', {}).get('price', 0),
                'risk': 7.5,  # TODO: Use actual risk index
            }
            path = trigger_manager.manual_generate(TemplateType.DAILY_SUMMARY, data, generate_video)
            st.success(f"Generated: {path.name}")

    st.markdown("---")

    # Section 2: Trigger Status
    st.markdown("#### ⚡ Auto-Trigger Status")

    status = trigger_manager.get_trigger_status()

    col1, col2 = st.columns([1, 1])

    with col1:
        enabled = st.toggle("Enable Auto-Triggers", value=status['enabled'])
        trigger_manager.set_enabled(enabled)

        st.markdown("**Price Thresholds:**")
        thresholds = status['price_thresholds']
        st.markdown(f"- Silver: {thresholds.get('silver', [])}")
        st.markdown(f"- MS Drop: {thresholds.get('ms_drop', [])}%")
        st.markdown(f"- VIX: {thresholds.get('vix', [])}")

    with col2:
        st.markdown("**Schedule:**")
        st.markdown(f"- Times: {', '.join(status['scheduled_times'])}")
        st.markdown(f"- Next: {status['next_scheduled'] or 'N/A'}")
        st.markdown(f"- Cooldown: {status['cooldown_hours']}h")

        if status['last_triggered']:
            st.markdown("**Last Triggered:**")
            for key, time in list(status['last_triggered'].items())[:3]:
                st.caption(f"- {key}: {time}")

    st.markdown("---")

    # Section 3: Recent Content
    st.markdown("#### 📁 Recent Content")

    recent_files = trigger_manager.get_recent_files(5)

    if recent_files:
        for file_path in recent_files:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(file_path.name)
            with col2:
                file_type = "🎬" if file_path.suffix == '.mp4' else "🖼️"
                st.text(file_type)
            with col3:
                # Read file for download
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            "⬇️",
                            f.read(),
                            file_name=file_path.name,
                            key=f"dl_{file_path.name}"
                        )
    else:
        st.info("No content generated yet. Use the buttons above to create content.")

    # Also check content-output directory for existing files
    output_dir = Path("content-output")
    if output_dir.exists():
        images = list((output_dir / "images").glob("*.png"))[-5:]
        videos = list((output_dir / "videos").glob("*.mp4"))[-5:]

        if images or videos:
            st.markdown("**Files in content-output/:**")
            all_files = sorted(images + videos, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            for file_path in all_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(file_path.name)
                with col2:
                    file_type = "🎬" if file_path.suffix == '.mp4' else "🖼️"
                    st.text(file_type)
                with col3:
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            "⬇️",
                            f.read(),
                            file_name=file_path.name,
                            key=f"dl_existing_{file_path.name}"
                        )


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # Sidebar
    st.sidebar.title("⚠️ fault.watch v4.0")
    st.sidebar.caption("Complete Crisis Monitor")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown(f"**Last Update:**")
    st.sidebar.markdown(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Links")
    st.sidebar.markdown("- [NYSE MS](https://www.nyse.com/quote/XNYS:MS)")
    st.sidebar.markdown("- [Fed Repo](https://www.newyorkfed.org/markets/desk-operations)")
    st.sidebar.markdown("- [COMEX Silver](https://www.cmegroup.com/markets/metals/precious/silver.html)")
    st.sidebar.markdown("- [OCC Derivatives](https://www.occ.gov/publications-and-resources/publications/quarterly-report-on-bank-trading-and-derivatives-activities/index-quarterly-report-on-bank-trading-and-derivatives-activities.html)")

    # Content trigger status indicator
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📱 Content")
    if 'trigger_manager' in st.session_state:
        tm = st.session_state.trigger_manager
        status = tm.get_trigger_status()
        trigger_status = "🟢 Enabled" if status['enabled'] else "🔴 Disabled"
        st.sidebar.markdown(f"Auto-triggers: {trigger_status}")
        st.sidebar.caption(f"Generated: {status['total_generated']} files")
    
    # Fetch data
    with st.spinner("Loading market data..."):
        prices = fetch_all_prices()
    
    # Build indicators
    indicators = {
        'vix': prices.get('vix', {}).get('price', 15),
        'gold': prices.get('gold', {}).get('price', 4520),
        'silver': prices.get('silver', {}).get('price', 80),
        'kre_weekly': prices.get('regional_banks', {}).get('week_change', 0),
        'hyg_weekly': prices.get('high_yield', {}).get('week_change', 0),
        'dollar_index': prices.get('dollar_index', {}).get('price', 102),
        'bitcoin': prices.get('bitcoin', {}).get('price', 91000),
        'gold_silver_ratio': prices.get('gold_silver_ratio', {}).get('price', 56),
        'ms_daily': prices.get('morgan_stanley', {}).get('change_pct', 0),
    }
    
    # Calculate everything
    countdown = calculate_countdown()
    stress_level = calculate_ms_stress_level(prices)
    dominoes = calculate_domino_status(prices)
    scenarios = calculate_scenarios(indicators)
    allocation = calculate_allocation(scenarios)
    silver_price = prices.get('silver', {}).get('price', 80)
    ms_exposure = calculate_ms_exposure(silver_price)
    bank_risk_scores = calculate_bank_risk_scores(prices)
    alerts = generate_all_alerts(indicators, prices, countdown, stress_level)
    
    risk_index = sum(scenarios.get(s, 0) * w for s, w in [
        ('slow_burn', 5), ('credit_crunch', 9), ('inflation_spike', 7),
        ('deflation_bust', 9), ('monetary_reset', 10)
    ])

    # Initialize trigger manager in session state
    if 'trigger_manager' not in st.session_state:
        st.session_state.trigger_manager = TriggerManager()

    # Check auto-triggers after price fetch
    trigger_manager = st.session_state.trigger_manager
    if trigger_manager.config.enabled:
        # Check price triggers
        trigger_prices = {
            'silver': prices.get('silver', {}).get('price', 0),
            'silver_change': prices.get('silver', {}).get('change_pct', 0),
            'ms_change': prices.get('morgan_stanley', {}).get('change_pct', 0),
            'ms_price': prices.get('morgan_stanley', {}).get('price', 0),
            'vix': prices.get('vix', {}).get('price', 0),
            'vix_change': prices.get('vix', {}).get('change_pct', 0),
        }
        generated = trigger_manager.check_price_triggers(trigger_prices)
        if generated:
            st.toast(f"🎬 Auto-generated {len(generated)} content files!")

        # Check scheduled triggers
        scheduled_file = trigger_manager.check_scheduled_triggers()
        if scheduled_file:
            st.toast(f"📊 Generated daily summary: {scheduled_file.name}")

    # Breaking News Banner (shows when risk is elevated)
    render_breaking_header(alerts, risk_index, countdown)

    # Header
    st.markdown("""
    <div style="text-align:center;padding:10px 0;">
        <h1 style="font-size:42px;margin:0;">⚠️ FAULT.WATCH</h1>
        <p style="color:#888;font-size:14px;">Complete Crisis Monitor • Fed Response Tracker • Bank Exposure</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Dashboard",
        "🏦 MS Collapse",
        "💀 Bank Exposure",
        "🏛️ Fed Response",
        "🎯 Dominoes",
        "💰 Positions",
        "📈 Scenarios",
        "📱 Content"
    ])

    with tab1:
        render_dashboard_tab(prices, indicators, scenarios, allocation, alerts, risk_index)

    with tab2:
        render_ms_collapse_tab(prices, countdown, stress_level, ms_exposure)

    with tab3:
        render_bank_exposure_tab(prices, bank_risk_scores)

    with tab4:
        render_fed_response_tab(prices, silver_price)

    with tab5:
        render_domino_tab(prices, dominoes)

    with tab6:
        render_positions_tab(prices)

    with tab7:
        render_scenarios_tab(scenarios, allocation)

    with tab8:
        render_content_tab(prices, countdown)
    
    # Footer
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** Based on UNVERIFIED whistleblower information. NOT financial advice. Risk of total loss.")
    st.caption(f"fault.watch v4.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
