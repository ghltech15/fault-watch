# FAULT WATCH - Detailed Watchlist & Monitoring Specifications

## Purpose
This document provides specific tickers, data sources, API endpoints, and monitoring logic for the Fault Watch application. Use this to build automated alerts and dashboards.

---

## SECTION 1: STOCK TICKERS TO MONITOR

### 1.1 Primary Bank Targets (Precious Metals Exposure)

| Ticker | Company | Why Monitor | Derivatives Exposure (Q1 2025) |
|--------|---------|-------------|-------------------------------|
| JPM | JPMorgan Chase | Largest PM derivatives book; reportedly flipped net long | $323.5B |
| C | Citigroup | Second largest PM exposure; ongoing layoffs; rumored massive short | $142.8B |
| BAC | Bank of America | Rumored 1B oz OTC silver short | $61.7B |
| GS | Goldman Sachs | Part of Big 5 U.S. bank short group | $269M |
| MS | Morgan Stanley | Part of Big 5 U.S. bank short group | Not disclosed |
| WFC | Wells Fargo | Part of U.S. bank group unwinding shorts | Not disclosed |

### 1.2 International Banks with PM Exposure

| Ticker | Company | Why Monitor |
|--------|---------|-------------|
| HSBC | HSBC Holdings | Major LBMA participant; large PM trading desk |
| DB | Deutsche Bank | Active in COMEX deliveries; delivering physical |
| BCS | Barclays | LBMA market maker |
| UBS | UBS Group | Credit Suisse integration; PM desk exposure |
| CS | Credit Suisse (now UBS) | Legacy positions absorbed by UBS |
| BMO | Bank of Montreal | Canadian bank with PM trading activity |
| BNPQY | BNP Paribas (ADR) | European PM market maker |
| SCBFF | Standard Chartered (OTC) | LBMA participant |

### 1.3 Regional Banks (Contagion/Counterparty Risk)

| Ticker | Company | Why Monitor |
|--------|---------|-------------|
| USB | U.S. Bancorp | Large regional; derivatives counterparty |
| PNC | PNC Financial | Regional bank; potential contagion |
| TFC | Truist Financial | Regional bank; potential contagion |
| FITB | Fifth Third Bancorp | Regional bank exposure |
| KEY | KeyCorp | Regional bank exposure |
| CFG | Citizens Financial | Regional bank exposure |
| SCHW | Charles Schwab | Brokerage with bank charter; client PM holdings |

### 1.4 Financial Sector ETFs

| Ticker | Description | Use Case |
|--------|-------------|----------|
| XLF | Financial Select Sector SPDR | Broad financial sector exposure |
| KBE | SPDR S&P Bank ETF | Pure bank exposure |
| KRE | SPDR S&P Regional Banking ETF | Regional bank stress indicator |
| IYF | iShares U.S. Financials ETF | Alternative broad financials |
| FAZ | Direxion Daily Financial Bear 3X | Leveraged short financials |
| SKF | ProShares UltraShort Financials | 2X inverse financials |

---

## SECTION 2: SILVER & PRECIOUS METALS TICKERS

### 2.1 Silver Price Exposure

| Ticker | Description | Use Case |
|--------|-------------|----------|
| SLV | iShares Silver Trust | Paper silver; watch for NAV discount |
| PSLV | Sprott Physical Silver Trust | Physical silver; usually trades at premium |
| SIVR | abrdn Physical Silver Shares ETF | Physical silver alternative |
| AGQ | ProShares Ultra Silver | 2X leveraged silver |
| ZSL | ProShares UltraShort Silver | 2X inverse silver |

### 2.2 Silver Miners & Streamers

