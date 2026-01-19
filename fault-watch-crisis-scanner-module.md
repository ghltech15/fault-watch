# Fault Watch Crisis Scanner Module

## Module Specification v1.0
**Date:** January 14, 2026  
**Purpose:** Add-on module for existing Fault Watch system to enable real-time crisis scanning of banking sector stress indicators related to silver market dynamics.

---

## 1. MODULE OVERVIEW

### 1.1 Core Function
This module extends Fault Watch with automated crisis scanning capabilities that:
- Track verified stress indicators across monitored banks
- Distinguish between VERIFIED and UNVERIFIED data sources
- Monitor silver market structural indicators
- Track Federal Reserve emergency facility usage
- Generate tiered alerts based on crisis severity

### 1.2 Banks Under Surveillance
Primary targets (silver exposure):
- JPMorgan Chase (JPM)
- Bank of America (BAC)
- Citigroup (C)
- Wells Fargo (WFC)
- HSBC Holdings (HSBC)
- Deutsche Bank (DB)
- UBS Group (UBS)
- Goldman Sachs (GS)

---

## 2. DATA ARCHITECTURE

### 2.1 Indicator Categories

```javascript
const INDICATOR_TIERS = {
  TIER_1_DAILY: {
    name: "Daily Monitoring",
    frequency: "daily",
    indicators: [
      "silver_spot_price",
      "silver_futures_price", 
      "comex_registered_inventory",
      "comex_eligible_inventory",
      "slv_etf_holdings",
      "bank_stock_prices",
      "fed_repo_facility_usage",
      "sofr_rate"
    ]
  },
  TIER_2_WEEKLY: {
    name: "Weekly Analysis", 
    frequency: "weekly",
    indicators: [
      "comex_delivery_notices",
      "cftc_cot_report",
      "bank_cds_spreads",
      "silver_lease_rates",
      "lbma_inventory_changes",
      "etf_inflows_outflows"
    ]
  },
  TIER_3_CRITICAL: {
    name: "Crisis Signals",
    frequency: "event_driven",
    indicators: [
      "fed_emergency_facility_activation",
      "margin_requirement_changes",
      "trading_halts",
      "bank_credit_rating_changes",
      "regulatory_actions",
      "whistleblower_reports"
    ]
  }
};
```

### 2.2 Data Source Classification

```javascript
const SOURCE_VERIFICATION = {
  VERIFIED: {
    level: "green",
    description: "Official government/exchange data",
    sources: [
      "Federal Reserve (federalreserve.gov)",
      "NY Fed (newyorkfed.org)", 
      "CME Group (cmegroup.com)",
      "CFTC (cftc.gov)",
      "SEC EDGAR filings",
      "FDIC",
      "Bank 10-K/10-Q filings"
    ]
  },
  CREDIBLE: {
    level: "yellow", 
    description: "Reputable journalism with specific citations",
    sources: [
      "Bloomberg",
      "Reuters",
      "Wall Street Journal",
      "Financial Times",
      "ICIJ (International Consortium of Investigative Journalists)"
    ]
  },
  UNVERIFIED: {
    level: "orange",
    description: "Single-source claims requiring corroboration",
    sources: [
      "Independent blogs",
      "Substack newsletters",
      "Social media aggregations",
      "Analyst estimates without primary data"
    ]
  },
  SPECULATIVE: {
    level: "red",
    description: "Unsubstantiated claims - monitor but do not act",
    sources: [
      "Anonymous sources",
      "Conspiracy-adjacent outlets",
      "Viral social media without verification"
    ]
  }
};
```

### 2.3 Bank Risk Schema

```javascript
const BANK_RISK_PROFILE = {
  bank_id: "string",
  bank_name: "string",
  ticker: "string",
  
  // Risk Categories
  silver_exposure: {
    level: "CRITICAL | HIGH | ELEVATED | MODERATE | LOW",
    known_position: "number | null", // in ounces if known
    position_direction: "LONG | SHORT | UNKNOWN",
    verification_status: "VERIFIED | UNVERIFIED",
    source: "string",
    last_updated: "ISO_date"
  },
  
  liquidity_risk: {
    level: "CRITICAL | HIGH | ELEVATED | MODERATE | LOW",
    indicators: [
      {
        name: "string",
        value: "number",
        threshold: "number",
        status: "ALERT | WARNING | NORMAL"
      }
    ]
  },
  
  regulatory_risk: {
    active_investigations: "number",
    consent_orders: "number",
    recent_fines: "array",
    whistleblower_allegations: "array"
  },
  
  market_signals: {
    stock_price: "number",
    stock_change_pct: "number",
    cds_spread: "number | null",
    insider_trading: {
      net_direction: "BUYING | SELLING | NEUTRAL",
      total_value: "number"
    }
  },
  
  overall_crisis_risk: "CRITICAL | HIGH | ELEVATED | MODERATE | LOW",
  last_scan: "ISO_date"
};
```

