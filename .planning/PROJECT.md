# PROJECT.md
> fault.watch UI Redesign & TikTok Content Engine

## Vision

Transform fault.watch from a functional Streamlit dashboard into a **news/media-style crisis monitor** with bold headlines and breaking news urgency, plus a **TikTok content generation engine** that automatically creates viral short-form videos from market events.

---

## Problem Statement

**Current Issues:**
1. UI is cluttered and busy - too much information on screen
2. Poor visual hierarchy - hard to distinguish critical alerts from secondary info
3. Looks dated - needs modern, polished news/media aesthetic
4. No content creation tools - manual effort to share insights on social media

**Desired Outcome:**
- Dashboard that looks like Bloomberg meets CNN Breaking News
- One-click export of charts and metrics as video-ready content
- Auto-generated clips triggered by market events
- Easy to scan, dramatic visual impact for viral potential

---

## Requirements

### Validated

- ✓ Real-time price fetching (Yahoo Finance, CoinGecko) — existing
- ✓ MS short position tracking and countdown — existing
- ✓ Bank PM derivatives exposure display — existing
- ✓ Fed response tracking — existing
- ✓ Domino effect cascade tracker — existing
- ✓ Position P&L calculator — existing
- ✓ Scenario probability analysis — existing
- ✓ 7-tab dashboard structure — existing
- ✓ Dark theme with red accent — existing
- ✓ Fly.io deployment — existing

### Active

**UI Redesign:**
- [ ] News/media visual style (bold headlines, breaking news urgency)
- [ ] Decluttered layout with clear visual hierarchy
- [ ] "Breaking alert" component with dramatic styling
- [ ] Improved readability (typography, spacing, contrast)
- [ ] Mobile-responsive design (web, not app)
- [ ] Animated transitions and attention-grabbing effects

**TikTok Content Engine:**
- [ ] Screenshot/screen recording export mode
- [ ] Auto-generated clips from price alerts (silver $100, MS -5%)
- [ ] Daily summary video generation
- [ ] Breaking event video generation (Fed repo spike, domino falls)
- [ ] Export-ready graphics (9:16 aspect ratio for TikTok/Reels)
- [ ] One-click download of video-ready assets

### Out of Scope

- Mobile native app — web only for v1
- User accounts/authentication — keep public, no login
- Push notifications — manual refresh is acceptable
- Paid APIs or services — free tier only

---

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| News/media style over Bloomberg density | Viral potential, easier to consume | — Pending |
| UI redesign before content tools | Foundation must be video-ready first | — Pending |
| Flexible on Streamlit | May need React/Next.js for video features | — Pending |

---

## Success Criteria

1. **UI:** First-time visitors immediately understand "crisis is happening"
2. **Readability:** Key metrics scannable in <3 seconds
3. **Content:** Generate TikTok-ready video in <30 seconds
4. **Viral:** Design optimized for screenshots and screen recordings

---

## Technical Considerations

**Current Stack:**
- Streamlit 1.40.0 (may need to evaluate alternatives for video)
- Python 3.11
- Plotly for charts
- Fly.io hosting

**Potential Additions:**
- Video generation library (MoviePy, FFmpeg)
- Image export (Plotly static export, Selenium screenshots)
- Animation libraries for dramatic effects

---

*Last updated: 2026-01-11 after initialization*