| Ticker | Company | Type | Notes |
|--------|---------|------|-------|
| WPM | Wheaton Precious Metals | Streamer | Largest PM streaming company |
| AG | First Majestic Silver | Miner | Pure-play silver miner |
| PAAS | Pan American Silver | Miner | Large silver producer |
| HL | Hecla Mining | Miner | U.S. silver producer |
| CDE | Coeur Mining | Miner | Silver/gold producer |
| MAG | MAG Silver | Miner | High-grade silver developer |
| EXK | Endeavour Silver | Miner | Mid-tier silver producer |
| SILJ | ETFMG Prime Junior Silver Miners | ETF | Junior miners exposure |
| SIL | Global X Silver Miners ETF | ETF | Senior miners exposure |

### 2.3 Gold (Correlated Indicator)

| Ticker | Description | Use Case |
|--------|-------------|----------|
| GLD | SPDR Gold Trust | Paper gold benchmark |
| IAU | iShares Gold Trust | Alternative paper gold |
| PHYS | Sprott Physical Gold Trust | Physical gold |
| GDX | VanEck Gold Miners ETF | Senior gold miners |
| GDXJ | VanEck Junior Gold Miners ETF | Junior gold miners |
| NEM | Newmont Corporation | Largest gold miner |
| GOLD | Barrick Gold | Major gold miner |

---

## SECTION 3: INDUSTRIAL SILVER USERS (CASCADE EFFECTS)

### 3.1 Solar Industry

| Ticker | Company | Silver Use | Why Monitor |
|--------|---------|------------|-------------|
| FSLR | First Solar | Thin-film (less silver) | Competitor advantage if silver spikes |
| ENPH | Enphase Energy | Microinverters | Supply chain exposure |
| SEDG | SolarEdge Technologies | Inverters | Supply chain exposure |
| RUN | Sunrun | Residential solar | Installation cost sensitivity |
| NOVA | Sunnova Energy | Residential solar | Installation cost sensitivity |
| JKS | JinkoSolar | Panel manufacturer | Heavy silver user |
| CSIQ | Canadian Solar | Panel manufacturer | Heavy silver user |
| TAN | Invesco Solar ETF | Solar sector ETF | Sector-wide impact |

### 3.2 Electronics & Semiconductors

| Ticker | Company | Why Monitor |
|--------|---------|-------------|
| AAPL | Apple | Consumer electronics; silver in components |
| INTC | Intel | Semiconductor manufacturing |
| TSM | TSMC | Chip fabrication |
| NVDA | NVIDIA | Chip manufacturing |
| AMD | AMD | Chip manufacturing |
| SMH | VanEck Semiconductor ETF | Sector ETF |

### 3.3 Electric Vehicles

| Ticker | Company | Why Monitor |
|--------|---------|-------------|
| TSLA | Tesla | EV manufacturing; silver in electronics |
| RIVN | Rivian | EV manufacturing |
| LCID | Lucid Motors | EV manufacturing |
| F | Ford | EV production ramp |
| GM | General Motors | EV production ramp |
| NIO | NIO Inc | Chinese EV; supply chain |

---

## SECTION 4: DATA SOURCES & API ENDPOINTS

### 4.1 CFTC Data (Official Government)

**Commitment of Traders (COT) Reports**
- URL: https://www.cftc.gov/dea/futures/other_lf.htm
- Frequency: Weekly (Tuesday data, released Friday 3:30 PM ET)
- Format: Text files, Excel
- Key fields: Commercial long/short, Non-commercial long/short, Open Interest
- Silver contract code: 084691 (COMEX Silver)

**Bank Participation Reports**
- URL: https://www.cftc.gov/MarketReports/BankParticipationReports/index.htm
- Frequency: Monthly (first Friday after first Tuesday)
- Format: HTML tables
- Key data: U.S. banks long/short, Non-U.S. banks long/short by contract

### 4.2 CME Group Data

**COMEX Silver Inventory**
- URL: https://www.cmegroup.com/delivery_reports/Silver_stocks.xls
- Frequency: Daily
- Key fields: Registered, Eligible, Total by depository
- Alert threshold: Registered < 100M oz

**Silver Futures Volume & Open Interest**
- URL: https://www.cmegroup.com/markets/metals/precious/silver.volume.html
- Frequency: Daily
- Key fields: Volume, Open Interest by contract month

