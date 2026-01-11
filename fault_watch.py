"""
FAULT.WATCH - Adaptive Systemic Risk Monitoring System
======================================================
Real-time indicator monitoring with dynamic scenario probabilities.

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

# Page config
st.set_page_config(page_title="fault.watch", page_icon="⚠️", layout="wide")

# Custom CSS
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
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA FETCHING - FIXED VERSION
# =============================================================================

@st.cache_data(ttl=60)
def fetch_prices():
    """Fetch real-time prices from multiple sources"""
    prices = {}
    
    # --- YAHOO FINANCE: ETFs and Indices ---
    yf_tickers = {
        'SPY': 'sp500',
        '^VIX': 'vix',
        'TLT': 'long_treasury',
        'KRE': 'regional_banks',
        'HYG': 'high_yield',
        'DX-Y.NYB': 'dollar_index',
        'XLE': 'energy',
        'GDX': 'gold_miners',
        'SILJ': 'silver_miners',
        'GC=F': 'gold_futures',      # Gold futures (actual gold price)
        'SI=F': 'silver_futures',    # Silver futures (actual silver price)
        '^TNX': 'treasury_10y',      # 10-year Treasury yield
    }
    
    try:
        for ticker, name in yf_tickers.items():
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period='5d')
                if not hist.empty and len(hist) >= 1:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    first = hist['Close'].iloc[0] if len(hist) > 0 else current
                    
                    prices[name] = {
                        'price': current,
                        'prev_close': prev,
                        'change_pct': ((current / prev) - 1) * 100 if prev != 0 else 0,
                        'week_change': ((current / first) - 1) * 100 if first != 0 else 0,
                    }
            except Exception as e:
                continue
    except Exception as e:
        st.warning(f"Yahoo Finance error: {e}")
    
    # --- Extract Gold and Silver from futures ---
    if 'gold_futures' in prices:
        prices['gold'] = prices['gold_futures'].copy()
    else:
        # Fallback estimate
        prices['gold'] = {'price': 4520, 'change_pct': 0, 'week_change': 0}
    
    if 'silver_futures' in prices:
        prices['silver'] = prices['silver_futures'].copy()
    else:
        # Fallback estimate
        prices['silver'] = {'price': 80, 'change_pct': 0, 'week_change': 0}
    
    # --- COINGECKO: Crypto ---
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
    
    # --- Calculate Gold/Silver Ratio ---
    if 'gold' in prices and 'silver' in prices:
        gold_price = prices['gold']['price']
        silver_price = prices['silver']['price']
        if silver_price > 0:
            prices['gold_silver_ratio'] = {'price': gold_price / silver_price, 'change_pct': 0}
    
    return prices

# =============================================================================
# THRESHOLDS
# =============================================================================

THRESHOLDS = {
    'vix': {'warning': 25, 'critical': 35},
    'silver': {'warning': 90, 'critical': 100},
    'gold': {'warning': 4700, 'critical': 5000},
    'kre_weekly': {'warning': -5, 'critical': -10},
    'hyg_weekly': {'warning': -3, 'critical': -5},
    'dollar_index': {'warning': 100, 'critical': 95},
    'gold_silver_ratio': {'warning': 50, 'critical': 40},
    'bitcoin': {'buy_zone': 80000, 'strong_buy': 60000},
}

# =============================================================================
# SCENARIO ENGINE
# =============================================================================

def calculate_scenarios(indicators):
    """Calculate scenario probabilities based on current indicators"""
    probs = {
        'slow_burn': 0.35,
        'credit_crunch': 0.25,
        'inflation_spike': 0.15,
        'deflation_bust': 0.15,
        'monetary_reset': 0.10
    }
    
    # VIX adjustments
    vix = indicators.get('vix', 15)
    if vix > 35:
        probs['credit_crunch'] += 0.15
        probs['deflation_bust'] += 0.10
        probs['slow_burn'] -= 0.20
    elif vix > 25:
        probs['credit_crunch'] += 0.08
        probs['slow_burn'] -= 0.08
    
    # Silver adjustments
    silver = indicators.get('silver', 80)
    if silver > 100:
        probs['monetary_reset'] += 0.15
        probs['inflation_spike'] += 0.05
        probs['slow_burn'] -= 0.15
    elif silver > 90:
        probs['monetary_reset'] += 0.05
        probs['inflation_spike'] += 0.03
    
    # Gold adjustments
    gold = indicators.get('gold', 4500)
    if gold > 5000:
        probs['monetary_reset'] += 0.10
        probs['inflation_spike'] += 0.05
    elif gold > 4700:
        probs['monetary_reset'] += 0.05
    
    # Bank stress (KRE weekly change)
    kre = indicators.get('kre_weekly', 0)
    if kre < -10:
        probs['credit_crunch'] += 0.20
        probs['deflation_bust'] += 0.10
        probs['slow_burn'] -= 0.25
    elif kre < -5:
        probs['credit_crunch'] += 0.10
        probs['slow_burn'] -= 0.10
    
    # Credit stress (HYG weekly change)
    hyg = indicators.get('hyg_weekly', 0)
    if hyg < -5:
        probs['credit_crunch'] += 0.15
        probs['deflation_bust'] += 0.10
        probs['slow_burn'] -= 0.20
    elif hyg < -3:
        probs['credit_crunch'] += 0.08
    
    # Dollar weakness
    dxy = indicators.get('dollar_index', 102)
    if dxy < 95:
        probs['monetary_reset'] += 0.15
        probs['inflation_spike'] += 0.05
        probs['slow_burn'] -= 0.15
    elif dxy < 100:
        probs['monetary_reset'] += 0.05
    
    # Gold/Silver ratio (low = silver outperforming = monetary stress)
    gs_ratio = indicators.get('gold_silver_ratio', 56)
    if gs_ratio < 40:
        probs['monetary_reset'] += 0.10
    elif gs_ratio < 50:
        probs['monetary_reset'] += 0.05
    
    # Ensure no negative probabilities
    probs = {k: max(0, v) for k, v in probs.items()}
    
    # Normalize to sum to 1.0
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
            'Quality Stocks': 0.00, 'Cash': 0.10, 'Bitcoin': 0.05, 'Bank Shorts (KRE puts)': 0.10
        },
        'inflation_spike': {
            'Physical Gold': 0.10, 'Physical Silver': 0.15, 'Gold Miners (GDX)': 0.10,
            'Silver Miners (SILJ)': 0.10, 'Long Treasuries (TLT)': 0.00, 'Energy (XLE)': 0.20,
            'Quality Stocks': 0.05, 'Cash': 0.05, 'Bitcoin': 0.10, 'TIPS': 0.15
        },
        'deflation_bust': {
            'Physical Gold': 0.20, 'Physical Silver': 0.05, 'Gold Miners (GDX)': 0.05,
            'Silver Miners (SILJ)': 0.00, 'Long Treasuries (TLT)': 0.30, 'Energy (XLE)': 0.00,
            'Quality Stocks': 0.00, 'Cash': 0.35, 'Bitcoin': 0.00, 'Bank Shorts (KRE puts)': 0.05
        },
        'monetary_reset': {
            'Physical Gold': 0.25, 'Physical Silver': 0.20, 'Gold Miners (GDX)': 0.15,
            'Silver Miners (SILJ)': 0.20, 'Long Treasuries (TLT)': 0.00, 'Energy (XLE)': 0.05,
            'Quality Stocks': 0.00, 'Cash': 0.00, 'Bitcoin': 0.15
        },
    }
    
    # Get all unique assets
    all_assets = set()
    for a in allocs.values():
        all_assets.update(a.keys())
    
    # Calculate weighted allocation
    target = {}
    for asset in all_assets:
        target[asset] = sum(probs.get(s, 0) * allocs.get(s, {}).get(asset, 0) for s in probs)
    
    # Filter out small allocations and sort by weight
    return {k: v for k, v in sorted(target.items(), key=lambda x: -x[1]) if v > 0.02}

def generate_alerts(indicators):
    """Generate alerts based on current indicators"""
    alerts = []
    
    # VIX alerts
    vix = indicators.get('vix', 15)
    if vix > THRESHOLDS['vix']['critical']:
        alerts.append({
            'level': 'critical',
            'title': '🔴 EXTREME VOLATILITY',
            'msg': f'VIX at {vix:.1f} - Risk-off event in progress. Review all positions immediately.',
            'action': 'Activate hedges, halt new equity purchases'
        })
    elif vix > THRESHOLDS['vix']['warning']:
        alerts.append({
            'level': 'warning',
            'title': '🟠 Elevated Volatility',
            'msg': f'VIX at {vix:.1f} - Market stress elevated.',
            'action': 'Prepare hedges, monitor closely'
        })
    
    # Silver alerts
    silver = indicators.get('silver', 80)
    if silver > THRESHOLDS['silver']['critical']:
        alerts.append({
            'level': 'critical',
            'title': '🔴 SILVER BREAKOUT - $100+',
            'msg': f'Silver at ${silver:.2f} - Squeeze accelerating!',
            'action': 'HOLD physical, trail stops on paper'
        })
    elif silver > THRESHOLDS['silver']['warning']:
        alerts.append({
            'level': 'warning',
            'title': '🟠 Silver Approaching Critical',
            'msg': f'Silver at ${silver:.2f} - Nearing breakout zone.',
            'action': 'Review miner positions, prepare for volatility'
        })
    
    # Gold alerts
    gold = indicators.get('gold', 4500)
    if gold > THRESHOLDS['gold']['critical']:
        alerts.append({
            'level': 'critical',
            'title': '🔴 GOLD BREAKOUT - $5000+',
            'msg': f'Gold at ${gold:,.0f} - Major technical breakout!',
            'action': 'Hold positions, consider adding on pullbacks'
        })
    elif gold > THRESHOLDS['gold']['warning']:
        alerts.append({
            'level': 'warning',
            'title': '🟠 Gold Elevated',
            'msg': f'Gold at ${gold:,.0f} - Approaching $5,000.',
            'action': 'Trail stops, hold core position'
        })
    
    # Bank stress alerts
    kre = indicators.get('kre_weekly', 0)
    if kre < THRESHOLDS['kre_weekly']['critical']:
        alerts.append({
            'level': 'critical',
            'title': '🔴 BANK CRISIS SIGNAL',
            'msg': f'Regional banks (KRE) down {kre:.1f}% this week!',
            'action': 'Execute bank crisis playbook - activate shorts'
        })
    elif kre < THRESHOLDS['kre_weekly']['warning']:
        alerts.append({
            'level': 'warning',
            'title': '🟠 Bank Stress',
            'msg': f'Regional banks (KRE) down {kre:.1f}% this week.',
            'action': 'Prepare short positions (KRE puts)'
        })
    
    # Credit stress alerts
    hyg = indicators.get('hyg_weekly', 0)
    if hyg < THRESHOLDS['hyg_weekly']['critical']:
        alerts.append({
            'level': 'critical',
            'title': '🔴 CREDIT STRESS',
            'msg': f'High yield bonds (HYG) down {hyg:.1f}% this week!',
            'action': 'Reduce credit exposure immediately'
        })
    
    # Dollar alerts
    dxy = indicators.get('dollar_index', 102)
    if dxy < THRESHOLDS['dollar_index']['critical']:
        alerts.append({
            'level': 'critical',
            'title': '🔴 DOLLAR CRISIS',
            'msg': f'Dollar index at {dxy:.1f} - Below critical support!',
            'action': 'Maximum precious metals allocation'
        })
    elif dxy < THRESHOLDS['dollar_index']['warning']:
        alerts.append({
            'level': 'warning',
            'title': '🟠 Dollar Weakness',
            'msg': f'Dollar index at {dxy:.1f} - Breaking down.',
            'action': 'Increase PM allocation'
        })
    
    # Bitcoin opportunity
    btc = indicators.get('bitcoin', 91000)
    if btc < THRESHOLDS['bitcoin']['strong_buy']:
        alerts.append({
            'level': 'info',
            'title': '🟢 BITCOIN ACCUMULATION ZONE',
            'msg': f'Bitcoin at ${btc:,.0f} - Strong buy zone!',
            'action': 'Scale in aggressively'
        })
    elif btc < THRESHOLDS['bitcoin']['buy_zone']:
        alerts.append({
            'level': 'info',
            'title': '🟢 Bitcoin Buy Zone',
            'msg': f'Bitcoin at ${btc:,.0f} - Accumulation opportunity.',
            'action': 'Consider adding to position'
        })
    
    # Gold/Silver ratio
    gs_ratio = indicators.get('gold_silver_ratio', 56)
    if gs_ratio < THRESHOLDS['gold_silver_ratio']['critical']:
        alerts.append({
            'level': 'warning',
            'title': '🟠 Silver Outperforming',
            'msg': f'Gold/Silver ratio at {gs_ratio:.1f} - Silver leading.',
            'action': 'Monetary stress signal - favor silver'
        })
    
    return alerts

# =============================================================================
# MAIN DASHBOARD
# =============================================================================

def main():
    # --- Sidebar ---
    st.sidebar.title("⚠️ fault.watch")
    st.sidebar.caption("Adaptive Systemic Risk Intelligence")
    st.sidebar.markdown("---")
    
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", False)
    if auto_refresh:
        time.sleep(60)
        st.rerun()
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Risk profile selector
    st.sidebar.markdown("---")
    risk_profile = st.sidebar.selectbox(
        "Risk Profile",
        ["Moderate", "Conservative", "Aggressive"],
        index=0
    )
    
    # --- Fetch Data ---
    with st.spinner("Fetching market data..."):
        prices = fetch_prices()
    
    # --- Build Indicators Dict ---
    indicators = {
        'vix': prices.get('vix', {}).get('price', 15),
        'gold': prices.get('gold', {}).get('price', 4520),
        'silver': prices.get('silver', {}).get('price', 80),
        'kre_weekly': prices.get('regional_banks', {}).get('week_change', 0),
        'hyg_weekly': prices.get('high_yield', {}).get('week_change', 0),
        'dollar_index': prices.get('dollar_index', {}).get('price', 102),
        'bitcoin': prices.get('bitcoin', {}).get('price', 91000),
        'gold_silver_ratio': prices.get('gold_silver_ratio', {}).get('price', 56),
        'treasury_10y': prices.get('treasury_10y', {}).get('price', 4.5),
    }
    
    # --- Calculate Scenarios ---
    scenarios = calculate_scenarios(indicators)
    allocation = calculate_allocation(scenarios)
    alerts = generate_alerts(indicators)
    
    # --- Calculate Risk Index ---
    risk_index = sum(scenarios.get(s, 0) * w for s, w in [
        ('slow_burn', 5),
        ('credit_crunch', 9),
        ('inflation_spike', 7),
        ('deflation_bust', 9),
        ('monetary_reset', 10)
    ])
    
    # ==========================================================================
    # HEADER
    # ==========================================================================
    risk_color = '#ff3b5c' if risk_index >= 7 else '#ff8c42' if risk_index >= 5 else '#4ade80'
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("⚠️ fault.watch")
        st.caption("Adaptive Systemic Risk Intelligence")
    with col2:
        st.markdown(f"""
        <div style="text-align:center;padding:15px;background:#1a1a2e;border-radius:10px;">
            <div style="color:#8888a0;font-size:12px;">SYSTEMIC RISK INDEX</div>
            <div style="color:{risk_color};font-size:42px;font-weight:bold;">{risk_index:.1f}</div>
            <div style="color:#8888a0;font-size:10px;">/ 10</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        n_crit = len([a for a in alerts if a['level'] == 'critical'])
        n_warn = len([a for a in alerts if a['level'] == 'warning'])
        st.markdown(f"""
        <div style="text-align:center;padding:15px;background:#1a1a2e;border-radius:10px;">
            <div style="color:#8888a0;font-size:12px;">ACTIVE ALERTS</div>
            <div style="font-size:28px;">
                <span style="color:#ff3b5c;">{n_crit} 🔴</span>
                <span style="color:#ff8c42;">{n_warn} 🟠</span>
            </div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================================================
    # ALERTS
    # ==========================================================================
    if alerts:
        st.subheader("🚨 Active Alerts")
        for a in alerts:
            css_class = f"alert-{a['level']}" if a['level'] != 'info' else 'alert-warning'
            st.markdown(f'''
            <div class="{css_class}">
                <strong>{a["title"]}</strong><br>
                {a["msg"]}<br>
                <em style="color:#aaa;">→ {a.get("action", "Monitor")}</em>
            </div>''', unsafe_allow_html=True)
        st.markdown("---")
    
    # ==========================================================================
    # SCENARIO PROBABILITIES
    # ==========================================================================
    st.subheader("📊 Scenario Probabilities")
    
    scenario_config = {
        'slow_burn': {'name': 'Slow Burn', 'color': '#4ade80', 'desc': 'Status quo continues'},
        'credit_crunch': {'name': 'Credit Crunch', 'color': '#ff3b5c', 'desc': 'Banking/CRE crisis'},
        'inflation_spike': {'name': 'Inflation Spike', 'color': '#ff8c42', 'desc': 'Inflation reaccelerates'},
        'deflation_bust': {'name': 'Deflation Bust', 'color': '#3b82f6', 'desc': 'Credit collapse'},
        'monetary_reset': {'name': 'Monetary Reset', 'color': '#a855f7', 'desc': 'Dollar crisis'},
    }
    
    cols = st.columns(5)
    for i, (key, prob) in enumerate(scenarios.items()):
        cfg = scenario_config.get(key, {'name': key, 'color': '#888', 'desc': ''})
        with cols[i]:
            st.markdown(f"""
            <div style="text-align:center;padding:12px;background:#1a1a2e;border-radius:10px;border-left:4px solid {cfg['color']};">
                <div style="color:#8888a0;font-size:10px;text-transform:uppercase;">{cfg['name']}</div>
                <div style="color:{cfg['color']};font-size:32px;font-weight:bold;">{prob*100:.0f}%</div>
                <div style="color:#666;font-size:9px;">{cfg['desc']}</div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================================================
    # REAL-TIME PRICES - ROW 1
    # ==========================================================================
    st.subheader("📈 Real-Time Indicators")
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        gold_p = indicators['gold']
        gold_chg = prices.get('gold', {}).get('change_pct', 0)
        st.metric("🥇 Gold", f"${gold_p:,.0f}", f"{gold_chg:+.2f}%")
    
    with c2:
        silver_p = indicators['silver']
        silver_chg = prices.get('silver', {}).get('change_pct', 0)
        st.metric("🥈 Silver", f"${silver_p:.2f}", f"{silver_chg:+.2f}%")
    
    with c3:
        gs_ratio = indicators['gold_silver_ratio']
        st.metric("⚖️ Gold/Silver", f"{gs_ratio:.1f}", "Lower = Silver leading")
    
    with c4:
        vix_p = indicators['vix']
        vix_chg = prices.get('vix', {}).get('change_pct', 0)
        st.metric("😰 VIX", f"{vix_p:.1f}", f"{vix_chg:+.1f}%", delta_color="inverse")
    
    with c5:
        btc_p = indicators['bitcoin']
        btc_chg = prices.get('bitcoin', {}).get('change_pct', 0)
        st.metric("₿ Bitcoin", f"${btc_p:,.0f}", f"{btc_chg:+.1f}%")
    
    with c6:
        dxy_p = indicators['dollar_index']
        dxy_chg = prices.get('dollar_index', {}).get('change_pct', 0)
        st.metric("💵 Dollar (DXY)", f"{dxy_p:.1f}", f"{dxy_chg:+.1f}%")
    
    # ROW 2
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        gdx = prices.get('gold_miners', {}).get('price', 0)
        gdx_chg = prices.get('gold_miners', {}).get('change_pct', 0)
        st.metric("⛏️ GDX", f"${gdx:.2f}", f"{gdx_chg:+.1f}%")
    
    with c2:
        silj = prices.get('silver_miners', {}).get('price', 0)
        silj_chg = prices.get('silver_miners', {}).get('change_pct', 0)
        st.metric("⛏️ SILJ", f"${silj:.2f}", f"{silj_chg:+.1f}%")
    
    with c3:
        kre = prices.get('regional_banks', {}).get('price', 0)
        kre_wk = indicators['kre_weekly']
        st.metric("🏦 KRE (Banks)", f"${kre:.2f}", f"{kre_wk:+.1f}% wk")
    
    with c4:
        hyg = prices.get('high_yield', {}).get('price', 0)
        hyg_wk = indicators['hyg_weekly']
        st.metric("📉 HYG (Credit)", f"${hyg:.2f}", f"{hyg_wk:+.1f}% wk")
    
    with c5:
        tlt = prices.get('long_treasury', {}).get('price', 0)
        tlt_chg = prices.get('long_treasury', {}).get('change_pct', 0)
        st.metric("📜 TLT (Bonds)", f"${tlt:.2f}", f"{tlt_chg:+.1f}%")
    
    with c6:
        spy = prices.get('sp500', {}).get('price', 0)
        spy_chg = prices.get('sp500', {}).get('change_pct', 0)
        st.metric("📊 SPY", f"${spy:.2f}", f"{spy_chg:+.1f}%")
    
    st.markdown("---")
    
    # ==========================================================================
    # TARGET ALLOCATION
    # ==========================================================================
    st.subheader("🎯 Recommended Allocation")
    st.caption(f"Based on current scenario probabilities • Risk Profile: {risk_profile}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pie chart
        fig = px.pie(
            values=list(allocation.values()),
            names=list(allocation.keys()),
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e8e8f0',
            showlegend=True,
            legend=dict(font=dict(size=11))
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Target Weights:**")
        for asset, wt in allocation.items():
            bar_color = '#3b82f6' if wt >= 0.10 else '#6b7280'
            st.markdown(f"""
            <div style="margin:8px 0;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:#e8e8f0;font-size:13px;">{asset}</span>
                    <span style="color:#8888a0;font-size:13px;">{wt*100:.1f}%</span>
                </div>
                <div style="background:#2a2a4a;height:6px;border-radius:3px;margin-top:4px;">
                    <div style="background:{bar_color};width:{wt*100}%;height:100%;border-radius:3px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================================================
    # KEY LEVELS
    # ==========================================================================
    st.subheader("🎚️ Key Threshold Levels")
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        vix_val = indicators['vix']
        vix_status = "🟢 Normal" if vix_val < 20 else "🟡 Elevated" if vix_val < 25 else "🟠 High" if vix_val < 35 else "🔴 EXTREME"
        st.markdown(f"**VIX:** {vix_val:.1f} → {vix_status}")
        st.caption(f"Warning: >{THRESHOLDS['vix']['warning']} | Critical: >{THRESHOLDS['vix']['critical']}")
    
    with c2:
        silver_val = indicators['silver']
        silver_status = "🟢 Normal" if silver_val < 85 else "🟡 Strong" if silver_val < 90 else "🟠 Breakout" if silver_val < 100 else "🔴 SQUEEZE"
        st.markdown(f"**Silver:** ${silver_val:.2f} → {silver_status}")
        st.caption(f"Warning: >${THRESHOLDS['silver']['warning']} | Critical: >${THRESHOLDS['silver']['critical']}")
    
    with c3:
        kre_val = indicators['kre_weekly']
        kre_status = "🟢 Normal" if kre_val > -3 else "🟡 Weak" if kre_val > -5 else "🟠 Stress" if kre_val > -10 else "🔴 CRISIS"
        st.markdown(f"**Banks (KRE wk):** {kre_val:.1f}% → {kre_status}")
        st.caption(f"Warning: <{THRESHOLDS['kre_weekly']['warning']}% | Critical: <{THRESHOLDS['kre_weekly']['critical']}%")
    
    with c4:
        dxy_val = indicators['dollar_index']
        dxy_status = "🟢 Strong" if dxy_val > 103 else "🟡 Normal" if dxy_val > 100 else "🟠 Weak" if dxy_val > 95 else "🔴 CRISIS"
        st.markdown(f"**Dollar (DXY):** {dxy_val:.1f} → {dxy_status}")
        st.caption(f"Warning: <{THRESHOLDS['dollar_index']['warning']} | Critical: <{THRESHOLDS['dollar_index']['critical']}")
    
    # ==========================================================================
    # FOOTER
    # ==========================================================================
    st.markdown("---")
    st.caption("""
    ⚠️ **Disclaimer:** For informational purposes only. Not financial advice.
    Data from Yahoo Finance & CoinGecko. May be delayed. Always verify before making financial decisions.
    """)
    st.caption(f"fault.watch v1.0 • Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