---

## 3. ALERT SYSTEM

### 3.1 Alert Levels

```javascript
const ALERT_LEVELS = {
  LEVEL_5_CRITICAL: {
    color: "#DC2626", // Red
    icon: "🔴",
    name: "CRITICAL",
    description: "Immediate systemic risk - potential bank failure imminent",
    triggers: [
      "Fed emergency facility usage > $100B single day",
      "Trading halt on major bank stock",
      "Credit rating downgrade to junk",
      "Confirmed margin call failure",
      "FDIC intervention announced"
    ],
    action: "IMMEDIATE REVIEW REQUIRED"
  },
  
  LEVEL_4_HIGH: {
    color: "#EA580C", // Orange
    icon: "🟠", 
    name: "HIGH",
    description: "Significant stress indicators - elevated monitoring",
    triggers: [
      "Fed repo usage > $50B (non year-end)",
      "Silver backwardation > 5%",
      "COMEX registered inventory < 50M oz",
      "Bank stock drops > 10% single day",
      "Credible whistleblower report published"
    ],
    action: "ENHANCED MONITORING"
  },
  
  LEVEL_3_ELEVATED: {
    color: "#F59E0B", // Amber
    icon: "🟡",
    name: "ELEVATED", 
    description: "Stress indicators present - watch closely",
    triggers: [
      "Fed repo usage > $25B (non year-end)",
      "Silver in backwardation",
      "COMEX deliveries exceed 20M oz/month",
      "Margin requirements increased",
      "Unverified stress reports circulating"
    ],
    action: "INCREASED VIGILANCE"
  },
  
  LEVEL_2_MODERATE: {
    color: "#10B981", // Green
    icon: "🟢",
    name: "MODERATE",
    description: "Normal market conditions with some volatility",
    triggers: [
      "Standard Fed facility usage",
      "Silver in contango",
      "Normal COMEX delivery patterns"
    ],
    action: "ROUTINE MONITORING"
  },
  
  LEVEL_1_LOW: {
    color: "#6B7280", // Gray
    icon: "⚪",
    name: "LOW",
    description: "Calm markets - no stress indicators",
    triggers: [],
    action: "STANDARD OPERATIONS"
  }
};
```

### 3.2 Alert Generation Logic

```javascript
function generateAlert(indicator, value, bank = null) {
  const alert = {
    id: generateUUID(),
    timestamp: new Date().toISOString(),
    indicator: indicator.name,
    current_value: value,
    threshold_breached: null,
    alert_level: null,
    bank: bank,
    verification_status: indicator.source_verification,
    requires_action: false,
    message: ""
  };
  
  // Check against thresholds
  for (const [level, config] of Object.entries(ALERT_LEVELS)) {
    if (config.triggers.some(trigger => evaluateTrigger(trigger, indicator, value))) {
      alert.alert_level = level;
      alert.threshold_breached = findBreachedThreshold(config.triggers, indicator, value);
      alert.requires_action = level === "LEVEL_5_CRITICAL" || level === "LEVEL_4_HIGH";
      alert.message = generateAlertMessage(indicator, value, level, bank);
      break;
    }
  }
  
  return alert;
}
```

---

## 4. CURRENT FINDINGS (January 14, 2026)

### 4.1 Verified Data Points