**Margin Requirements**
- URL: https://www.cmegroup.com/clearing/margins/outright-vol-scans.html
- Monitor for: Sudden increases (margin hikes signal stress)

### 4.3 Federal Reserve Data

**Repo Operations**
- URL: https://www.newyorkfed.org/markets/desk-operations/repo
- Frequency: Daily
- Key fields: Overnight repo, Term repo amounts
- Alert threshold: Unusual spikes (>$50B overnight)

**H.4.1 Statistical Release**
- URL: https://www.federalreserve.gov/releases/h41/
- Frequency: Weekly (Thursday 4:30 PM ET)
- Key fields: Discount window borrowing, Emergency facilities

**Standing Repo Facility**
- URL: https://www.newyorkfed.org/markets/standing-repo-facility
- Monitor for: Usage spikes indicating bank liquidity stress

### 4.4 OCC Derivatives Data

**Quarterly Report on Bank Trading and Derivatives Activities**
- URL: https://www.occ.gov/publications-and-resources/publications/quarterly-report-on-bank-trading-and-derivatives-activities/index-quarterly-report-on-bank-trading-and-derivatives-activities.html
- Frequency: Quarterly
- Key tables: Table 9 (Precious Metals Derivatives by Bank)
- Key banks: JPM, C, BAC, GS

### 4.5 SEC Filings

**Form 4 (Insider Transactions)**
- URL: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=only&count=40
- Frequency: Real-time (filed within 2 business days of transaction)
- Filter by: Bank tickers (JPM, C, BAC, GS, etc.)
- Alert: Cluster selling by multiple executives

**13F Holdings**
- URL: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F
- Frequency: Quarterly (45 days after quarter end)
- Use: Track institutional PM ETF holdings

### 4.6 Price Data APIs

**Silver Spot Price**
```
# Free APIs
Metals-API: https://metals-api.com/
Gold-API: https://www.goldapi.io/
Kitco (scrape): https://www.kitco.com/charts/livesilver.html

# Key data points
- COMEX spot (XAG/USD)
- Shanghai spot (converted from CNY)
- London fix (AM/PM)
```

**Shanghai Gold Exchange**
- URL: https://www.sge.com.cn/sjzx/mrhq (Chinese)
- Key: Silver T+D contract price
- Calculate: Premium = (SGE price / COMEX price - 1) * 100

### 4.7 CDS Spreads

**Bank CDS Data Sources**
```
# Bloomberg Terminal (if available)
CDSW <GO> for CDS pricing

# Free alternatives
- IHS Markit (delayed): https://ihsmarkit.com/products/cds-pricing-data.html
- DTCC Trade Repository: https://www.dtcc.com/repository-otc-data

# Key tickers (5Y Senior CDS)
JPM 5Y CDS
C 5Y CDS  
BAC 5Y CDS
GS 5Y CDS

# Alert threshold: >50 bps widening in one week
```

---

## SECTION 5: MONITORING LOGIC & ALERT CONDITIONS

### 5.1 Daily Automated Checks

```python
# Pseudocode for daily monitoring

# 1. COMEX Inventory Check
comex_registered = fetch_cme_silver_stocks()
if comex_registered < 100_000_000:  # 100M oz
    alert("CRITICAL: COMEX registered silver below 100M oz")
if comex_registered_change_1d < -5_000_000:  # 5M oz daily drain
    alert("WARNING: Large COMEX inventory drain")

# 2. Shanghai Premium Check
shanghai_price = fetch_sge_silver_price()
comex_price = fetch_comex_spot()
premium_pct = (shanghai_price / comex_price - 1) * 100
if premium_pct > 10:
    alert("WARNING: Shanghai premium exceeds 10%")
if premium_pct > 15:
    alert("CRITICAL: Shanghai premium exceeds 15% - market stress")

# 3. Bank Stock vs XLF Divergence
for bank in ['JPM', 'C', 'BAC', 'GS']:
    bank_return_5d = get_return(bank, days=5)
    xlf_return_5d = get_return('XLF', days=5)
    if bank_return_5d < xlf_return_5d - 5:  # 5% underperformance
        alert(f"WARNING: {bank} underperforming XLF by >5%")

# 4. Silver Futures Curve (Backwardation Check)
front_month = get_futures_price('SIH26')  # March 2026
second_month = get_futures_price('SIK26')  # May 2026
if front_month > second_month:
    alert("WARNING: Silver in backwardation - physical shortage signal")

# 5. SLV NAV Discount
slv_price = get_price('SLV')
slv_nav = get_nav('SLV')
discount = (slv_price / slv_nav - 1) * 100
if discount < -2:
    alert("WARNING: SLV trading at >2% discount to NAV")
```

