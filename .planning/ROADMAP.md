# ROADMAP.md
> fault.watch UI Redesign & TikTok Content Engine

## Milestone: v2.0 — News/Media Dashboard + Content Creation

**Depth:** Quick (3-5 phases, 1-3 plans each)
**Mode:** YOLO

---

## Domain Expertise

None — using standard web/Python patterns

---

## Phases

### Phase 1: UI Foundation ✓
**Goal:** Restructure layout, typography, and visual hierarchy for news/media style

**Deliverables:**
- Decluttered layout with clear information hierarchy
- News/media typography (bold headlines, readable body text)
- Improved spacing and contrast
- Refactored CSS system

**Research:** Unlikely (internal Streamlit patterns, CSS)

**Status:** Complete (2/2 plans)

---

### Phase 2: Content Export Engine ⬅️ PRIORITY
**Goal:** Enable one-click export of charts and metrics as video-ready assets

**Deliverables:**
- Screenshot export functionality
- 9:16 aspect ratio export for TikTok/Reels
- Chart export as high-quality images
- Export-ready graphics with branding
- Trigger-based export (price alerts, deadlines)

**Research:** Likely (image/video export libraries)
**Research topics:**
- Plotly static image export (kaleido)
- Selenium/Playwright for full-page screenshots
- PIL/Pillow for image processing
- 9:16 aspect ratio composition

**Status:** Complete (3/3 plans)

---

### Phase 3: Auto-Clip Generator
**Goal:** Automatically generate TikTok clips from market events

**Deliverables:**
- Price alert trigger → video generation
- Daily summary video generation
- Breaking event video generation
- One-click video download
- Output to deployment folder

**Research:** Likely (video generation libraries)
**Research topics:**
- MoviePy for video composition
- FFmpeg integration
- Text overlay and animation
- Background music/sound effects

**Status:** Not started

---

### Phase 4: Breaking News Components (DEFERRED)
**Goal:** Create dramatic alert components with breaking news urgency

**Deliverables:**
- Enhanced "Breaking Alert" banner component
- Headline styling (large, bold, attention-grabbing)
- Status indicators with dramatic color coding
- Animated transitions for key metrics

**Research:** Unlikely (CSS animations, Streamlit components)

**Status:** Deferred (content creation prioritized)

---

## Dependencies

```
Phase 1 ─────► Phase 2 ─────► Phase 3 ─────► Phase 4
(foundation)   (export)       (video)        (UI polish)
```

- Phase 2 depends on Phase 1 (exports current UI)
- Phase 3 depends on Phase 2 (combines exports into video)
- Phase 4 can happen anytime (UI polish, not blocking)

**RATIONALE:** Content creation prioritized to build audience while developing.

---

## Progress Tracking

| Phase | Status | Plans | Completed |
|-------|--------|-------|-----------|
| 1. UI Foundation | Complete | 2 | 2 |
| 2. Content Export Engine | Complete | 3 | 3 |
| 3. Auto-Clip Generator | Not started | 0 | 0 |
| 4. Breaking News Components | Deferred | 0 | 0 |

**Overall:** 50% complete (5 of ~10 estimated plans)

---

*Last updated: 2026-01-11*
