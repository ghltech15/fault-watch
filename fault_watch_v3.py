"""
FAULT.WATCH v3.0 - COMPREHENSIVE EDITION
=========================================
Adaptive Systemic Risk Monitoring System
With Morgan Stanley Silver Short Tracking

TABS:
1. Dashboard - Main overview with all indicators
2. MS Collapse - Morgan Stanley tracking & countdown
3. Domino Effects - Cascade tracker
4. My Positions - Trade tracking & P/L calculator
5. Scenarios - Detailed scenario analysis

Run with: streamlit run fault_watch.py
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
        
        # Banks - CRITICAL
        'MS': 'morgan_stanley',
        'JPM': 'jpmorgan',
        'C': 'citibank',
        'BAC': 'bank_of_america',
        'GS': 'goldman',
        
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
            if 'ethereum' in data:
                prices['ethereum'] = {
                    'price': data['ethereum']['usd'],
                    'change_pct': data['ethereum'].get('usd_24h_change', 0),
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
    
    # Domino 7: COMEX (simulated based on silver price)
    if silver > 120: dominoes['comex'] = {'status': 'FAILING', 'color': '#ff3b5c', 'detail': 'Delivery stress'}
    elif silver > 100: dominoes['comex'] = {'status': 'STRESSED', 'color': '#ff8c42', 'detail': 'High demand'}
    else: dominoes['comex'] = {'status': 'NORMAL', 'color': '#4ade80', 'detail': 'Functioning'}
    
    # Domino 8: Fed Response
    if vix > 35 and bank_avg < -5: dominoes['fed'] = {'status': 'EMERGENCY', 'color': '#ff3b5c', 'detail': 'QE likely'}
    elif vix > 30: dominoes['fed'] = {'status': 'WATCHING', 'color': '#ff8c42', 'detail': 'On alert'}
    else: dominoes['fed'] = {'status': 'NORMAL', 'color': '#4ade80', 'detail': 'Status quo'}
    
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
    
    # Gold adjustments
    if gold > 5000:
        probs['monetary_reset'] += 0.10
        probs['inflation_spike'] += 0.05
    elif gold > 4700:
        probs['monetary_reset'] += 0.05
    
    # Bank stress
    if kre < -10:
        probs['credit_crunch'] += 0.20
        probs['deflation_bust'] += 0.10
        probs['slow_burn'] -= 0.25
    elif kre < -5:
        probs['credit_crunch'] += 0.10
        probs['slow_burn'] -= 0.10
    
    # Credit stress
    if hyg < -5:
        probs['credit_crunch'] += 0.15
        probs['deflation_bust'] += 0.10
        probs['slow_burn'] -= 0.20
    elif hyg < -3:
        probs['credit_crunch'] += 0.08
    
    # Dollar weakness
    if dxy < 95:
        probs['monetary_reset'] += 0.15
        probs['inflation_spike'] += 0.05
        probs['slow_burn'] -= 0.15
    elif dxy < 100:
        probs['monetary_reset'] += 0.05
    
    # Gold/Silver ratio
    if gs_ratio < 40:
        probs['monetary_reset'] += 0.10
    elif gs_ratio < 50:
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
    
    # Stress level alerts
    if stress_level > 80:
        alerts.append({'level': 'critical', 'title': '🔥 EXTREME STRESS',
            'msg': f'MS Stress Level at {stress_level}/100.',
            'action': 'Multiple warning signs active. Crisis likely imminent.'})
    elif stress_level > 50:
        alerts.append({'level': 'warning', 'title': '⚠️ ELEVATED STRESS',
            'msg': f'MS Stress Level at {stress_level}/100.',
            'action': 'Conditions deteriorating. Stay alert.'})
    
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
    
    # VIX alerts
    vix = indicators.get('vix', 15)
    if vix > THRESHOLDS['vix']['critical']:
        alerts.append({'level': 'critical', 'title': '🔴 EXTREME VOLATILITY',
            'msg': f'VIX at {vix:.1f} - Risk-off event in progress.',
            'action': 'Activate hedges'})
    elif vix > THRESHOLDS['vix']['warning']:
        alerts.append({'level': 'warning', 'title': '🟠 Elevated Volatility',
            'msg': f'VIX at {vix:.1f} - Market stress elevated.',
            'action': 'Prepare hedges'})
    
    # Bank stress
    kre = indicators.get('kre_weekly', 0)
    if kre < THRESHOLDS['kre_weekly']['critical']:
        alerts.append({'level': 'critical', 'title': '🔴 BANK CRISIS SIGNAL',
            'msg': f'Regional banks (KRE) down {kre:.1f}% this week!',
            'action': 'Execute bank crisis playbook'})
    elif kre < THRESHOLDS['kre_weekly']['warning']:
        alerts.append({'level': 'warning', 'title': '🟠 Bank Stress',
            'msg': f'Regional banks (KRE) down {kre:.1f}% this week.',
            'action': 'Prepare short positions'})
    
    # Dollar alerts
    dxy = indicators.get('dollar_index', 102)
    if dxy < THRESHOLDS['dollar_index']['critical']:
        alerts.append({'level': 'critical', 'title': '🔴 DOLLAR CRISIS',
            'msg': f'Dollar index at {dxy:.1f} - Below critical support!',
            'action': 'Maximum precious metals allocation'})
    
    # Bitcoin opportunity
    btc = indicators.get('bitcoin', 91000)
    if btc < THRESHOLDS['bitcoin']['strong_buy']:
        alerts.append({'level': 'info', 'title': '🟢 BITCOIN ACCUMULATION ZONE',
            'msg': f'Bitcoin at ${btc:,.0f} - Strong buy zone!',
            'action': 'Scale in aggressively'})
    elif btc < THRESHOLDS['bitcoin']['buy_zone']:
        alerts.append({'level': 'info', 'title': '🟢 Bitcoin Buy Zone',
            'msg': f'Bitcoin at ${btc:,.0f} - Accumulation opportunity.',
            'action': 'Consider adding'})
    
    return alerts

# =============================================================================
# TAB CONTENT FUNCTIONS
# =============================================================================

def render_dashboard_tab(prices, indicators, scenarios, allocation, alerts, risk_index):
    """Render main dashboard tab"""
    
    # Header with risk index
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
    
    # Alerts section
    if alerts:
        with st.expander(f"🚨 Active Alerts ({len(alerts)})", expanded=True):
            for a in alerts[:5]:  # Show top 5
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
    
    # Real-time prices - Row 1
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
    
    st.markdown("---")
    
    # Allocation
    st.markdown("### 🎯 Recommended Allocation")
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.pie(values=list(allocation.values()), names=list(allocation.keys()),
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font_color='#e8e8f0', showlegend=True)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**Target Weights:**")
        for asset, wt in allocation.items():
            st.markdown(f"- {asset}: **{wt*100:.1f}%**")

def render_ms_collapse_tab(prices, countdown, stress_level, ms_exposure):
    """Render MS Collapse tracking tab"""
    
    # Countdown timer
    st.markdown(f"""
    <div class="countdown-box">
        <div style="color:#8888a0;font-size:14px;text-transform:uppercase;letter-spacing:2px;">⏰ SEC DEADLINE COUNTDOWN</div>
        <div class="countdown-number">{countdown['days']} DAYS : {countdown['hours']:02d} HRS : {countdown['minutes']:02d} MIN</div>
        <div style="color:#ff8c42;font-size:14px;margin-top:10px;">February 15, 2026 - MS must close 5.9B oz silver short</div>
        <div style="color:#666;font-size:11px;margin-top:5px;">Based on whistleblower report filed Jan 7, 2026</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stress meter and losses
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
            <div style="display:flex;justify-content:space-between;margin-top:5px;color:#666;font-size:10px;">
                <span>Normal</span><span>Elevated</span><span>High</span><span>Critical</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💀 Theoretical Losses")
        st.metric("Paper Loss", f"${ms_exposure['paper_loss']/1e9:.0f}B")
        st.metric("vs $100B Equity", f"{ms_exposure['loss_vs_equity']:.1f}x")
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
    
    st.markdown("---")
    
    # Price calculator
    st.markdown("### 📈 Silver Price Impact Calculator")
    silver_target = st.slider("Silver Target Price", 80, 500, 289, 10)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        ms_loss = MS_SHORT_POSITION_OZ * (silver_target - 30)
        st.metric("MS Paper Loss", f"${ms_loss/1e12:.2f}T")
        st.metric("vs Equity", f"{ms_loss/1e11:.0f}x")
    with c2:
        slv_target = silver_target * 0.897 * 1.02
        st.metric("SLV Price Est.", f"${slv_target:.0f}")
    with c3:
        ms_stock_est = max(0, 135 - (ms_loss / 1e9 / 10)) if ms_loss > 100e9 else 135
        st.metric("MS Stock Est.", f"${max(0, ms_stock_est):.0f}")

