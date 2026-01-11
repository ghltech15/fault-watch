# CONVENTIONS.md
> Code style and patterns for fault-watch

**Last Updated:** 2026-01-11

---

## Code Style

**Formatting:**
- Indentation: 4 spaces (Python standard)
- Quotes: Single quotes for strings, double for docstrings
- Line length: ~100-120 characters (no strict limit)
- No linter/formatter config files detected

**Imports:**
```python
# Standard library first
import json
import time
from datetime import datetime, timedelta

# Third-party
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import requests
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Constants | UPPER_SNAKE_CASE | `SEC_DEADLINE`, `MS_SHORT_POSITION_OZ` |
| Functions | snake_case | `calculate_countdown()`, `fetch_all_prices()` |
| Variables | snake_case | `silver_price`, `stress_level` |
| Dict Keys | snake_case | `'change_pct'`, `'week_change'` |

**Function Prefixes:**
- `calculate_*` - Pure computation functions
- `render_*_tab` - Streamlit UI rendering functions
- `fetch_*` - Data fetching functions
- `generate_*` - Content generation functions

---

## Common Patterns

**Data Dictionary Pattern:**
```python
# Configuration stored as nested dicts
BANK_PM_EXPOSURE = {
    'JPM': {'name': 'JPMorgan Chase', 'ticker': 'JPM', 'pm_derivatives': 437.4e9, ...},
    'C': {'name': 'Citigroup', 'ticker': 'C', 'pm_derivatives': 204.3e9, ...},
}
```

**Cached Data Fetching:**
```python
@st.cache_data(ttl=60)
def fetch_all_prices():
    prices = {}
    # ... fetch logic
    return prices
```

**Streamlit Tab Pattern:**
```python
def render_dashboard_tab(prices, indicators, scenarios, allocation, alerts, risk_index):
    """Render main dashboard tab"""
    # All rendering logic for one tab
    st.markdown("### Title")
    col1, col2 = st.columns(2)
    # ...
```

**Try/Except Silence Pattern:**
```python
try:
    data = yf.Ticker(ticker)
    # ... process
except:
    continue  # Silently skip failures
```

---

## Documentation Style

**File Header:**
```python
"""
FAULT.WATCH v4.0 - COMPLETE CRISIS MONITOR
===========================================
Adaptive Systemic Risk Monitoring System

TABS:
1. Dashboard - Main overview
2. MS Collapse - Morgan Stanley tracking
...
"""
```

**Section Comments:**
```python
# =============================================================================
# PAGE CONFIG
# =============================================================================
```

**Function Docstrings:**
```python
def calculate_countdown():
    """Calculate time remaining to SEC deadline"""
```

---

## HTML/CSS in Streamlit

**Inline CSS via markdown:**
```python
st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; }
    .alert-critical {
        background: rgba(255,59,92,0.15);
        border: 1px solid #ff3b5c;
        ...
    }
</style>
""", unsafe_allow_html=True)
```

**HTML components:**
```python
st.markdown(f"""
<div class="countdown-box">
    <div class="countdown-number">{countdown['days']} DAYS</div>
</div>
""", unsafe_allow_html=True)
```