```javascript
const VERIFIED_FINDINGS = {
  scan_date: "2026-01-14",
  
  federal_reserve: {
    repo_facility_limit_removed: {
      date: "2025-12-10",
      previous_limit: "$500B daily",
      new_limit: "UNLIMITED",
      status: "VERIFIED",
      source: "Federal Reserve FOMC Statement",
      significance: "Fed opened unlimited liquidity backstop"
    },
    year_end_repo_usage: {
      date: "2025-12-31", 
      amount: 74.6e9, // $74.6 billion
      previous_record: 50.35e9,
      status: "VERIFIED",
      source: "NY Fed Daily Operations Data",
      significance: "Largest liquidity injection since COVID"
    },
    qe_ended: {
      date: "2025-12-01",
      status: "VERIFIED",
      source: "Federal Reserve"
    }
  },
  
  silver_market: {
    backwardation: {
      present: true,
      status: "VERIFIED",
      source: "CME COMEX Futures Data",
      significance: "Spot > Futures indicates physical shortage"
    },
    comex_inventory: {
      registered_oz: 445737395, // ~446M oz as of Jan 7
      trend: "DECLINING",
      status: "VERIFIED", 
      source: "CME Warehouse Reports"
    },
    delivery_activity: {
      jan_7_2026: {
        contracts_delivered: 1624,
        ounces: 8.1e6,
        primary_issuer: "JPMorgan (99%)",
        status: "VERIFIED",
        source: "CME COMEX Delivery Notices"
      }
    },
    china_export_curbs: {
      effective_date: "2026-01-01",
      impact: "~65% global refined supply ring-fenced",
      status: "VERIFIED",
      source: "Multiple news sources"
    },
    supply_deficit: {
      year: 2025,
      deficit_oz: 230e6, // 230 million oz
      consecutive_years: 5,
      status: "VERIFIED",
      source: "Silver Institute, HSBC Research"
    }
  },
  
  bank_earnings_q4_2025: {
    jpmorgan: {
      eps: 5.23,
      revenue: 46.77e9,
      beat_estimates: true,
      notable: "Jamie Dimon warned of 'elevated asset prices'",
      status: "VERIFIED"
    },
    bank_of_america: {
      eps: 0.98,
      revenue: 28.53e9,
      beat_estimates: true,
      nii_growth: "9.7%",
      status: "VERIFIED"
    },
    stress_test_passed: ["JPM", "BAC", "C", "WFC", "GS"],
    status: "VERIFIED"
  }
};
```

### 4.2 Unverified Claims (Flagged for Monitoring)

```javascript
const UNVERIFIED_CLAIMS = {
  scan_date: "2026-01-14",
  
  jpmorgan_silver_short: {
    claim: "5,900 tons of silver short position",
    exposure_estimate: "$13.7 billion",
    source: "DCReport.org (David Cay Johnston)",
    verification_status: "UNVERIFIED",
    concerns: [
      "No specific SEC filing cited",
      "Exposure is author's calculation",
      "No major financial outlet has corroborated",
      "CFTC does not disclose individual bank positions"
    ],
    action: "Monitor for corroboration, do not treat as fact"
  },
  
  jpmorgan_whistleblower: {
    claim: "Misrepresented complexity indicators via prohibited netting",
    source: "ICIJ (International Consortium of Investigative Journalists)",
    verification_status: "CREDIBLE_ALLEGATION",
    details: {
      timeframe: "Since 2016",
      raised_internally: "2018",
      whistleblower_status: "Laid off 2022",
      document: "35-page letter to board audit committee"
    },
    action: "Monitor for regulatory response"
  },
  
  bank_collapse_rumors: {
    claim: "Major bullion bank collapsed after margin call",
    source: "Social media (Dec 29, 2025)",
    verification_status: "SPECULATIVE",
    debunked_by: [
      "No FDIC announcement",
      "No CME trading halt",
      "No Bloomberg/Reuters confirmation"
    ],
    action: "Disregard unless corroborated by official sources"
  },
  
  physical_premium_claims: {
    claim: "Physical silver trading at $130/oz in Tokyo/Dubai",
    source: "Various independent analysts",
    verification_status: "UNVERIFIED",
    note: "Premium existence is likely real, exact figures unconfirmed",
    action: "Seek primary dealer quotes for verification"
  }
};
```

---

## 5. UI COMPONENTS

