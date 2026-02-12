# Security Audit & Link Check Summary

**Audit Date:** 2026-02-11
**Audited By:** Claude Code
**Project:** fault.watch

---

## SECURITY FINDINGS

### HIGH PRIORITY

#### 1. Hardcoded Supabase Credentials
**Files affected:**
- `frontend/lib/supabase.ts:3-4`
- `frontend/lib/supabase-server.ts:8`

**Issue:** Supabase URL and anon key are hardcoded as fallbacks:
```typescript
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://xieyimjykzccrjmlqdps.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGci...'
```

**Risk:** Medium - Anon keys are client-side and designed to be public, but hardcoding makes rotation difficult.

**Recommendation:** Remove fallback values; require env vars in production.

---

#### 2. Weak Authorization in Hourly Search API
**File:** `frontend/app/api/hourly-parameter-search/route.ts:488-491`

**Issue:** Authorization bypass allows requests from localhost without authentication:
```typescript
const isAuthorized =
  !expectedKey ||  // No key = authorized (development)
  authHeader === `Bearer ${expectedKey}` ||
  request.headers.get('host')?.includes('localhost')  // localhost bypass
```

**Risk:** Medium - In development mode or misconfigured production, anyone can trigger the cron endpoint.

**Recommendation:**
- Remove localhost bypass for production
- Always require `HOURLY_SEARCH_API_KEY` in production
- Add IP allowlist for Fly.io cron service

---

#### 3. Finnhub API Key in .env
**File:** `.env:1`

**Issue:** API key visible: `FINNHUB_API_KEY=d5ickfpr01qmmfjg366gd5ickfpr01qmmfjg3670`

**Risk:** Low - .env is in .gitignore and not tracked, but key appears to be a test/free tier key.

**Recommendation:** Rotate the key and ensure .env is never committed.

---

#### 4. Docker Compose Dev Credentials
**File:** `docker-compose.yml:12-14, 44-47`

**Issue:** Default development credentials are used:
```yaml
POSTGRES_USER: faultwatch
POSTGRES_PASSWORD: faultwatch_dev
PGADMIN_DEFAULT_PASSWORD: admin
```

**Risk:** Low - Only for local development.

**Recommendation:** Add warning comments; never use in production.

---

### MEDIUM PRIORITY

#### 5. CORS Configuration
**File:** `api.py:338-349`

**Issue:** Wildcard pattern for Vercel previews:
```python
"https://*.vercel.app"  # Vercel previews
```

**Risk:** Low - Pattern is limited to vercel.app domain.

**Recommendation:** Consider restricting to specific preview URLs if possible.

---

#### 6. Google Analytics ID Exposed
**File:** `frontend/app/layout.tsx:25`

**Issue:** GA Measurement ID hardcoded: `G-J40XCP5K2S`

**Risk:** Very Low - GA IDs are designed to be public.

**Recommendation:** No action needed; this is expected behavior.

---

### LOW PRIORITY / GOOD PRACTICES OBSERVED

- **No SQL Injection:** Database uses Supabase client with parameterized queries
- **No XSS vulnerabilities:** No `dangerouslySetInnerHTML`, `eval()`, or `innerHTML` usage found
- **No secret files tracked:** `.env` is properly in `.gitignore`
- **CORS properly configured:** Limited to known origins
- **Environment variables used:** API keys loaded from environment where possible

---

## EXTERNAL LINKS TO CHECK

### API Data Sources (Critical - Require Testing)

| Source | URL | Purpose |
|--------|-----|---------|
| Finnhub | `https://finnhub.io/api/v1/quote` | Stock quotes |
| FRED | `https://api.stlouisfed.org/fred/series/observations` | Economic data |
| FX Rates API | `https://api.fxratesapi.com/latest` | Silver/Gold prices |
| Metals.live | `https://api.metals.live/v1/spot/silver` | Spot metal prices |
| CoinGecko | `https://api.coingecko.com/api/v3/simple/price` | Crypto prices |
| GoldSilver.ai | `https://goldsilver.ai/api/metal-prices/shanghai-silver` | Shanghai premium |

### Government/Official Sources (May Change Structure)

| Source | URL | Purpose |
|--------|-----|---------|
| OFR Financial Stress | `https://www.financialresearch.gov/financial-stress-index/` | Stress index |
| NY Fed Repo | `https://www.newyorkfed.org/markets/desk-operations/repo` | Fed operations |
| FRED SOFR | `https://fred.stlouisfed.org/series/SOFR` | SOFR rate |
| COMEX Inventory | `https://www.cmegroup.com/delivery_reports/Silver_stocks.xls` | Silver stocks |
| Fed H.4.1 | `https://www.federalreserve.gov/releases/h41/` | Fed balance sheet |
| SEC OpenInsider | `https://openinsider.com` | Insider transactions |
| Trading Economics | `https://tradingeconomics.com/commodity/silver` | Silver price |
| CFTC COT | `https://www.cftc.gov/dea/futures/other_lf.htm` | COT reports |
| CFTC Disaggregated | `https://www.cftc.gov/dea/futures/deacmxsf.htm` | Silver COT |
| LBMA Vault Data | `https://www.lbma.org.uk/prices-and-data/london-vault-data` | Vault holdings |
| FDIC Failed Banks | `https://www.fdic.gov/resources/resolutions/bank-failures/failed-bank-list/` | Bank failures |

