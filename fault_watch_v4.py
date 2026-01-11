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

Run with: streamlit run fault_watch_v4.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import requests
import json
import time

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(page_title="fault.watch", page_icon="⚠️", layout="wide")

# =============================================================================
# CONSTANTS
# =============================================================================
SEC_DEADLINE = datetime(2026, 2, 15, 16, 0, 0)
MS_SHORT_POSITION_OZ = 5_900_000_000

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

# Fed Emergency Lending History
FED_REPO_HISTORY = [
    {'date': '2025-12-27', 'amount': 17.25, 'note': 'Silver spike to $83'},
    {'date': '2025-12-30', 'amount': 5.8, 'note': 'Continued stress'},
    {'date': '2025-12-31', 'amount': 0, 'note': 'Holiday'},
]

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
# CUSTOM CSS
# =============================================================================
st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; }
    h1, h2, h3, h4 { color: #e8e8f0 !important; }
    [data-testid="stMetricLabel"] { color: #8888a0 !important; }
    [data-testid="stMetricValue"] { color: #e8e8f0 !important; }
    .alert-critical { 
        background: rgba(255,59,92,0.15);
        border: 1px solid #ff3b5c;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .alert-warning {
        background: rgba(255,140,66,0.15);
        border: 1px solid #ff8c42;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .alert-info {
        background: rgba(59,130,246,0.15);
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .countdown-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #ff3b5c;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    .countdown-number {
        font-size: 48px;
        font-weight: bold;
        color: #ff3b5c;
    }
    .stress-meter {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .domino-box {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 10px;
        margin: 5px;
        border-left: 4px solid #3b82f6;
    }
    .metric-card {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    .scenario-card {
        text-align: center;
        padding: 15px;
        background: #1a1a2e;
        border-radius: 10px;
        margin: 5px;
    }
    .bank-card {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #ff3b5c;
    }
    .fed-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #1e3a5f 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #3b82f6;
    }
    .bailout-bar {
        background: #2a2a4a;
        height: 24px;
        border-radius: 12px;
        margin: 5px 0;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

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
    # Current known Fed repo
    current_repo = 23.05  # billions
    
    # Calculate what's needed
    ms_loss = MS_SHORT_POSITION_OZ * (silver_price - 30)
    jpm_potential_loss = 437.4e9 * 0.25  # 25% of PM derivatives
    citi_potential_loss = 204.3e9 * 0.25
    
    total_potential_loss = ms_loss + jpm_potential_loss + citi_potential_loss
    total_potential_loss_b = total_potential_loss / 1e9
    
    coverage_pct = (current_repo / total_potential_loss_b) * 100 if total_potential_loss_b > 0 else 0
    
    return {
        'current_repo': current_repo,
        'ms_need': ms_loss / 1e9,
        'jpm_need': jpm_potential_loss / 1e9,
        'citi_need': citi_potential_loss / 1e9,
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
    
    # Countdown alerts
    if countdown['days'] < 7 and not countdown['expired']:
        alerts.append({'level': 'critical', 'title': '⏰ DEADLINE IMMINENT',
            'msg': f"Only {countdown['days']} days until SEC Feb 15 deadline.",
            'action': 'Maximum alert. MS must act soon.'})
    elif countdown['days'] < 14 and not countdown['expired']:
        alerts.append({'level': 'warning', 'title': '⏰ DEADLINE APPROACHING',
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
    """Render main dashboard tab"""
    
    risk_color = '#ff3b5c' if risk_index >= 7 else '#ff8c42' if risk_index >= 5 else '#4ade80'
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("## 📊 System Overview")
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="color:#8888a0;font-size:11px;">RISK INDEX</div>
            <div style="color:{risk_color};font-size:36px;font-weight:bold;">{risk_index:.1f}/10</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        n_crit = len([a for a in alerts if a['level'] == 'critical'])
        n_warn = len([a for a in alerts if a['level'] == 'warning'])
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="color:#8888a0;font-size:11px;">ALERTS</div>
            <div style="font-size:24px;"><span style="color:#ff3b5c;">{n_crit}🔴</span> <span style="color:#ff8c42;">{n_warn}🟠</span></div>
        </div>""", unsafe_allow_html=True)
    
    if alerts:
        with st.expander(f"🚨 Active Alerts ({len(alerts)})", expanded=True):
            for a in alerts[:5]:
                css_class = f"alert-{a['level']}" if a['level'] != 'info' else 'alert-info'
                st.markdown(f'<div class="{css_class}"><strong>{a["title"]}</strong><br>{a["msg"]}<br><em style="color:#aaa;">→ {a["action"]}</em></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Scenario probabilities
    st.markdown("### 📊 Scenario Probabilities")
    scenario_config = {
        'slow_burn': {'name': 'Slow Burn', 'color': '#4ade80'},
        'credit_crunch': {'name': 'Credit Crunch', 'color': '#ff3b5c'},
        'inflation_spike': {'name': 'Inflation', 'color': '#ff8c42'},
        'deflation_bust': {'name': 'Deflation', 'color': '#3b82f6'},
        'monetary_reset': {'name': 'Reset', 'color': '#a855f7'},
    }
    cols = st.columns(5)
    for i, (key, prob) in enumerate(scenarios.items()):
        cfg = scenario_config.get(key, {'name': key, 'color': '#888'})
        with cols[i]:
            st.markdown(f"""
            <div class="scenario-card" style="border-left:4px solid {cfg['color']};">
                <div style="color:#8888a0;font-size:10px;">{cfg['name']}</div>
                <div style="color:{cfg['color']};font-size:28px;font-weight:bold;">{prob*100:.0f}%</div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Real-time prices
    st.markdown("### 📈 Real-Time Prices")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        g = prices.get('gold', {})
        st.metric("🥇 Gold", f"${g.get('price', 0):,.0f}", f"{g.get('change_pct', 0):+.2f}%")
    with c2:
        s = prices.get('silver', {})
        st.metric("🥈 Silver", f"${s.get('price', 0):.2f}", f"{s.get('change_pct', 0):+.2f}%")
    with c3:
        r = prices.get('gold_silver_ratio', {})
        st.metric("⚖️ G/S Ratio", f"{r.get('price', 0):.1f}", "")
    with c4:
        v = prices.get('vix', {})
        st.metric("😰 VIX", f"{v.get('price', 0):.1f}", f"{v.get('change_pct', 0):+.1f}%", delta_color="inverse")
    with c5:
        b = prices.get('bitcoin', {})
        st.metric("₿ Bitcoin", f"${b.get('price', 0):,.0f}", f"{b.get('change_pct', 0):+.1f}%")
    with c6:
        d = prices.get('dollar_index', {})
        st.metric("💵 DXY", f"{d.get('price', 0):.1f}", f"{d.get('change_pct', 0):+.1f}%")
    
    # Row 2
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        x = prices.get('gold_miners', {})
        st.metric("⛏️ GDX", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")
    with c2:
        x = prices.get('silver_miners', {})
        st.metric("⛏️ SILJ", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")
    with c3:
        x = prices.get('regional_banks', {})
        st.metric("🏦 KRE", f"${x.get('price', 0):.2f}", f"{x.get('week_change', 0):+.1f}%wk")
    with c4:
        x = prices.get('high_yield', {})
        st.metric("📉 HYG", f"${x.get('price', 0):.2f}", f"{x.get('week_change', 0):+.1f}%wk")
    with c5:
        x = prices.get('long_treasury', {})
        st.metric("📜 TLT", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")
    with c6:
        x = prices.get('sp500', {})
        st.metric("📊 SPY", f"${x.get('price', 0):.2f}", f"{x.get('change_pct', 0):+.1f}%")

def render_ms_collapse_tab(prices, countdown, stress_level, ms_exposure):
    """Render MS Collapse tracking tab"""
    
    st.markdown(f"""
    <div class="countdown-box">
        <div style="color:#8888a0;font-size:14px;text-transform:uppercase;letter-spacing:2px;">⏰ SEC DEADLINE COUNTDOWN</div>
        <div class="countdown-number">{countdown['days']} DAYS : {countdown['hours']:02d} HRS : {countdown['minutes']:02d} MIN</div>
        <div style="color:#ff8c42;font-size:14px;margin-top:10px;">February 15, 2026 - MS must close 5.9B oz silver short</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🏦 Morgan Stanley Stress Monitor")
        stress_color = '#4ade80' if stress_level < 30 else '#fbbf24' if stress_level < 50 else '#ff8c42' if stress_level < 70 else '#ff3b5c'
        stress_label = 'LOW' if stress_level < 30 else 'MODERATE' if stress_level < 50 else 'HIGH' if stress_level < 70 else 'CRITICAL'
        st.markdown(f"""
        <div class="stress-meter">
            <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                <span style="color:#e8e8f0;">Stress Level: <strong>{stress_label}</strong></span>
                <span style="color:{stress_color};font-size:24px;font-weight:bold;">{stress_level}/100</span>
            </div>
            <div style="background:#2a2a4a;height:30px;border-radius:15px;overflow:hidden;">
                <div style="background:linear-gradient(90deg, #4ade80, #fbbf24, #ff8c42, #ff3b5c);width:{stress_level}%;height:100%;border-radius:15px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💀 Theoretical Losses")
        st.metric("Paper Loss", f"${ms_exposure['paper_loss']/1e9:.0f}B")
        st.metric("vs Equity", f"{ms_exposure['loss_vs_equity']:.1f}x")
        if ms_exposure['insolvent']:
            st.error(f"⚠️ INSOLVENT ({ms_exposure['insolvency_multiple']:.1f}x)")
    
    st.markdown("---")
    
    # Bank stocks
    st.markdown("### 🏦 Bank Stock Monitor")
    c1, c2, c3, c4, c5 = st.columns(5)
    banks = [('morgan_stanley', '🎯 MS'), ('jpmorgan', 'JPM'), ('citibank', 'C'), ('bank_of_america', 'BAC'), ('goldman', 'GS')]
    for col, (key, name) in zip([c1, c2, c3, c4, c5], banks):
        with col:
            b = prices.get(key, {})
            st.metric(name, f"${b.get('price', 0):.2f}", f"{b.get('change_pct', 0):+.2f}%")

def render_bank_exposure_tab(prices, bank_risk_scores):
    """Render Bank Exposure tab"""
    
    st.markdown("### 🏦 Bank PM Derivatives Exposure")
    st.markdown("*Data from OCC Q3 2025 Quarterly Report on Bank Derivatives*")
    
    st.markdown("---")
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        total_pm = 437.4 + 204.3 + 47.9 + 0.6
        st.metric("Total US Bank PM Derivatives", f"${total_pm:.1f}B")
    with col2:
        st.metric("JPM + Citi Share", "91.1%", "Extreme concentration")
    with col3:
        st.metric("Banks Tracked", "10", "US + European")
    
    st.markdown("---")
    
    # Tier 1: US Big Banks
    st.markdown("### 🔴 TIER 1: Extreme Risk (US Majors)")
    
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
                    <span style="color:#e8e8f0;font-size:20px;font-weight:bold;">{bank['name']}</span>
                    <span style="color:#888;font-size:14px;margin-left:10px;">({bank['ticker']})</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:{score_color};font-size:24px;font-weight:bold;">{score}/100</span>
                    <span style="color:#888;font-size:12px;"> RISK</span>
                </div>
            </div>
            <div style="display:flex;gap:30px;margin-top:10px;">
                <div><span style="color:#888;">PM Derivatives:</span> <span style="color:#e8e8f0;font-weight:bold;">{pm_display}</span></div>
                <div><span style="color:#888;">% of Total:</span> <span style="color:#e8e8f0;">{pct_display}</span></div>
                <div><span style="color:#888;">Equity:</span> <span style="color:#e8e8f0;">${bank['equity']/1e9:.0f}B</span></div>
                <div><span style="color:#888;">Price:</span> <span style="color:#e8e8f0;">${risk.get('price', 0):.2f}</span> <span style="color:{'#ff3b5c' if risk.get('daily_change', 0) < 0 else '#4ade80'};">{risk.get('daily_change', 0):+.2f}%</span></div>
            </div>
            {f'<div style="color:#ff8c42;font-size:12px;margin-top:5px;">⚠️ {bank.get("note", "")}</div>' if bank.get('note') else ''}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tier 2: Other US Banks
    st.markdown("### 🟠 TIER 2: High Risk")
    
    col1, col2 = st.columns(2)
    for i, key in enumerate(['BAC', 'GS']):
        bank = BANK_PM_EXPOSURE[key]
        risk = bank_risk_scores.get(key, {})
        with col1 if i == 0 else col2:
            pm_display = f"${bank['pm_derivatives']/1e9:.1f}B" if bank['pm_derivatives'] else "N/A"
            st.markdown(f"""
            <div class="bank-card" style="border-left-color:#ff8c42;">
                <div style="font-size:16px;font-weight:bold;color:#e8e8f0;">{bank['name']} ({bank['ticker']})</div>
                <div style="color:#888;font-size:12px;">PM Derivatives: {pm_display} | Equity: ${bank['equity']/1e9:.0f}B</div>
                <div style="color:#888;font-size:12px;">Price: ${risk.get('price', 0):.2f} ({risk.get('daily_change', 0):+.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tier 3: European Banks
    st.markdown("### 🟡 TIER 3: European Exposure (LBMA)")
    
    cols = st.columns(3)
    for i, key in enumerate(['HSBC', 'DB', 'UBS', 'BCS', 'BNS']):
        bank = BANK_PM_EXPOSURE[key]
        risk = bank_risk_scores.get(key, {})
        with cols[i % 3]:
            st.markdown(f"""
            <div class="bank-card" style="border-left-color:#fbbf24;">
                <div style="font-size:14px;font-weight:bold;color:#e8e8f0;">{bank['name']}</div>
                <div style="color:#888;font-size:11px;">{bank['ticker']} | ${risk.get('price', 0):.2f}</div>
                <div style="color:#ff8c42;font-size:10px;">{bank.get('note', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Put options table
    st.markdown("### 🎯 Suggested Put Options (Contagion Plays)")
    
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
    
    # Big numbers
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Known Fed Repo", f"${fed['current_repo']:.1f}B", "Dec 27-30 combined")
    with col2:
        coverage_color = "inverse" if fed['coverage_pct'] < 20 else "normal"
        st.metric("Coverage", f"{fed['coverage_pct']:.1f}%", "of potential losses", delta_color=coverage_color)
    with col3:
        st.metric("Gap Needed", f"${fed['gap']:.0f}B", "to cover losses")
    with col4:
        st.metric("Adequate?", "NO ❌" if not fed['adequate'] else "YES ✅", "")
    
    st.markdown("---")
    
    # Visual comparison
    st.markdown("### 📊 Fed Response vs Potential Losses")
    
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
                <span style="color:#e8e8f0;">MS Potential Loss</span>
                <span style="color:#ff3b5c;font-weight:bold;">${fed['ms_need']:.0f}B</span>
            </div>
            <div class="bailout-bar">
                <div style="background:#ff3b5c;width:{min(fed['ms_need']/500*100, 100):.1f}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>
        
        <div style="margin-bottom:15px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:#e8e8f0;">JPM Potential Loss (25%)</span>
                <span style="color:#ff8c42;font-weight:bold;">${fed['jpm_need']:.0f}B</span>
            </div>
            <div class="bailout-bar">
                <div style="background:#ff8c42;width:{min(fed['jpm_need']/500*100, 100):.1f}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>
        
        <div style="margin-bottom:15px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                <span style="color:#e8e8f0;">Citi Potential Loss (25%)</span>
                <span style="color:#fbbf24;font-weight:bold;">${fed['citi_need']:.0f}B</span>
            </div>
            <div class="bailout-bar">
                <div style="background:#fbbf24;width:{min(fed['citi_need']/500*100, 100):.1f}%;height:100%;border-radius:12px;"></div>
            </div>
        </div>
        
        <div style="border-top:1px solid #444;padding-top:15px;margin-top:15px;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#e8e8f0;font-weight:bold;">TOTAL POTENTIAL LOSSES</span>
                <span style="color:#ff3b5c;font-weight:bold;font-size:20px;">${fed['total_need']:.0f}B</span>
            </div>
        </div>
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
        If Morgan Stanley owes 5.9 billion oz of silver and silver is at $300, they owe $1.77 TRILLION. 
        The Fed cannot print silver. The Fed cannot make that debt disappear. The Fed can only delay the inevitable.
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
    
    # Header
    st.markdown("""
    <div style="text-align:center;padding:10px 0;">
        <h1 style="font-size:42px;margin:0;">⚠️ FAULT.WATCH</h1>
        <p style="color:#888;font-size:14px;">Complete Crisis Monitor • Fed Response Tracker • Bank Exposure</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard",
        "🏦 MS Collapse",
        "💀 Bank Exposure",
        "🏛️ Fed Response",
        "🎯 Dominoes",
        "💰 Positions",
        "📈 Scenarios"
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
    
    # Footer
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** Based on UNVERIFIED whistleblower information. NOT financial advice. Risk of total loss.")
    st.caption(f"fault.watch v4.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
