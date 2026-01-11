# TESTING.md
> Test structure and practices for fault-watch

**Last Updated:** 2026-01-11

---

## Framework

**Not detected** - No test framework is currently configured.

---

## Structure

**Not detected** - No test files found:
- No `tests/` directory
- No `*_test.py` files
- No `test_*.py` files
- No `*.spec.py` files
- No `__tests__/` directory

---

## Coverage

**Not detected** - No coverage tooling configured.

---

## Tools

**Not detected** - No testing tools in `requirements.txt`:
- No pytest
- No unittest
- No coverage
- No tox

---

## Current Testing Approach

Manual testing only:
1. Run `streamlit run fault_watch.py`
2. Manually check each tab
3. Verify data displays correctly
4. Check for console errors

---

## Recommended Testing Setup

If tests were to be added:

```python
# requirements-dev.txt
pytest==8.0.0
pytest-cov==4.1.0
pytest-mock==3.12.0

# tests/test_calculations.py
def test_calculate_countdown():
    result = calculate_countdown()
    assert 'days' in result
    assert 'hours' in result
    assert 'expired' in result

def test_calculate_ms_exposure():
    result = calculate_ms_exposure(silver_price=100, entry_price=30)
    assert result['paper_loss'] > 0
    assert 'loss_vs_equity' in result
```

---

## Test Priority Areas

If adding tests, these functions should be tested first:

1. `calculate_countdown()` - Date math
2. `calculate_ms_exposure()` - Financial calculations
3. `calculate_scenarios()` - Probability logic
4. `calculate_allocation()` - Portfolio math
5. `fetch_all_prices()` - API error handling
