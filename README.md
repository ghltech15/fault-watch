# FAULT WATCH - Crisis Monitor Module

Real-time banking system stress monitoring dashboard for tracking the silver short squeeze impact on major banks.

![Crisis Level](https://img.shields.io/badge/Status-Active-red)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)

## 🚨 Current Status

**Crisis Level: SEVERE**
- Silver at $94/oz (ATH)
- Shanghai premium >12%
- Multiple broker restrictions active
- Bank layoffs clustering

## 📊 What This Monitors

### Tier 1: Immediate Warning Signs (Daily)
| Indicator | Current | Status |
|-----------|---------|--------|
| Silver Spot Price | $94.00 | 🔴 SEVERE |
| Silver 24h Change | +7.14% | 🔴 SEVERE |
| Shanghai Premium | 12.0% | 🔴 SEVERE |
| COMEX Registered | 85M oz | 🟡 WARNING |
| Bank vs XLF | -4.2% | 🟡 ELEVATED |
| OFR Stress Index | 0.3 | 🟡 ELEVATED |
| SOFR Spread | 12 bps | 🟡 ELEVATED |

### Tier 2: Confirming Signals (Weekly)
- CDS spread changes
- Insider selling (Form 4)
- Put option volume
- COMEX daily drain rate
- Futures backwardation
- CME margin hikes
- Broker restrictions
- Layoff clustering

### Tier 3: Pre-Crisis Indicators
- Fed Discount Window usage
- Standing Repo Facility spikes
- Credit rating watches
- Dividend cuts
- Credit facility drawdowns
- Interbank lending freezes

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Clone or copy the project
cd fault-watch-monitor

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open at `http://localhost:3000`

### Build for Production

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
fault-watch-monitor/
├── src/
│   ├── components/
│   │   ├── Header.jsx           # Top navigation bar
│   │   ├── CrisisGauge.jsx      # Main crisis level gauge
│   │   ├── IndicatorCard.jsx    # Individual indicator display
│   │   ├── TierPanel.jsx        # Grouped indicators by tier
│   │   ├── BankExposurePanel.jsx # Bank loss calculations
│   │   ├── CrisisTimeline.jsx   # Stage progression tracker
│   │   └── DataSourcesPanel.jsx # Links to primary sources
│   ├── data/
│   │   └── indicators.js        # Indicator definitions & thresholds
│   ├── hooks/
│   │   └── useStore.js          # Zustand state management
│   ├── App.jsx                  # Main application
│   ├── main.jsx                 # React entry point
│   └── index.css                # Tailwind styles
├── public/
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## 🎯 Crisis Level Calculation

The overall crisis level is computed from weighted indicators:

```
Level 0: NORMAL    - Months away
Level 1: ELEVATED  - Weeks to months
Level 2: WARNING   - Days to weeks
Level 3: SEVERE    - Hours to days
Level 4: CRITICAL  - IMMINENT
```

**Weighting:**
- Tier 1 indicators: 60% of score
- Maximum severity across all: 40% of score

## 📡 Data Sources

### Real-time / Daily
- [COMEX Silver Inventory](https://www.cmegroup.com/delivery_reports/Silver_stocks.xls)
- [Shanghai Silver Benchmark](https://en.sge.com.cn/data_SilverBenchmarkPrice)
- [NY Fed Repo Operations](https://www.newyorkfed.org/markets/desk-operations/repo)
- [OFR Financial Stress Index](https://www.financialresearch.gov/financial-stress-index/)

### Weekly
- [CFTC COT Report](https://www.cftc.gov/dea/futures/other_lf.htm) (Fridays 3:30 PM ET)
- [Fed H.4.1 Balance Sheet](https://www.federalreserve.gov/releases/h41/)

### Monthly
- [CFTC Bank Participation Report](https://www.cftc.gov/MarketReports/BankParticipationReports)
- [OCC Quarterly Derivatives](https://www.occ.gov/publications-and-resources/publications/quarterly-report-on-bank-trading-and-derivatives-activities/)

### Event-Driven
- [SEC Form 4 (Insider Trading)](https://www.secform4.com/)
- [SEC EDGAR 8-K Filings](https://www.sec.gov/cgi-bin/browse-edgar)

## 🔧 Customization

### Adding New Indicators

Edit `src/data/indicators.js`:

```javascript
NEW_INDICATOR: {
  id: 'new_indicator',
  name: 'New Indicator Name',
  category: 'Category',
  tier: 1, // 1, 2, or 3
  unit: '%',
  description: 'What this measures',
  source: 'Data source',
  sourceUrl: 'https://...',
  thresholds: {
    normal: { max: 10, phase: 'NORMAL' },
    elevated: { min: 10, max: 20, phase: 'ELEVATED' },
    // ... etc
  },
  currentValue: 0,
  evaluate: (value) => {
    // Return CRISIS_PHASES.LEVEL based on value
  },
},
```

### Updating Values

Use the Zustand store:

```javascript
import useStore from './hooks/useStore';

const { updateIndicator } = useStore();

// Update a single indicator
updateIndicator('tier1', 'SILVER_SPOT_PRICE', 95.50);

// Bulk update
bulkUpdateIndicators([
  { tier: 'tier1', id: 'SILVER_SPOT_PRICE', value: 95.50 },
  { tier: 'tier1', id: 'SHANGHAI_PREMIUM', value: 13.5 },
]);
```

## 🚀 Future Enhancements

- [ ] API integration for live data feeds
- [ ] Push notifications for threshold breaches
- [ ] Historical charting with Recharts
- [ ] Export functionality (CSV, PDF)
- [ ] Mobile app version (React Native)
- [ ] Discord/Telegram alert bot

## ⚠️ Disclaimer

This dashboard is for **informational purposes only**. 

- Bank-specific short positions are **unverified rumors** from social media
- CFTC only provides **aggregate** data, not bank-specific positions
- OTC derivatives exposure is **not publicly disclosed**
- Always verify data from **primary sources**
- This is **NOT financial advice**

## 📜 License

MIT License - Use at your own risk.

---

**Built for the Fault Watch Project**
Monitoring potential systemic risk from concentrated precious metals short positions.
