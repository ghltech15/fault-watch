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

### Phase 1: UI Foundation
**Goal:** Restructure layout, typography, and visual hierarchy for news/media style

**Deliverables:**
- Decluttered layout with clear information hierarchy
- News/media typography (bold headlines, readable body text)
- Improved spacing and contrast
- Refactored CSS system

**Research:** Unlikely (internal Streamlit patterns, CSS)

**Status:** Complete (2/2 plans)

---

### Phase 2: Breaking News Components
**Goal:** Create dramatic alert components with breaking news urgency

**Deliverables:**
- "Breaking Alert" banner component with animation
- Headline styling (large, bold, attention-grabbing)
- Status indicators with dramatic color coding
- Animated transitions for key metrics

**Research:** Unlikely (CSS animations, Streamlit components)

**Status:** Not started

---

### Phase 3: Content Export Engine
**Goal:** Enable one-click export of charts and metrics as video-ready assets

**Deliverables:**
- Screenshot export functionality
- 9:16 aspect ratio export for TikTok/Reels
- Chart export as high-quality images
- Export-ready graphics with branding

**Research:** Likely (image/video export libraries)
**Research topics:**
- Plotly static image export (kaleido)
- Selenium/Playwright for full-page screenshots
- PIL/Pillow for image processing
- 9:16 aspect ratio composition

**Status:** Not started

---

### Phase 4: Auto-Clip Generator
**Goal:** Automatically generate TikTok clips from market events

**Deliverables:**
- Price alert trigger → video generation
- Daily summary video generation
- Breaking event video generation
- One-click video download

**Research:** Likely (video generation libraries)
**Research topics:**
- MoviePy for video composition
- FFmpeg integration
- Text overlay and animation
- Background music/sound effects

**Status:** Not started

---

## Dependencies

```
Phase 1 ─────► Phase 2 ─────► Phase 3 ─────► Phase 4
(foundation)   (components)   (export)       (video)
```

- Phase 2 depends on Phase 1 (needs new layout)
- Phase 3 depends on Phase 2 (exports the new components)
- Phase 4 depends on Phase 3 (combines exports into video)

---

## Progress Tracking

| Phase | Status | Plans | Completed |
|-------|--------|-------|-----------|
| 1. UI Foundation | Complete | 2 | 2 |
| 2. Breaking News Components | Not started | 0 | 0 |
| 3. Content Export Engine | Not started | 0 | 0 |
| 4. Auto-Clip Generator | Not started | 0 | 0 |

**Overall:** 20% complete (2 of ~10 estimated plans)

---

*Last updated: 2026-01-11*
