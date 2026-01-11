# ARCHITECTURE.md
> System design and patterns for fault-watch

**Last Updated:** 2026-01-11

---

## Pattern Overview

**Architecture Style:** Single-file Streamlit Monolith

The application is a self-contained Python script that uses Streamlit's reactive programming model. All logic—data fetching, calculations, and rendering—lives in `fault_watch.py`.

---

## Layers

```
┌─────────────────────────────────────────────┐
│              UI Layer (Streamlit)            │
│  render_*_tab() functions                    │
├─────────────────────────────────────────────┤
│           Calculation Layer                  │
│  calculate_*() functions                     │
├─────────────────────────────────────────────┤
│             Data Layer                       │
│  fetch_all_prices() with @st.cache_data     │
├─────────────────────────────────────────────┤
│          External Services                   │
│  Yahoo Finance API, CoinGecko API           │
│  (Supabase configured but not active)       │
└─────────────────────────────────────────────┘
```

---

## Data Flow

1. **Page Load:** `main()` called in `fault_watch.py`
2. **Data Fetch:** `fetch_all_prices()` calls Yahoo Finance & CoinGecko (cached 60s)
3. **Calculate:** Multiple `calculate_*()` functions process raw data
4. **Render:** Tab-specific `render_*_tab()` functions display UI
5. **Refresh:** User clicks refresh button → cache cleared → `st.rerun()`

---

## Key Abstractions

| Pattern | Implementation | Location |
|---------|----------------|----------|
| Caching | `@st.cache_data(ttl=60)` | `fetch_all_prices()` |
| Tab Router | `st.tabs()` with 7 tabs | `main()` |
| Config | Python dicts as constants | `THRESHOLDS`, `BANK_PM_EXPOSURE` |
| Styling | Inline CSS via `st.markdown()` | Top of `fault_watch.py` |

---

## Entry Points

| Entry Point | File | Purpose |
|-------------|------|---------|
| Main App | `fault_watch.py:1268` | `if __name__ == "__main__": main()` |
| Docker | `Dockerfile:32` | `CMD ["streamlit", "run", "fault_watch.py", ...]` |

---

## Module Boundaries

Currently **no module boundaries** - everything in single file:

- Lines 1-29: Header comments
- Lines 30-86: Constants and configuration
- Lines 87-178: CSS styling
- Lines 180-270: Data fetching
- Lines 272-652: Calculation functions
- Lines 654-1163: Render functions (one per tab)
- Lines 1165-1268: Main function and entry point

---

## State Management

- **Server State:** Streamlit session (automatic)
- **Cached Data:** `@st.cache_data` with 60s TTL
- **User Input:** `st.number_input`, `st.sidebar` widgets
- **Persistent State:** Supabase (schema ready, not integrated in UI)