### 5.1 Crisis Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  FAULT WATCH - CRISIS SCANNER                    [Last Scan: TIME] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  SYSTEM ALERT LEVEL: [🟡 ELEVATED]                          │   │
│  │  Primary Driver: Silver backwardation + Fed facility usage  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │  SILVER INDICATORS  │  │  FED FACILITIES     │                  │
│  │  ─────────────────  │  │  ────────────────   │                  │
│  │  Spot:    $90.42    │  │  SRF Usage: $0B     │                  │
│  │  Futures: $88.15    │  │  (Year-end spike    │                  │
│  │  Status: BACKWARDA- │  │   resolved)         │                  │
│  │          TION 🔴    │  │                     │                  │
│  │                     │  │  ON RRP: $6B        │                  │
│  │  COMEX Reg: 446M oz │  │  Daily Limit: NONE  │                  │
│  │  Trend: ↓ DECLINING │  │                     │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  BANK RISK MATRIX                                           │   │
│  │  ─────────────────────────────────────────────────────────  │   │
│  │  Bank          │ Silver  │ Liquidity │ Overall │ Status    │   │
│  │  ──────────────┼─────────┼───────────┼─────────┼──────────│   │
│  │  JPMorgan      │ 🔴 CRIT*│ 🟠 ELEV   │ 🔴 HIGH │ MONITOR   │   │
│  │  BofA          │ 🟡 MOD  │ 🟠 ELEV   │ 🟠 ELEV │ WATCH     │   │
│  │  Citigroup     │ 🟠 ELEV │ 🟡 MOD    │ 🟠 ELEV │ WATCH     │   │
│  │  Wells Fargo   │ 🟢 LOW  │ 🟢 LOW    │ 🟢 LOW  │ STABLE    │   │
│  │  HSBC          │ 🟠 ELEV │ 🟡 MOD    │ 🟡 MOD  │ WATCH     │   │
│  │  Deutsche      │ 🟠 ELEV │ 🟡 MOD    │ 🟠 ELEV │ WATCH     │   │
│  │  ──────────────┴─────────┴───────────┴─────────┴──────────│   │
│  │  * UNVERIFIED - based on single-source reporting            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  RECENT ALERTS                                              │   │
│  │  ─────────────────────────────────────────────────────────  │   │
│  │  🟡 2026-01-14 | Silver remains in backwardation            │   │
│  │  ✅ 2026-01-05 | Fed SRF usage returned to $0 (resolved)    │   │
│  │  🔴 2025-12-31 | Record $74.6B Fed repo injection           │   │
│  │  🟠 2025-12-10 | Fed removes $500B daily SRF limit          │   │
│  │  🟡 2026-01-01 | China silver export curbs take effect      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  UNVERIFIED CLAIMS TRACKER                    [⚠️ CAUTION]  │   │
│  │  ─────────────────────────────────────────────────────────  │   │
│  │  • JPM 5,900 ton short (DCReport) - AWAITING CORROBORATION  │   │
│  │  • JPM whistleblower netting (ICIJ) - MONITORING            │   │
│  │  • Physical premiums $130/oz - PARTIALLY CORROBORATED       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Design Direction

