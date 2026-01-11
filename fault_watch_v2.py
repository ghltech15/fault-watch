"""
FAULT.WATCH v2.0 - MS COLLAPSE EDITION
=======================================
Adaptive Systemic Risk Monitoring System
With Morgan Stanley Silver Short Tracking

Run with: streamlit run fault_watch_v2.py
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

# Page config
st.set_page_config(page_title="fault.watch", page_icon="⚠️", layout="wide")

# =============================================================================
# CONSTANTS
# =============================================================================

SEC_DEADLINE = datetime(2026, 2, 15, 16, 0, 0)
MS_SHORT_POSITION_OZ = 5_900_000_000

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; }
    h1, h2, h3, h4 { color: #e8e8f0 !important; }
    [data-testid="stMetricLabel"] { color: #8888a0 !important; }
    [data-testid="stMetricValue"] { color: #e8e8f0 !important; }
    .alert-critical { background: rgba(255,59,92,0.15); border: 1px solid #ff3b5c; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .alert-warning { background: rgba(255,140,66,0.15); border: 1px solid #ff8c42; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .alert-info { background: rgba(59,130,246,0.15); border: 1px solid #3b82f6; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .countdown-box { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border: 2px solid #ff3b5c; border-radius: 15px; padding: 20px; text-align: center; margin: 20px 0; }
    .countdown-number { font-size: 48px; font-weight: bold; color: #ff3b5c; }
    .stress-meter { background: #1a1a2e; border-radius: 10px; padding: 15px; margin: 10px 0; }
    .domino-box { background: #1a1a2e; border-radius: 8px; padding: 10px; margin: 5px; border-left: 4px solid #3b82f6; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA FETCHING
# =============================================================================

@st.cache_data(ttl=60)
def fetch_all_prices():
    prices = {}
    yf_tickers = {
        'SPY': 'sp500', '^VIX': 'vix', 'TLT': 'long_treasury', 'DX-Y.NYB': 'dollar_index',
        'GC=F': 'gold', 'SI=F': 'silver', 'GDX': 'gold_miners', 'SILJ': 'silver_miners', 'SLV': 'slv',
        'MS': 'morgan_stanley', 'JPM': 'jpmorgan', 'C': 'citibank', 'BAC': 'bank_of_america', 'GS': 'goldman',
        'KRE': 'regional_banks', 'XLF': 'financials', 'HYG': 'high_yield', 'XLE': 'energy', '^TNX': 'treasury_10y',
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
                    'price': current, 'prev_close': prev,
                    'change_pct': ((current / prev) - 1) * 100 if prev != 0 else 0,
                    'week_change': ((current / first) - 1) * 100 if first != 0 else 0,
                }
        except:
            continue
    
    try:
        resp = requests.get('https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin', 'vs_currencies': 'usd', 'include_24hr_change': 'true'}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if 'bitcoin' in data:
                prices['bitcoin'] = {'price': data['bitcoin']['usd'], 'change_pct': data['bitcoin'].get('usd_24h_change', 0), 'week_change': 0}
    except:
        prices['bitcoin'] = {'price': 91000, 'change_pct': 0, 'week_change': 0}
    
    if 'gold' in prices and 'silver' in prices and prices['silver']['price'] > 0:
        prices['gold_silver_ratio'] = {'price': prices['gold']['price'] / prices['silver']['price'], 'change_pct': 0}
    
    return prices

def calculate_ms_exposure(silver_price, entry_price=30):
    position_oz = MS_SHORT_POSITION_OZ
    current_value = position_oz * silver_price
    entry_value = position_oz * entry_price
    paper_loss = current_value - entry_value
    ms_equity = 100_000_000_000
    return {
        'position_oz': position_oz, 'current_value': current_value, 'paper_loss': paper_loss,
        'loss_vs_equity': paper_loss / ms_equity, 'insolvent': paper_loss > ms_equity,
        'insolvency_multiple': paper_loss / ms_equity if paper_loss > ms_equity else 0
    }

def calculate_countdown():
    now = datetime.now()
    remaining = SEC_DEADLINE - now
    if remaining.total_seconds() <= 0:
        return {'days': 0, 'hours': 0, 'minutes': 0, 'expired': True}
    return {'days': remaining.days, 'hours': remaining.seconds // 3600, 
            'minutes': (remaining.seconds % 3600) // 60, 'expired': False}

def calculate_ms_stress_level(prices):
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
    
    vix = prices.get('vix', {}).get('price', 15)
    if vix > 40: stress += 15
    elif vix > 30: stress += 10
    elif vix > 25: stress += 5
    
    return min(stress, 100)

def calculate_domino_status(prices):
    dominoes = {}
    
    ms = prices.get('morgan_stanley', {})
    ms_price = ms.get('price', 135)
    ms_daily = ms.get('change_pct', 0)
    if ms_price < 80: dominoes['ms_stock'] = {'status': 'CRITICAL', 'color': '#ff3b5c'}
    elif ms_price < 100 or ms_daily < -5: dominoes['ms_stock'] = {'status': 'WARNING', 'color': '#ff8c42'}
    elif ms_daily < -2: dominoes['ms_stock'] = {'status': 'ELEVATED', 'color': '#fbbf24'}
    else: dominoes['ms_stock'] = {'status': 'STABLE', 'color': '#4ade80'}
    
    silver = prices.get('silver', {}).get('price', 80)
    if silver > 150: dominoes['silver'] = {'status': 'EXPLODING', 'color': '#ff3b5c'}
    elif silver > 100: dominoes['silver'] = {'status': 'SQUEEZING', 'color': '#ff8c42'}
    elif silver > 90: dominoes['silver'] = {'status': 'RISING', 'color': '#fbbf24'}
    else: dominoes['silver'] = {'status': 'STABLE', 'color': '#4ade80'}
    
    jpm = prices.get('jpmorgan', {}).get('change_pct', 0)
    c = prices.get('citibank', {}).get('change_pct', 0)
    bac = prices.get('bank_of_america', {}).get('change_pct', 0)
    bank_avg = (jpm + c + bac) / 3
    if bank_avg < -8: dominoes['other_banks'] = {'status': 'CRITICAL', 'color': '#ff3b5c'}
    elif bank_avg < -5: dominoes['other_banks'] = {'status': 'WARNING', 'color': '#ff8c42'}
    elif bank_avg < -2: dominoes['other_banks'] = {'status': 'ELEVATED', 'color': '#fbbf24'}
    else: dominoes['other_banks'] = {'status': 'STABLE', 'color': '#4ade80'}
    
    hyg = prices.get('high_yield', {}).get('week_change', 0)
    if hyg < -5: dominoes['credit'] = {'status': 'FREEZING', 'color': '#ff3b5c'}
    elif hyg < -3: dominoes['credit'] = {'status': 'STRESSED', 'color': '#ff8c42'}
    elif hyg < -1: dominoes['credit'] = {'status': 'ELEVATED', 'color': '#fbbf24'}
    else: dominoes['credit'] = {'status': 'STABLE', 'color': '#4ade80'}
    
    vix = prices.get('vix', {}).get('price', 15)
    if vix > 40: dominoes['fear'] = {'status': 'EXTREME', 'color': '#ff3b5c'}
    elif vix > 30: dominoes['fear'] = {'status': 'HIGH', 'color': '#ff8c42'}
    elif vix > 25: dominoes['fear'] = {'status': 'ELEVATED', 'color': '#fbbf24'}
    else: dominoes['fear'] = {'status': 'NORMAL', 'color': '#4ade80'}
    
    dxy = prices.get('dollar_index', {}).get('price', 102)
    if dxy < 95: dominoes['dollar'] = {'status': 'CRISIS', 'color': '#ff3b5c'}
    elif dxy < 98: dominoes['dollar'] = {'status': 'WEAK', 'color': '#ff8c42'}
    elif dxy < 100: dominoes['dollar'] = {'status': 'DECLINING', 'color': '#fbbf24'}
    else: dominoes['dollar'] = {'status': 'STABLE', 'color': '#4ade80'}
    
    return dominoes

def calculate_scenarios(prices):
    probs = {'slow_burn': 0.35, 'credit_crunch': 0.25, 'inflation_spike': 0.15, 'deflation_bust': 0.15, 'monetary_reset': 0.10}
    
    vix = prices.get('vix', {}).get('price', 15)
    silver = prices.get('silver', {}).get('price', 80)
    ms_daily = prices.get('morgan_stanley', {}).get('change_pct', 0)
    kre_wk = prices.get('regional_banks', {}).get('week_change', 0)
    dxy = prices.get('dollar_index', {}).get('price', 102)
    
    if ms_daily < -10: probs['credit_crunch'] += 0.25; probs['slow_burn'] -= 0.20
    elif ms_daily < -5: probs['credit_crunch'] += 0.15; probs['slow_burn'] -= 0.10
    
    if vix > 35: probs['credit_crunch'] += 0.15; probs['deflation_bust'] += 0.10; probs['slow_burn'] -= 0.20
    
    if silver > 150: probs['monetary_reset'] += 0.30; probs['slow_burn'] -= 0.25
    elif silver > 100: probs['monetary_reset'] += 0.15; probs['slow_burn'] -= 0.15
    
    if kre_wk < -10: probs['credit_crunch'] += 0.20; probs['slow_burn'] -= 0.25
    if dxy < 95: probs['monetary_reset'] += 0.15
    
    total = sum(probs.values())
    return {k: max(0, v/total) for k, v in probs.items()}

def generate_alerts(prices, dominoes, stress_level, countdown):
    alerts = []
    ms = prices.get('morgan_stanley', {})
    ms_daily = ms.get('change_pct', 0)
    ms_price = ms.get('price', 135)
    silver = prices.get('silver', {}).get('price', 80)
    
    if ms_daily < -10:
        alerts.append({'level': 'critical', 'title': '🚨 MS STOCK CRASHING', 
            'msg': f"Morgan Stanley down {ms_daily:.1f}% today.", 'action': 'Check MS puts value.'})
    elif ms_daily < -5:
        alerts.append({'level': 'warning', 'title': '⚠️ MS UNDER PRESSURE',
            'msg': f"Morgan Stanley down {ms_daily:.1f}%.", 'action': 'Watch for acceleration.'})
    
    if ms_price < 100:
        alerts.append({'level': 'critical', 'title': '🚨 MS BELOW $100',
            'msg': f"MS at ${ms_price:.2f}. Critical support broken.", 'action': 'Consider taking put profits.'})
    
    if silver > 150:
        alerts.append({'level': 'critical', 'title': '🚀 SILVER EXPLOSION',
            'msg': f"Silver at ${silver:.2f}. Squeeze in effect.", 'action': 'Scale out of SLV calls.'})
    elif silver > 100:
        alerts.append({'level': 'warning', 'title': '📈 SILVER BREAKOUT',
            'msg': f"Silver above $100 at ${silver:.2f}.", 'action': 'Consider taking 25% profit.'})
    
    if countdown['days'] < 7 and not countdown['expired']:
        alerts.append({'level': 'critical', 'title': '⏰ DEADLINE IMMINENT',
            'msg': f"Only {countdown['days']} days to Feb 15.", 'action': 'Maximum alert.'})
    elif countdown['days'] < 14 and not countdown['expired']:
        alerts.append({'level': 'warning', 'title': '⏰ DEADLINE APPROACHING',
            'msg': f"{countdown['days']} days remaining.", 'action': 'Watch for MS activity.'})
    
    if stress_level > 80:
        alerts.append({'level': 'critical', 'title': '🔥 EXTREME STRESS',
            'msg': f"Stress Level at {stress_level}/100.", 'action': 'Crisis likely imminent.'})
    
    return alerts

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    st.sidebar.title("⚠️ fault.watch v2.0")
    st.sidebar.caption("MS Collapse Edition")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Quick Links")
    st.sidebar.markdown("- [NYSE MS](https://www.nyse.com/quote/XNYS:MS)")
    st.sidebar.markdown("- [COMEX Silver](https://www.cmegroup.com/markets/metals/precious/silver.html)")
    st.sidebar.markdown("- [Fed Repo](https://www.newyorkfed.org/markets/desk-operations)")
    
    prices = fetch_all_prices()
    countdown = calculate_countdown()
    stress_level = calculate_ms_stress_level(prices)
    dominoes = calculate_domino_status(prices)
    scenarios = calculate_scenarios(prices)
    alerts = generate_alerts(prices, dominoes, stress_level, countdown)
    silver_price = prices.get('silver', {}).get('price', 80)
    ms_exposure = calculate_ms_exposure(silver_price)
    
    # HEADER
    st.markdown("""
    <div style="text-align:center;padding:20px 0;">
        <h1 style="font-size:48px;margin:0;">⚠️ FAULT.WATCH</h1>
        <p style="color:#ff3b5c;font-size:18px;">MORGAN STANLEY SILVER SHORT MONITOR</p>
    </div>
    """, unsafe_allow_html=True)
    
    # COUNTDOWN
    st.markdown(f"""
    <div class="countdown-box">
        <div style="color:#8888a0;font-size:14px;text-transform:uppercase;">⏰ SEC DEADLINE COUNTDOWN</div>
        <div class="countdown-number">{countdown['days']} DAYS : {countdown['hours']:02d} HRS : {countdown['minutes']:02d} MIN</div>
        <div style="color:#ff8c42;font-size:14px;margin-top:10px;">February 15, 2026 - MS must close 5.9B oz silver short</div>
    </div>
    """, unsafe_allow_html=True)
    
    # STRESS METER
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
        st.metric("Paper Loss", f"${ms_exposure['paper_loss']/1e9:.0f}B", f"{ms_exposure['loss_vs_equity']:.1f}x equity")
        if ms_exposure['insolvent']:
            st.error(f"⚠️ INSOLVENT ({ms_exposure['insolvency_multiple']:.1f}x)")
    
    st.markdown("---")
    
    # DOMINO TRACKER
    st.markdown("### 🎯 Domino Effect Monitor")
    domino_cols = st.columns(6)
    domino_config = [('ms_stock', 'MS Stock', '🏦'), ('silver', 'Silver', '🥈'), ('other_banks', 'Other Banks', '🏛️'),
                     ('credit', 'Credit', '📉'), ('fear', 'VIX', '😰'), ('dollar', 'Dollar', '💵')]
    
    for i, (key, name, icon) in enumerate(domino_config):
        with domino_cols[i]:
            d = dominoes.get(key, {'status': 'UNKNOWN', 'color': '#666'})
            st.markdown(f"""
            <div class="domino-box" style="border-left-color:{d['color']};">
                <div style="font-size:24px;text-align:center;">{icon}</div>
                <div style="color:#e8e8f0;font-size:11px;text-align:center;">{name}</div>
                <div style="color:{d['color']};font-size:12px;font-weight:bold;text-align:center;">{d['status']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ALERTS
    if alerts:
        st.markdown("### 🚨 Active Alerts")
        for a in alerts:
            st.markdown(f'<div class="alert-{a["level"]}"><strong>{a["title"]}</strong><br>{a["msg"]}<br><em style="color:#aaa;">→ {a["action"]}</em></div>', unsafe_allow_html=True)
        st.markdown("---")
    
    # BANK STOCKS
    st.markdown("### 🏦 Bank Stocks")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        ms = prices.get('morgan_stanley', {})
        st.metric("🎯 MS", f"${ms.get('price', 0):.2f}", f"{ms.get('change_pct', 0):+.2f}%")
    with c2:
        jpm = prices.get('jpmorgan', {})
        st.metric("JPM", f"${jpm.get('price', 0):.2f}", f"{jpm.get('change_pct', 0):+.2f}%")
    with c3:
        c_p = prices.get('citibank', {})
        st.metric("C", f"${c_p.get('price', 0):.2f}", f"{c_p.get('change_pct', 0):+.2f}%")
    with c4:
        bac = prices.get('bank_of_america', {})
        st.metric("BAC", f"${bac.get('price', 0):.2f}", f"{bac.get('change_pct', 0):+.2f}%")
    with c5:
        gs = prices.get('goldman', {})
        st.metric("GS", f"${gs.get('price', 0):.2f}", f"{gs.get('change_pct', 0):+.2f}%")
    
    # PRECIOUS METALS
    st.markdown("### 🥈 Precious Metals")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        silver = prices.get('silver', {})
        st.metric("🥈 Silver", f"${silver.get('price', 0):.2f}", f"{silver.get('change_pct', 0):+.2f}%")
    with c2:
        gold = prices.get('gold', {})
        st.metric("🥇 Gold", f"${gold.get('price', 0):,.0f}", f"{gold.get('change_pct', 0):+.2f}%")
    with c3:
        ratio = prices.get('gold_silver_ratio', {})
        st.metric("⚖️ Ratio", f"{ratio.get('price', 0):.1f}", "")
    with c4:
        slv = prices.get('slv', {})
        st.metric("SLV", f"${slv.get('price', 0):.2f}", f"{slv.get('change_pct', 0):+.2f}%")
    with c5:
        silj = prices.get('silver_miners', {})
        st.metric("SILJ", f"${silj.get('price', 0):.2f}", f"{silj.get('change_pct', 0):+.2f}%")
    with c6:
        gdx = prices.get('gold_miners', {})
        st.metric("GDX", f"${gdx.get('price', 0):.2f}", f"{gdx.get('change_pct', 0):+.2f}%")
    
    # MARKET INDICATORS
    st.markdown("### 📊 Market Indicators")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        vix = prices.get('vix', {})
        st.metric("VIX", f"{vix.get('price', 0):.1f}", f"{vix.get('change_pct', 0):+.1f}%", delta_color="inverse")
    with c2:
        spy = prices.get('sp500', {})
        st.metric("SPY", f"${spy.get('price', 0):.2f}", f"{spy.get('change_pct', 0):+.1f}%")
    with c3:
        kre = prices.get('regional_banks', {})
        st.metric("KRE", f"${kre.get('price', 0):.2f}", f"{kre.get('week_change', 0):+.1f}%wk")
    with c4:
        hyg = prices.get('high_yield', {})
        st.metric("HYG", f"${hyg.get('price', 0):.2f}", f"{hyg.get('week_change', 0):+.1f}%wk")
    with c5:
        dxy = prices.get('dollar_index', {})
        st.metric("DXY", f"{dxy.get('price', 0):.1f}", f"{dxy.get('change_pct', 0):+.1f}%")
    with c6:
        btc = prices.get('bitcoin', {})
        st.metric("BTC", f"${btc.get('price', 0):,.0f}", f"{btc.get('change_pct', 0):+.1f}%")
    
    st.markdown("---")
    
    # SCENARIOS
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
            <div style="text-align:center;padding:12px;background:#1a1a2e;border-radius:10px;border-left:4px solid {cfg['color']};">
                <div style="color:#8888a0;font-size:10px;">{cfg['name']}</div>
                <div style="color:{cfg['color']};font-size:32px;font-weight:bold;">{prob*100:.0f}%</div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # POSITION TRACKER
    st.markdown("### 💰 Your Positions")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**SLV $145 Call (Feb 20)**")
        slv_price = prices.get('slv', {}).get('price', 72)
        if slv_price >= 145:
            call_value = (slv_price - 145) * 200 * 100
            st.success(f"ITM! Value: ${call_value:,.0f}")
        else:
            st.info(f"${145 - slv_price:.2f} to strike | Cost: $2,200")
    
    with col2:
        st.markdown("**MS $60 Put (Mar 21)**")
        ms_price = prices.get('morgan_stanley', {}).get('price', 135)
        if ms_price <= 60:
            put_value = (60 - ms_price) * 1000 * 100
            st.success(f"ITM! Value: ${put_value:,.0f}")
        else:
            st.info(f"${ms_price - 60:.2f} above strike | Cost: $1,000")
    
    st.markdown("---")
    
    # CALCULATOR
    st.markdown("### 📈 Price Impact Calculator")
    silver_target = st.slider("Silver Target Price", 80, 500, 289, 10)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ms_loss = MS_SHORT_POSITION_OZ * (silver_target - 30)
        st.metric("MS Paper Loss", f"${ms_loss/1e12:.2f}T")
    with col2:
        slv_target = silver_target * 0.897 * 1.02
        call_profit = max(0, (slv_target - 145)) * 200 * 100
        st.metric("SLV Call Value", f"${call_profit:,.0f}")
    with col3:
        ms_stock_est = max(0, 135 - (ms_loss / 1e9 / 10)) if ms_loss > 100e9 else 135
        put_profit = max(0, (60 - ms_stock_est)) * 1000 * 100
        st.metric("MS Put Value", f"${put_profit:,.0f}")
    
    # FOOTER
    st.markdown("---")
    st.caption("⚠️ Based on UNVERIFIED whistleblower info. NOT financial advice. Risk of total loss.")
    st.caption(f"fault.watch v2.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
