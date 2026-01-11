# fault.watch

Adaptive Systemic Risk Monitoring System

## Quick Start

```powershell
cd C:\Users\ghlte\projects\fault-watch
.\venv\Scripts\Activate
streamlit run fault_watch.py
```

## Features

- Real-time price monitoring (Gold, Silver, VIX, Bitcoin, Banks, etc.)
- Dynamic scenario probability calculation
- Automated alerts when thresholds are breached
- Adaptive allocation recommendations
- Auto-refresh capability

## Scenarios Tracked

1. **Slow Burn** - Status quo, gradual deterioration
2. **Credit Crunch** - CRE triggers banking crisis
3. **Inflation Spike** - Inflation reaccelerates, Fed trapped
4. **Deflationary Bust** - Credit collapse overwhelms Fed
5. **Monetary Reset** - Dollar crisis, new monetary system

## Key Thresholds

| Indicator | Warning | Critical |
|-----------|---------|----------|
| VIX | >25 | >35 |
| Silver | >$90 | >$100 |
| KRE Weekly | -5% | -10% |
| HYG Weekly | -3% | -5% |
| Dollar Index | <100 | <95 |

## Data Sources

- Yahoo Finance (stocks, ETFs, VIX)
- CoinGecko (Bitcoin)
- All free, no API keys required
