# INTEGRATIONS.md
> External services and APIs for fault-watch

**Last Updated:** 2026-01-11

---

## External APIs

### Yahoo Finance (yfinance)
- **Purpose:** Real-time stock and commodity prices
- **Library:** `yfinance==0.2.36`
- **Location:** `fault_watch.py:228-241`
- **Tickers fetched:**
  - Market: SPY, ^VIX, TLT, DX-Y.NYB
  - Metals: GC=F, SI=F, GDX, SILJ, SLV
  - US Banks: MS, JPM, C, BAC, GS, WFC
  - EU Banks: HSBC, DB, UBS, BCS, BNS
  - Stress: KRE, XLF, HYG
- **Caching:** 60 second TTL via `@st.cache_data`
- **Error Handling:** Silent `try/except` - skips failed tickers

### CoinGecko
- **Purpose:** Cryptocurrency prices (Bitcoin, Ethereum)
- **Endpoint:** `https://api.coingecko.com/api/v3/simple/price`
- **Location:** `fault_watch.py:246-261`
- **Fallback:** Hardcoded `$91,000` if API fails
- **No API key required** (public endpoint)

---

## Database

### Supabase (PostgreSQL)
- **Purpose:** Persistent data storage, user accounts
- **Library:** `supabase==2.3.4`
- **Schema:** `supabase_schema.sql`
- **Tables:**
  - `current_prices` - Latest price cache
  - `price_history` - Historical data for charts
  - `user_positions` - User tracked positions
  - `user_alerts` - Custom price alerts
  - `fed_repo_data` - Fed operations tracking
  - `bank_exposure` - Bank PM derivatives data

**Current Status:** Schema defined but **not actively used** in `fault_watch.py`. All data is currently fetched live from APIs.

**Connection:**
```python
# Not implemented in current code
# Would use environment variables:
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
```

---

## Third-Party Services

### Fly.io
- **Purpose:** Production hosting
- **Config:** `fly.toml`
- **Region:** San Jose (sjc)
- **Resources:** 1 shared CPU, 512MB RAM
- **Auto-scaling:** Yes (1 min, 100 max connections)

### GitHub Actions
- **Purpose:** CI/CD pipeline
- **Config:** `.github/workflows/deploy.yml`
- **Trigger:** Push to main branch → auto-deploy

---

## Authentication

**Not implemented** - Supabase auth is configured in schema (`auth.users` references) but no authentication UI exists in the Streamlit app.

---

## Webhooks

**Not detected** - No webhook endpoints.

---

## Data Sources Summary

| Data | Source | Update | Reliability |
|------|--------|--------|-------------|
| Stock Prices | Yahoo Finance | 60s cache | High (free API) |
| Crypto Prices | CoinGecko | 60s cache | Medium (rate limits) |
| PM Derivatives | Hardcoded | Manual | Static (OCC quarterly) |
| Fed Repo | Hardcoded | Manual | Static (manual entry) |
| Bank Data | Hardcoded | Manual | Static (manual entry) |
