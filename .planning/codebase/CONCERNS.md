# CONCERNS.md
> Technical debt and issues for fault-watch

**Last Updated:** 2026-01-11

---

## Technical Debt

### 1. Single-File Architecture (High Priority)
- **Location:** `fault_watch.py` (1269 lines, 54KB)
- **Issue:** All logic in one file makes maintenance difficult
- **Recommendation:** Split into modules:
  - `config.py` - Constants and thresholds
  - `data.py` - Data fetching functions
  - `calculations.py` - Business logic
  - `ui/` - Tab rendering functions

### 2. Duplicate Version Files
- **Location:** `fault_watch_v2.py`, `fault_watch_v3.py`, `fault_watch_v4.py`
- **Issue:** Multiple version files clutter the repo
- **Recommendation:** Remove old versions or move to `archive/` directory

### 3. Hardcoded Data
- **Location:** `fault_watch.py:42-85`
- **Issue:** Bank exposure, Fed repo data, thresholds all hardcoded
- **Recommendation:** Move to Supabase (schema exists) or config files

---

## Known Issues

### 1. Silent Error Handling
- **Location:** `fault_watch.py:242` and throughout
- **Issue:** `except: continue` swallows all errors silently
- **Impact:** Failed API calls go unnoticed, no debugging info
- **Example:**
  ```python
  try:
      data = yf.Ticker(ticker)
      # ...
  except:
      continue  # No logging, no user notification
  ```

### 2. No Input Validation
- **Location:** `fault_watch.py:1125-1127`
- **Issue:** `st.number_input` values used directly in calculations
- **Impact:** Edge cases (negative prices, zero) could cause errors

### 3. Hardcoded Fallback Values
- **Location:** `fault_watch.py:261`
- **Issue:** Bitcoin fallback to `$91,000` if CoinGecko fails
- **Impact:** Stale data displayed without user awareness

---

## Security

### 1. No Secrets in Code (Good)
- Environment variables used for Supabase credentials
- `.env` properly gitignored

### 2. No Authentication
- **Location:** Entire app
- **Issue:** Anyone can access the dashboard
- **Impact:** Not a security risk (public data), but limits personalization
- **Note:** Supabase auth schema exists but not implemented

### 3. Raw HTML Injection
- **Location:** Multiple `st.markdown(..., unsafe_allow_html=True)`
- **Issue:** If user input were displayed, XSS possible
- **Current Risk:** Low - no user-generated content displayed

---

## Performance

### 1. API Rate Limits
- **Location:** `fetch_all_prices()` - `fault_watch.py:184`
- **Issue:** 25+ tickers fetched on every cache miss
- **Impact:** Could hit Yahoo Finance rate limits with heavy traffic
- **Mitigation:** 60s cache helps, but no rate limit handling

### 2. No Lazy Loading
- **Location:** `main()` - `fault_watch.py:1190`
- **Issue:** All data fetched on page load, even for unviewed tabs
- **Impact:** Slower initial load, wasted API calls

### 3. Large CSS Block
- **Location:** `fault_watch.py:90-178`
- **Issue:** 88 lines of CSS sent on every page load
- **Recommendation:** Move to external `.css` file

---

## Documentation Gaps

### 1. No Inline Comments in Calculations
- **Location:** `calculate_scenarios()` - `fault_watch.py:484-552`
- **Issue:** Complex probability adjustments without explanation
- **Impact:** Hard to understand/modify scenario logic

### 2. Magic Numbers
- **Location:** `fault_watch.py:504-546`
- **Issue:** Values like `0.25`, `0.15`, `0.20` unexplained
- **Example:**
  ```python
  if ms_daily < -10:
      probs['credit_crunch'] += 0.25  # Why 0.25?
      probs['slow_burn'] -= 0.20      # Why 0.20?
  ```

---

## Missing Features

### 1. No Tests
- **Impact:** Changes risk breaking existing functionality
- **Priority:** High - especially for financial calculations

### 2. Supabase Not Integrated
- **Impact:** Data doesn't persist, no historical charts
- **Schema:** Ready in `supabase_schema.sql`
- **Note:** All `current_prices`, `price_history`, etc. unused

### 3. No Error Boundaries
- **Impact:** One API failure could crash the whole dashboard

---

## Priority Ranking

| Issue | Severity | Effort | Priority |
|-------|----------|--------|----------|
| Silent error handling | High | Low | 1 |
| No tests | High | Medium | 2 |
| Single-file architecture | Medium | High | 3 |
| Supabase integration | Medium | Medium | 4 |
| Hardcoded data | Low | Low | 5 |
| Remove old versions | Low | Low | 6 |