**Aesthetic:** Industrial/Utilitarian Crisis Control Center
- Dark theme (near-black background: #0a0a0a)
- High contrast status indicators
- Monospace fonts for data (JetBrains Mono, Fira Code)
- Accent color: Amber/Gold (#F59E0B) - ties to precious metals theme
- Red alerts that pulse subtly
- Grid-based layout with clear hierarchy
- Scanlines or subtle noise texture for "control room" feel

---

## 6. INTEGRATION POINTS

### 6.1 Required API Endpoints (for live data)

```javascript
const DATA_SOURCES = {
  // Free/Public APIs
  silver_price: {
    primary: "https://api.metals.live/v1/spot/silver",
    fallback: "Yahoo Finance API"
  },
  
  // Requires scraping or paid API
  comex_inventory: {
    source: "CME Group Warehouse Reports",
    url: "https://www.cmegroup.com/delivery_reports/Silver_stocks.xls",
    format: "XLS",
    update_frequency: "daily"
  },
  
  fed_repo: {
    source: "NY Fed",
    url: "https://markets.newyorkfed.org/api/rp/all/search.json",
    format: "JSON"
  },
  
  bank_stocks: {
    source: "Yahoo Finance / Alpha Vantage",
    tickers: ["JPM", "BAC", "C", "WFC", "GS", "MS"]
  },
  
  // Manual entry required
  cftc_cot: {
    source: "CFTC Commitments of Traders",
    url: "https://www.cftc.gov/dea/futures/other_sf.htm",
    note: "Weekly release, Fridays"
  }
};
```

### 6.2 File Structure for Local Build

```
fault-watch/
├── src/
│   ├── components/
│   │   ├── CrisisScanner/
│   │   │   ├── CrisisScanner.jsx
│   │   │   ├── AlertPanel.jsx
│   │   │   ├── BankRiskMatrix.jsx
│   │   │   ├── SilverIndicators.jsx
│   │   │   ├── FedFacilities.jsx
│   │   │   ├── UnverifiedTracker.jsx
│   │   │   └── styles.css
│   │   └── ... (existing components)
│   │
│   ├── data/
│   │   ├── indicators.js        # Indicator definitions
│   │   ├── thresholds.js        # Alert thresholds
│   │   ├── sources.js           # Source verification rules
│   │   ├── banks.js             # Bank profiles
│   │   └── findings/
│   │       ├── 2026-01-14.json  # Today's scan results
│   │       └── ...
│   │
│   ├── hooks/
│   │   ├── useCrisisScanner.js  # Main scanner logic
│   │   ├── useAlertSystem.js    # Alert generation
│   │   └── useDataFetch.js      # API/data fetching
│   │
│   └── utils/
│       ├── alertLogic.js        # Alert evaluation functions
│       ├── sourceVerification.js # Verify data sources
│       └── formatters.js        # Number/date formatting
│
├── data/
│   └── manual/
│       ├── verified-findings.json
│       └── unverified-claims.json
│
└── README.md
```

---

## 7. IMPLEMENTATION INSTRUCTIONS FOR LOCAL CLAUDE

### 7.1 Build Order

1. **Create data schemas** (indicators.js, thresholds.js, banks.js)
2. **Implement alert logic** (alertLogic.js, useAlertSystem.js)
3. **Build core components** (SilverIndicators, FedFacilities, BankRiskMatrix)
4. **Create main CrisisScanner component** integrating all pieces
5. **Add styling** per design direction (dark, industrial, utilitarian)
6. **Integrate with existing Fault Watch dashboard**

### 7.2 Key Requirements

- **Data verification badges** on every data point
- **Source citations** visible on hover/click
- **Timestamp** for all data showing freshness
- **Manual override** capability for entering news/findings
- **Export functionality** for reports
- **Alert history** with acknowledgment tracking

### 7.3 Silver Price Tracking Note

User's current observations:
- Recent high: $94.50
- Recent low: $87.00  
- Current: $90.42
- User thesis: "Strong buying from commercial + retail FOMO"

Implement tracking to compare spot vs user's thesis validation.

---

## 8. SAMPLE DATA PAYLOAD

```json
{
  "scan_id": "FW-2026-01-14-001",
  "scan_timestamp": "2026-01-14T15:30:00Z",
  "system_alert_level": "ELEVATED",
  "primary_driver": "Silver backwardation persistent + Fed facility changes",
  
  "silver": {
    "spot_price": 90.42,
    "futures_front_month": 88.15,
    "spread": -2.27,
    "spread_status": "BACKWARDATION",
    "user_tracked": {
      "recent_high": 94.50,
      "recent_low": 87.00,
      "recovery_pct": 45.6
    }
  },
  
  "fed": {
    "srf_balance": 0,
    "srf_limit": "UNLIMITED",
    "on_rrp_balance": 6000000000,
    "last_major_event": {
      "date": "2025-12-31",
      "srf_usage": 74600000000,
      "note": "Record year-end injection - now resolved"
    }
  },
  
  "banks": [
    {
      "ticker": "JPM",
      "name": "JPMorgan Chase",
      "silver_risk": "CRITICAL",
      "silver_risk_verified": false,
      "liquidity_risk": "ELEVATED",
      "overall_risk": "HIGH",
      "notes": "Unverified 5,900 ton short claim; whistleblower allegations"
    },
    {
      "ticker": "BAC",
      "name": "Bank of America", 
      "silver_risk": "MODERATE",
      "liquidity_risk": "ELEVATED",
      "overall_risk": "ELEVATED",
      "notes": "$130B unrealized bond losses (verified)"
    }
  ],
  
  "alerts": [
    {
      "level": "ELEVATED",
      "timestamp": "2026-01-14T15:30:00Z",
      "message": "Silver remains in backwardation - physical demand exceeds paper",
      "verified": true
    }
  ],
  
  "unverified_watchlist": [
    {
      "claim": "JPM 5,900 ton silver short",
      "source": "DCReport",
      "status": "AWAITING_CORROBORATION",
      "added": "2026-01-14"
    }
  ]
}
```

---

## 9. NEXT STEPS FOR LOCAL BUILD

1. Copy this specification to your local environment
2. Have local Claude generate the React components based on Section 5 & 6
3. Implement the data schemas from Section 2 & 3
4. Create a manual data entry form for findings like today's scan
5. Style according to Section 5.2 design direction
6. Test alert logic with sample thresholds
7. Integrate with your existing Fault Watch dashboard

---

**Module Version:** 1.0  
**Author:** Claude (Anthropic)  
**For:** Gene's Fault Watch System  
**Classification:** Crisis Monitoring Add-On