### 5.2 Weekly Checks (Friday after COT release)

```python
# 1. COT Positioning Changes
cot_data = fetch_cot_report('silver')
commercial_net = cot_data['commercial_long'] - cot_data['commercial_short']
commercial_net_change = commercial_net - previous_week_commercial_net

if commercial_net_change > 10000:  # 10K contracts = 50M oz
    alert("SIGNAL: Commercials covering shorts aggressively")

# 2. Open Interest Changes
oi_change_pct = (cot_data['open_interest'] / previous_oi - 1) * 100
if oi_change_pct < -10:
    alert("WARNING: Open interest down >10% - deleveraging")

# 3. Managed Money Positioning
mm_net = cot_data['managed_money_long'] - cot_data['managed_money_short']
if mm_net < 0:
    alert("SIGNAL: Managed money net short - contrarian bullish")
```

### 5.3 Monthly Checks (After Bank Participation Report)

```python
# 1. U.S. Bank Net Position
bpr_data = fetch_bank_participation_report('silver')
us_bank_net = bpr_data['us_long'] - bpr_data['us_short']
non_us_bank_net = bpr_data['non_us_long'] - bpr_data['non_us_short']

if us_bank_net > 0:
    alert("MAJOR: U.S. banks now NET LONG silver")
    
# 2. Non-U.S. Bank Exposure
non_us_short_oz = bpr_data['non_us_short'] * 5000  # contracts to oz
if non_us_short_oz > 200_000_000:  # 200M oz
    alert("WARNING: Non-U.S. banks short >200M oz")
```

### 5.4 Event-Driven Alerts

```python
# 1. CME Margin Hike Detection
current_margin = fetch_cme_margin('silver')
if current_margin > previous_margin * 1.10:  # >10% increase
    alert("CRITICAL: CME raised silver margins - expect volatility")
    alert("STRATEGY: Wait for dip, then buy calls")

# 2. Insider Selling Cluster
form4_filings = fetch_sec_form4(['JPM', 'C', 'BAC', 'GS'])
sales_last_week = sum(f['shares_sold'] for f in form4_filings if f['transaction_type'] == 'S')
if len([f for f in form4_filings if f['transaction_type'] == 'S']) >= 3:
    alert("WARNING: Multiple bank insiders selling")

# 3. Layoff Announcements
# Monitor news feeds for keywords
keywords = ['layoff', 'job cuts', 'workforce reduction', 'restructuring']
banks = ['JPMorgan', 'Citigroup', 'Bank of America', 'Goldman', 'Morgan Stanley']
# Trigger alert if bank + layoff keyword detected

# 4. Fed Emergency Actions
fed_actions = monitor_fed_announcements()
if 'emergency' in fed_actions or 'facility' in fed_actions:
    alert("CRITICAL: Fed emergency action detected")
```

---

## SECTION 6: POSITIONING MATRIX

### 6.1 Signal-to-Action Mapping

