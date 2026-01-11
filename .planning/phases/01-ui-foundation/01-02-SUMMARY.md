---
phase: 01-ui-foundation
plan: 02
subsystem: ui
tags: [layout, hierarchy, typography, streamlit, expanders]

requires: [01-01]
provides:
  - 4-level visual hierarchy system
  - Typography scale (hero/headline/subhead/body/caption/label)
  - Restructured Dashboard, MS Collapse, Bank Exposure tabs
affects: [02-breaking-news-components]

tech-stack:
  added: []
  patterns:
    - Hero → Key Metrics → Details → Expandable hierarchy
    - Typography scale for consistent sizing
    - st.expander for secondary content

key-files:
  created: []
  modified:
    - fault_watch.py

key-decisions:
  - "4-level hierarchy: Hero (72px) → Key Metrics → Summary → Expandable"
  - "Only 4 key metrics on Dashboard (Silver, MS Stock, VIX, KRE)"
  - "Horizontal scenario bar replaces 5 vertical cards"
  - "Secondary content moved to expanders to reduce clutter"

patterns-established:
  - "Typography classes: .text-hero (72px), .text-headline (32px), .text-subhead (20px), .text-body (16px), .text-caption (12px), .text-label (11px)"
  - "Hierarchy pattern: Hero section → Key metrics row → Compact summary → Expandable details"
  - "Use st.expander for all secondary/detailed information"

issues-created: []

duration: 15min
completed: 2026-01-11
---

# Phase 1 Plan 2: Layout Restructure & Visual Hierarchy Summary

**4-level visual hierarchy system with typography scale and decluttered tabs**

## Performance

- **Duration:** 15 min
- **Started:** 2026-01-11
- **Completed:** 2026-01-11
- **Tasks:** 3
- **Files modified:** 1

## Accomplishments

- Dashboard tab restructured with hero risk index, 4 key metrics, horizontal scenario bar, and expandable details
- Typography scale system with 6 size classes for consistent hierarchy
- MS Collapse tab with hero countdown, simplified stress meter, and expandable details
- Bank Exposure tab with hero total ($690B), tiered bank display, and trading ideas in expander

## Task Commits

Each task was committed atomically:

1. **Task 1: Restructure Dashboard tab for visual hierarchy** - `a24a988` (feat)
2. **Task 2: Add typography hierarchy** - `5aba80a` (feat)
3. **Task 3: Declutter MS Collapse and Bank Exposure tabs** - `61dae07` (feat)

## Files Created/Modified

- `fault_watch.py` - Complete layout restructure across 3 render functions, typography CSS system added

## Decisions Made

- Risk index as visual centerpiece at 72px (hero size)
- Limited Dashboard to 4 most critical metrics: Silver, MS Stock, VIX, KRE
- Horizontal scenario probability bar instead of 5 separate cards
- All secondary information moved to st.expander components
- Bank exposure tiered display: Tier 1 always visible, Tier 2/3 expandable

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## Phase 1 Complete

This completes Phase 1 (UI Foundation). All deliverables achieved:
- Decluttered layout with clear information hierarchy
- News/media typography (bold headlines, readable body text)
- Improved spacing and contrast
- Refactored CSS system with typography scale

Ready for Phase 2: Breaking News Components

---
*Phase: 01-ui-foundation*
*Completed: 2026-01-11*