### News/RSS Feeds (Need Validation)

| Source | URL |
|--------|-----|
| Reuters Finance | `https://feeds.reuters.com/reuters/businessNews` |
| Reuters Markets | `https://feeds.reuters.com/reuters/marketsNews` |
| Bloomberg | `https://feeds.bloomberg.com/markets/news.rss` |
| WSJ Markets | `https://feeds.wsj.com/xml/rss/3_7031.xml` |
| FT Markets | `https://www.ft.com/markets?format=rss` |
| Seeking Alpha | `https://seekingalpha.com/market_currents.xml` |
| Kitco | `https://www.kitco.com/rss/rss.xml` |
| ZeroHedge | `https://feeds.feedburner.com/zerohedge/feed` |

### Dealer Sites (May Block Scraping)

| Dealer | URL |
|--------|-----|
| JM Bullion | `https://www.jmbullion.com/silver/` |
| APMEX | `https://www.apmex.com/silver` |
| SD Bullion | `https://sdbullion.com/silver` |
| Provident Metals | `https://www.providentmetals.com` |
| Money Metals | `https://www.moneymetals.com` |

### Internal/Production URLs

| Purpose | URL |
|--------|-----|
| Production Frontend | `https://fault.watch` |
| Production Frontend (www) | `https://www.fault.watch` |
| Production API | `https://fault-watch-api.fly.dev` |
| Production UI (Fly) | `https://fault-watch-ui.fly.dev` |

### Social/Share URLs

| Platform | URL Pattern |
|----------|-------------|
| Twitter Share | `https://twitter.com/intent/tweet?text=...&url=...` |
| Reddit Submit | `https://reddit.com/submit?url=...&title=...` |
| Reddit API | `https://oauth.reddit.com` |

---

## RESEARCH DATA TO AUDIT

### Key Dates Referenced in Code
These dates/events are hardcoded and may need updating:

| Date | Event | Location |
|------|-------|----------|
| Feb 15, 2026 | SEC Deadline | `api.py:355` |
| Jan 31, 2026 | Lloyds Deadline | `api.py:356` |
| Jan 17, 2026 | SILJ options expiration | `api.py:4989` |
| Jan 31, 2026 | Rumored HSBC exit deadline | `api.py:4990` |
| Early Feb 2026 | LBMA January vault data release | `api.py:4991` |
| Dec 11, 2025 | NY Fed repo policy change | `api.py:4997` |
| Oct 8, 2025 | India silver order / LBMA event | `api.py:5002` |

### Hardcoded Financial Data
These values should be periodically verified:

| Data Point | Value | Location |
|------------|-------|----------|
| Total Naked Shorts | 29.84B oz | `api.py:366` |
| Available Physical | 1B oz | `api.py:367` |
| Naked Short Ratio | 30:1 | `api.py:368` |
| Years Production | 36 years | `api.py:369` |

---

## CHECKLIST FOR COMET

### Security Tasks
- [ ] Rotate Finnhub API key
- [ ] Verify Supabase RLS (Row Level Security) policies are properly configured
- [ ] Remove localhost authorization bypass in production hourly search API
- [ ] Set `HOURLY_SEARCH_API_KEY` secret in Fly.io
- [ ] Review Supabase service role key access patterns

### Link Testing Tasks
- [ ] Test all API data source endpoints (Finnhub, FRED, FX Rates, etc.)
- [ ] Verify government source URLs still work (SEC, CFTC, Fed, FDIC)
- [ ] Check RSS feed URLs are active
- [ ] Test dealer website scrapers still function
- [ ] Verify production URLs (fault.watch, fault-watch-api.fly.dev)

### Research Audit Tasks
- [ ] Verify key dates are still accurate
- [ ] Update any passed deadlines (Jan 17, Jan 31, Feb 15 2026)
- [ ] Confirm financial exposure numbers are current
- [ ] Review claims and sources for accuracy
- [ ] Check LBMA authorized companies count (currently 44)

### Recommended Periodic Tasks
- [ ] Weekly: Check API endpoints are responding
- [ ] Monthly: Review government data source structures
- [ ] Monthly: Verify dealer scraping still works
- [ ] Quarterly: Full security review
- [ ] On news: Update key dates and events

---

## SUMMARY

**Critical Issues:** 0
**High Priority Issues:** 2 (hardcoded credentials, weak auth bypass)
**Medium Priority Issues:** 2 (CORS wildcard, exposed GA ID)
**Low Priority Issues:** 1 (docker dev credentials)

**External Links to Verify:** 50+
**Research Data Points to Audit:** 10+

The codebase follows good security practices overall. The main concerns are:
1. Authorization bypass in the hourly search API for localhost
2. Hardcoded Supabase credentials as fallbacks

Both are easily fixable with environment variable enforcement.