def render_domino_tab(prices, dominoes):
    """Render Domino Effects tab"""
    
    st.markdown("### 🎯 Domino Effect Monitor")
    st.markdown("*Track the cascade of potential failures*")
    
    # Main dominoes
    domino_config = [
        ('ms_stock', 'Domino 1: MS Stock', '🏦', 'Morgan Stanley stock price collapse'),
        ('silver', 'Domino 2: Silver', '🥈', 'Silver price explosion from short covering'),
        ('other_banks', 'Domino 3: Other Banks', '🏛️', 'Contagion to JPM, Citi, BAC'),
        ('credit', 'Domino 4: Credit Markets', '📉', 'High yield spreads blow out'),
        ('fear', 'Domino 5: VIX/Fear', '😰', 'Market panic and volatility'),
        ('dollar', 'Domino 6: Dollar', '💵', 'Dollar weakness from Fed response'),
        ('comex', 'Domino 7: COMEX', '🏪', 'Exchange delivery failures'),
        ('fed', 'Domino 8: Fed Response', '🏛️', 'Emergency QE and bailouts'),
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
    
    st.markdown("---")
    st.markdown("### 📋 Domino Cascade Timeline")
    st.markdown("""
    | Phase | Timeline | Events |
    |-------|----------|--------|
    | **Phase 1** | Days 1-14 | MS collapse, silver to $150+ |
    | **Phase 2** | Days 10-25 | Other banks stress, credit spreads widen |
    | **Phase 3** | Days 20-40 | COMEX stress, Fed emergency meetings |
    | **Phase 4** | Days 30-60 | Full crisis, QE announced, dollar drops |
    | **Phase 5** | Months 2-6 | Recession, monetary system discussions |
    """)

def render_positions_tab(prices):
    """Render My Positions tab"""
    
    st.markdown("### 💰 Your Position Tracker")
    
    # Current positions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SLV $145 Call (Feb 20, 2026)")
        slv_price = prices.get('slv', {}).get('price', 72)
        st.markdown(f"**Current SLV Price:** ${slv_price:.2f}")
        st.markdown(f"**Strike Price:** $145.00")
        st.markdown(f"**Distance to Strike:** ${145 - slv_price:.2f}")
        st.markdown(f"**Contracts:** 200")
        st.markdown(f"**Cost Basis:** $2,200")
        
        if slv_price >= 145:
            itm_value = (slv_price - 145) * 200 * 100
            st.success(f"✅ IN THE MONEY! Value: ${itm_value:,.0f}")
        else:
            st.info(f"⏳ Out of the money - needs ${145 - slv_price:.2f} move")
    
    with col2:
        st.markdown("#### MS $60 Put (Mar 21, 2026)")
        ms_price = prices.get('morgan_stanley', {}).get('price', 135)
        st.markdown(f"**Current MS Price:** ${ms_price:.2f}")
        st.markdown(f"**Strike Price:** $60.00")
        st.markdown(f"**Distance to Strike:** ${ms_price - 60:.2f}")
        st.markdown(f"**Contracts:** 1,000")
        st.markdown(f"**Cost Basis:** $1,000")
        
        if ms_price <= 60:
            itm_value = (60 - ms_price) * 1000 * 100
            st.success(f"✅ IN THE MONEY! Value: ${itm_value:,.0f}")
        else:
            st.info(f"⏳ Out of the money - needs ${ms_price - 60:.2f} drop")
    
    st.markdown("---")
    
    # P&L Calculator
    st.markdown("### 📊 P&L Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        silver_input = st.number_input("Silver Price at Exit", 80, 500, 289)
    with col2:
        ms_input = st.number_input("MS Stock Price at Exit", 0, 150, 0)
    
    # Calculate P&L
    slv_at_exit = silver_input * 0.897 * 1.02
    slv_call_value = max(0, (slv_at_exit - 145)) * 200 * 100
    slv_profit = slv_call_value - 2200
    
    ms_put_value = max(0, (60 - ms_input)) * 1000 * 100
    ms_profit = ms_put_value - 1000
    
    total_profit = slv_profit + ms_profit
    total_cost = 3200
    total_return = (total_profit / total_cost) * 100 if total_cost > 0 else 0
    
    st.markdown("---")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("SLV Call P&L", f"${slv_profit:,.0f}", f"{(slv_profit/2200)*100:+.0f}%" if slv_profit != -2200 else "-100%")
    with c2:
        st.metric("MS Put P&L", f"${ms_profit:,.0f}", f"{(ms_profit/1000)*100:+.0f}%" if ms_profit != -1000 else "-100%")
    with c3:
        color = "normal" if total_profit >= 0 else "inverse"
        st.metric("TOTAL P&L", f"${total_profit:,.0f}", f"{total_return:+.0f}%", delta_color=color)
    
    st.markdown("---")
    
    # Scenario table
    st.markdown("### 📋 Scenario Outcomes")
    scenarios_data = [
        {"Scenario": "Nothing happens", "Silver": "$80", "MS": "$135", "SLV Calls": "-$2,200", "MS Puts": "-$1,000", "Total": "-$3,200"},
        {"Scenario": "Mild squeeze", "Silver": "$120", "MS": "$100", "SLV Calls": "-$2,200", "MS Puts": "-$1,000", "Total": "-$3,200"},
        {"Scenario": "MS stress", "Silver": "$150", "MS": "$60", "SLV Calls": "-$2,200", "MS Puts": "$0", "Total": "-$2,200"},
        {"Scenario": "Major squeeze", "Silver": "$200", "MS": "$40", "SLV Calls": "$660K", "MS Puts": "$2M", "Total": "$2.66M"},
        {"Scenario": "MS collapse", "Silver": "$289", "MS": "$5", "SLV Calls": "$2.3M", "MS Puts": "$5.5M", "Total": "$7.8M"},
        {"Scenario": "Full crisis", "Silver": "$350", "MS": "$0", "SLV Calls": "$3.4M", "MS Puts": "$6M", "Total": "$9.4M"},
    ]
    st.table(pd.DataFrame(scenarios_data))

def render_scenarios_tab(scenarios, allocation):
    """Render detailed Scenarios tab"""
    
    st.markdown("### 📊 Scenario Analysis")
    
    scenario_details = {
        'slow_burn': {
            'name': 'Slow Burn',
            'color': '#4ade80',
            'desc': 'Status quo continues with gradual deterioration',
            'triggers': ['Inflation stays 2-3%', 'No major bank failures', 'Fed maintains policy'],
            'winners': ['Quality stocks', 'Gold (modest)', 'Energy'],
            'losers': ['Long-duration bonds', 'Unprofitable tech'],
        },
        'credit_crunch': {
            'name': 'Credit Crunch',
            'color': '#ff3b5c',
            'desc': 'Banking crisis triggered by MS collapse or CRE defaults',
            'triggers': ['MS bankruptcy', 'Regional bank failures', 'CRE defaults spike'],
            'winners': ['Gold', 'Silver miners', 'Long Treasuries', 'Bank puts'],
            'losers': ['Bank stocks', 'Real estate', 'High yield bonds'],
        },
        'inflation_spike': {
            'name': 'Inflation Spike',
            'color': '#ff8c42',
            'desc': 'Inflation reaccelerates despite Fed efforts',
            'triggers': ['CPI above 5%', 'Fed forced to cut anyway', 'Wage spiral'],
            'winners': ['Silver', 'Energy', 'TIPS', 'Bitcoin'],
            'losers': ['Long bonds', 'Growth stocks', 'Cash'],
        },
        'deflation_bust': {
            'name': 'Deflation Bust',
            'color': '#3b82f6',
            'desc': 'Credit collapse leads to deflationary depression',
            'triggers': ['Major credit event', 'Consumer spending collapse', 'Asset prices crater'],
            'winners': ['Cash', 'Long Treasuries', 'Gold'],
            'losers': ['Everything else', 'Commodities', 'Stocks'],
        },
        'monetary_reset': {
            'name': 'Monetary Reset',
            'color': '#a855f7',
            'desc': 'Dollar crisis forces new monetary framework',
            'triggers': ['Dollar index below 90', 'Treasury auction failures', 'Gold above $5000'],
            'winners': ['Gold', 'Silver', 'Mining stocks', 'Bitcoin'],
            'losers': ['Dollar assets', 'Bonds', 'Bank stocks'],
        },
    }
    
    for key, prob in scenarios.items():
        details = scenario_details.get(key, {})
        with st.expander(f"{details.get('name', key)} - {prob*100:.0f}%", expanded=(prob > 0.20)):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
                <div style="text-align:center;padding:20px;background:#1a1a2e;border-radius:10px;border-left:4px solid {details.get('color', '#888')};">
                    <div style="color:{details.get('color', '#888')};font-size:48px;font-weight:bold;">{prob*100:.0f}%</div>
                    <div style="color:#888;font-size:12px;">Probability</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Description:** {details.get('desc', '')}")
                st.markdown("**Triggers:**")
                for t in details.get('triggers', []):
                    st.markdown(f"- {t}")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Winners:** " + ", ".join(details.get('winners', [])))
                with col_b:
                    st.markdown("**Losers:** " + ", ".join(details.get('losers', [])))

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # Sidebar
    st.sidebar.title("⚠️ fault.watch v3.0")
    st.sidebar.caption("Comprehensive Edition")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown(f"**Last Update:**")
    st.sidebar.markdown(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Links")
    st.sidebar.markdown("- [NYSE MS](https://www.nyse.com/quote/XNYS:MS)")
    st.sidebar.markdown("- [COMEX Silver](https://www.cmegroup.com/markets/metals/precious/silver.html)")
    st.sidebar.markdown("- [Fed Repo](https://www.newyorkfed.org/markets/desk-operations)")
    st.sidebar.markdown("- [CFTC COT](https://www.cftc.gov/dea/futures/deacmxsf.htm)")
    
    # Fetch all data
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
    alerts = generate_all_alerts(indicators, prices, countdown, stress_level)
    
    risk_index = sum(scenarios.get(s, 0) * w for s, w in [
        ('slow_burn', 5), ('credit_crunch', 9), ('inflation_spike', 7),
        ('deflation_bust', 9), ('monetary_reset', 10)
    ])
    
    # Header
    st.markdown("""
    <div style="text-align:center;padding:10px 0;">
        <h1 style="font-size:42px;margin:0;">⚠️ FAULT.WATCH</h1>
        <p style="color:#888;font-size:14px;">Adaptive Systemic Risk Intelligence • MS Collapse Tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "🏦 MS Collapse",
        "🎯 Domino Effects",
        "💰 My Positions",
        "📈 Scenarios"
    ])
    
    with tab1:
        render_dashboard_tab(prices, indicators, scenarios, allocation, alerts, risk_index)
    
    with tab2:
        render_ms_collapse_tab(prices, countdown, stress_level, ms_exposure)
    
    with tab3:
        render_domino_tab(prices, dominoes)
    
    with tab4:
        render_positions_tab(prices)
    
    with tab5:
        render_scenarios_tab(scenarios, allocation)
    
    # Footer
    st.markdown("---")
    st.caption("⚠️ **Disclaimer:** Based on UNVERIFIED whistleblower information. NOT financial advice. Risk of total loss. Data from Yahoo Finance & CoinGecko.")
    st.caption(f"fault.watch v3.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