| Signal Combination | Confidence | Action | Tickers |
|-------------------|------------|--------|---------|
| Shanghai premium >10% + COMEX drain | HIGH | Long silver miners | WPM, AG, PSLV |
| Bank CDS widening + insider selling | HIGH | Bank puts | C, BAC puts |
| Margin hike + backwardation | MEDIUM | Wait for dip, long silver | SLV calls, AG calls |
| Layoff cluster + repo spike | MEDIUM | Short financials | XLF puts, FAZ |
| U.S. banks flip net long | HIGH | Long silver, short paper | Long PSLV, short SLV |
| SLV NAV discount >3% | HIGH | Arbitrage | Short SLV, long PSLV |
| COT commercials covering rapidly | MEDIUM | Long silver | SLV calls, miners |

### 6.2 Position Sizing Guidelines

```
Conservative (25% of allocation):
- Signal confidence: MEDIUM
- Use: Single confirmation signal
- Position: 2-5% of portfolio per trade

Moderate (50% of allocation):
- Signal confidence: HIGH
- Use: Two confirming signals
- Position: 5-10% of portfolio per trade

Aggressive (25% of allocation):
- Signal confidence: CRITICAL
- Use: Three+ confirming signals
- Position: 10-20% of portfolio per trade
```

### 6.3 Options Strategy Specifications

**Bank Puts (Bearish Bank Thesis)**
```
Ticker: C, BAC
Strike: 10-15% OTM
Expiration: 60-90 DTE
Entry trigger: CDS widening + insider selling
Target: 100-200% gain
Stop: 50% loss
```

**Silver Calls (Bullish Silver Thesis)**
```
Ticker: SLV, AG, WPM
Strike: ATM or slightly ITM
Expiration: 90-120 DTE
Entry trigger: Shanghai premium blowout + backwardation
Target: 200-500% gain
Stop: 50% loss
```

**XLF Puts (Systemic Risk Play)**
```
Ticker: XLF
Strike: 10-20% OTM
Expiration: 90-180 DTE (allow time for cascade)
Entry trigger: Multiple bank stress signals
Target: 300%+ gain
Stop: 50% loss
```

---

## SECTION 7: QUICK REFERENCE DASHBOARD LAYOUT

### 7.1 Suggested Dashboard Panels

```
┌─────────────────────────────────────────────────────────────────┐
│ PANEL 1: SILVER MARKET                                          │
│ ┌─────────────┬─────────────┬─────────────┬─────────────┐      │
│ │ COMEX Spot  │ Shanghai    │ Premium %   │ Curve       │      │
│ │ $XX.XX      │ $XX.XX      │ +X.X%       │ Contango/   │      │
│ │             │             │             │ Backwrdtn   │      │
│ └─────────────┴─────────────┴─────────────┴─────────────┘      │
├─────────────────────────────────────────────────────────────────┤
│ PANEL 2: COMEX INVENTORY                                        │
│ ┌─────────────────────┬─────────────────────┐                  │
│ │ Registered: XXX M oz│ Eligible: XXX M oz  │                  │
│ │ [====----] 30%      │ [========] 70%      │                  │
│ │ 24h change: -X.X M  │ 24h change: +X.X M  │                  │
│ └─────────────────────┴─────────────────────┘                  │
├─────────────────────────────────────────────────────────────────┤
│ PANEL 3: BANK STRESS INDICATORS                                 │
│ ┌──────┬────────┬────────┬────────┬────────┐                   │
│ │ Bank │ Price  │ vs XLF │ CDS 5Y │ Alert  │                   │
│ ├──────┼────────┼────────┼────────┼────────┤                   │
│ │ JPM  │ $XXX   │ +X.X%  │ XX bps │ ○      │                   │
│ │ C    │ $XX    │ -X.X%  │ XX bps │ ●      │                   │
│ │ BAC  │ $XX    │ -X.X%  │ XX bps │ ●      │                   │
│ │ GS   │ $XXX   │ +X.X%  │ XX bps │ ○      │                   │
│ └──────┴────────┴────────┴────────┴────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│ PANEL 4: FED LIQUIDITY                                          │
│ ┌─────────────────────┬─────────────────────┐                  │
│ │ Overnight Repo      │ Term Repo           │                  │
│ │ $XX.X B             │ $XX.X B             │                  │
│ │ [Normal/Elevated]   │ [Normal/Elevated]   │                  │
│ └─────────────────────┴─────────────────────┘                  │
├─────────────────────────────────────────────────────────────────┤
│ PANEL 5: ACTIVE ALERTS                                          │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ 🔴 CRITICAL: Shanghai premium at 12% (threshold: 10%)       ││
│ │ 🟡 WARNING: COMEX registered down 3M oz today               ││
│ │ 🟢 INFO: COT report due Friday 3:30 PM ET                   ││
│ └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## SECTION 8: IMPLEMENTATION NOTES FOR LOCAL CLAUDE

### 8.1 Data Fetch Priority

1. **Real-time (every 5 min during market hours)**
   - Silver spot prices (COMEX, Shanghai)
   - Bank stock prices
   - XLF price

2. **Hourly**
   - COMEX inventory (when updated)
   - Fed repo operations

3. **Daily (after market close)**
   - Full inventory reconciliation
   - Bank price vs sector analysis
   - Futures curve analysis

4. **Weekly (Friday evening)**
   - COT report parsing
   - Position change analysis

5. **Monthly (first Friday)**
   - Bank Participation Report
   - OCC derivatives (when available)

### 8.2 Alert Priority Levels

```
CRITICAL (immediate notification):
- Shanghai premium >15%
- COMEX registered <75M oz
- CME margin hike
- Fed emergency facility activation
- Bank stock drops >10% in day

WARNING (daily digest):
- Shanghai premium 10-15%
- COMEX inventory declining >5M oz/day
- Bank underperforming XLF by >5%
- CDS widening >25 bps/week

INFO (weekly summary):
- COT positioning changes
- Bank Participation Report updates
- Insider transaction summaries
```

### 8.3 Database Schema Suggestion

```sql
-- Core price data
CREATE TABLE silver_prices (
    timestamp DATETIME PRIMARY KEY,
    comex_spot DECIMAL(10,4),
    shanghai_spot DECIMAL(10,4),
    premium_pct DECIMAL(5,2),
    front_month_futures DECIMAL(10,4),
    second_month_futures DECIMAL(10,4)
);

-- COMEX inventory
CREATE TABLE comex_inventory (
    date DATE PRIMARY KEY,
    registered_oz BIGINT,
    eligible_oz BIGINT,
    total_oz BIGINT
);

-- Bank metrics
CREATE TABLE bank_metrics (
    date DATE,
    ticker VARCHAR(10),
    close_price DECIMAL(10,2),
    vs_xlf_pct DECIMAL(5,2),
    cds_5y_bps DECIMAL(7,2),
    PRIMARY KEY (date, ticker)
);

-- COT data
CREATE TABLE cot_silver (
    report_date DATE PRIMARY KEY,
    commercial_long INT,
    commercial_short INT,
    managed_money_long INT,
    managed_money_short INT,
    open_interest INT
);

-- Alerts
CREATE TABLE alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME,
    level ENUM('CRITICAL', 'WARNING', 'INFO'),
    category VARCHAR(50),
    message TEXT,
    acknowledged BOOLEAN DEFAULT FALSE
);
```

---

## SECTION 9: IMPORTANT CAVEATS

1. **Unverified Claims**: The specific short position sizes attributed to individual banks (e.g., "BofA 1B oz short", "Citi 3.4B oz short") are social media speculation. CFTC reports only provide aggregate data, not bank-specific positions.

2. **OTC Opacity**: Over-the-counter derivatives positions are not publicly reported. The OCC quarterly report shows notional values but not directional exposure.

3. **Hedging vs Speculation**: Large short positions often represent hedging activity (offsetting client longs) rather than directional bets.

4. **Data Delays**: CFTC data is delayed by several days. Real-time positioning is unknowable.

5. **Regime Changes**: Past patterns may not predict future behavior. Banks may have changed their PM trading strategies significantly.

---

*Document Version: 1.0*
*Created: January 14, 2026*
*For use with Fault Watch Application*
