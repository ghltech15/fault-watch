# fault.watch UI Audit & Engagement Recommendations

**Audit Date:** January 2026
**Auditor:** Claude
**Objective:** Identify opportunities to increase user engagement and time-on-site

---

## Executive Summary

The current fault.watch UI has strong visual foundations with dramatic crisis gauges, color-coded indicators, and a narrative scroll structure. However, **the site is primarily passive** - users read content but have few reasons to interact, explore, or return.

**Key Finding:** The site lacks the "sticky" elements that keep users engaged and coming back. Without interactivity, personalization, or social features, users view the data once and leave.

---

## Current State Assessment

### Strengths
| Element | Rating | Notes |
|---------|--------|-------|
| Visual Impact | 9/10 | Dramatic crisis gauge, strong color coding |
| Information Hierarchy | 8/10 | Clear narrative flow (Trigger → Exposure → Cracks → Cascade) |
| Data Presentation | 8/10 | Good use of cards, progress bars, phase indicators |
| Mobile Responsiveness | 7/10 | Basic responsiveness, could be better |
| Animation Quality | 8/10 | Smooth Framer Motion animations |
| Creator Tools | 7/10 | Screenshot/share/record mode functional |

### Weaknesses
| Element | Rating | Issue |
|---------|--------|-------|
| Interactivity | 3/10 | Almost entirely passive viewing |
| Personalization | 1/10 | No user preferences or customization |
| Return Motivation | 2/10 | No alerts, notifications, or reasons to come back |
| Social Features | 1/10 | No community, comments, or live users |
| Gamification | 0/10 | No achievements, streaks, or rewards |
| Data Exploration | 3/10 | No "what if" scenarios or historical charts |

---

## High-Impact Recommendations

### 1. ADD LIVE URGENCY INDICATORS
**Impact: High | Effort: Low**

Users need to feel "this is happening NOW."

**Current Problem:** Static data with "Last updated" timestamp feels dead.

**Solutions:**
- **Pulsing "LIVE" indicator** with active user count: "1,247 watching now"
- **Real-time activity feed** showing recent price movements as they happen
- **Countdown timers** that create urgency: "Silver could hit $100 in 12 days at current rate"
- **"Since you arrived" changes** - Show what changed during their visit

```tsx
// Example: Live Activity Pulse
<div className="fixed top-4 right-4 flex items-center gap-2">
  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
  <span className="text-sm text-gray-400">1,247 watching</span>
  <span className="text-xs text-gray-600">Updated 3s ago</span>
</div>
```

---

### 2. ADD INTERACTIVE "WHAT IF" SCENARIOS
**Impact: High | Effort: Medium**

Let users explore hypotheticals to understand the crisis better.

**Current Problem:** Users can only see current state, not explore possibilities.

**Solutions:**
- **Silver Price Slider** - "Drag to see what happens if silver hits $120"
- **Bank Failure Simulator** - "Click a bank to see cascade effect"
- **Timeline Scrubber** - "See how this looked 30 days ago"

```tsx
// Example: Interactive Price Explorer
<div className="p-6 bg-gray-900/50 rounded-xl">
  <h3>What If Silver Reaches...</h3>
  <input
    type="range"
    min={50}
    max={200}
    value={hypotheticalPrice}
    onChange={(e) => setHypotheticalPrice(e.target.value)}
    className="w-full"
  />
  <div className="text-4xl font-black">${hypotheticalPrice}</div>
  <div className="grid grid-cols-3 gap-4 mt-4">
    <div className="text-center">
      <div className="text-red-400 text-2xl font-bold">
        ${calculateLoss(hypotheticalPrice)}B
      </div>
      <div className="text-xs text-gray-500">Total Bank Losses</div>
    </div>
    {/* More impact stats */}
  </div>
</div>
```

---

### 3. ADD PERSONALIZED ALERTS & WATCHLIST
**Impact: High | Effort: Medium**

Give users a reason to return by letting them set personal triggers.

**Current Problem:** No way to be notified when something important happens.

**Solutions:**
- **Price Alerts** - "Alert me when silver hits $100"
- **Bank Watchlist** - "Notify me if JPMorgan status changes"
- **Crack Alerts** - "Alert me when any Tier 1 indicator breaks"
- **Push notifications** or **email alerts** (requires backend)

```tsx
// Example: Alert Setup Modal
<AlertSetupModal>
  <h3>Set Price Alert</h3>
  <input placeholder="Alert when silver reaches $" />
  <select>
    <option>Above</option>
    <option>Below</option>
  </select>
  <button className="btn-primary">
    <Bell className="w-4 h-4" />
    Create Alert
  </button>
</AlertSetupModal>
```

---

### 4. ADD HISTORICAL CHARTS & TRENDS
**Impact: High | Effort: Medium**

Show users the trajectory, not just the snapshot.

**Current Problem:** Only current values shown - no context of change over time.

**Solutions:**
- **7-day/30-day/90-day silver price chart** with crisis overlay
- **Bank exposure trend lines** - Are losses growing or shrinking?
- **Crack indicator history** - When did each indicator flip?
- **Crisis probability over time** - Line chart of gauge history

```tsx
// Example: Mini Sparkline in Stat Cards
<div className="stat-box">
  <div className="text-4xl font-black">$95.02</div>
  <Sparkline
    data={last30DaysPrices}
    color={silverChange >= 0 ? 'green' : 'red'}
    height={40}
  />
  <div className="text-xs text-gray-500">30-day trend</div>
</div>
```

---

### 5. ADD SOCIAL PROOF & COMMUNITY
**Impact: Medium | Effort: Medium**

Make users feel part of something bigger.

**Current Problem:** Feels like looking at data alone in the dark.

**Solutions:**
- **Live viewer count** - "1,247 watching right now"
- **Community predictions** - "68% of users predict crisis within 90 days"
- **Share milestones** - "You're one of the first 10,000 to see this"
- **Recent shares** - "John from Texas just shared this dashboard"

```tsx
// Example: Community Pulse
<div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
  <h4 className="text-sm text-gray-400 uppercase tracking-wider mb-3">
    Community Pulse
  </h4>
  <div className="flex items-center justify-between mb-4">
    <div>
      <div className="text-3xl font-black text-amber-400">68%</div>
      <div className="text-xs text-gray-500">predict crisis within 90 days</div>
    </div>
    <button className="btn-sm">Vote</button>
  </div>
  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
    <div className="h-full bg-amber-500" style={{ width: '68%' }} />
  </div>
</div>
```

---

### 6. ADD COLLAPSIBLE/EXPANDABLE SECTIONS
**Impact: Medium | Effort: Low**

Reduce scroll fatigue and let users focus on what matters.

**Current Problem:** All 4 narrative sections are always expanded - overwhelming.

**Solutions:**
- **Accordion-style sections** - Click to expand/collapse
- **"Jump to" navigation** - Quick links to each section
- **Sticky section indicator** - Show which section you're in
- **"Show only active" toggle** - Hide stable/low-risk items

```tsx
// Example: Collapsible Section
<NarrativeSection
  id="exposure"
  title="THE EXPOSURE"
  defaultExpanded={false}
  onToggle={(expanded) => trackSection(expanded)}
>
  {/* Section content */}
</NarrativeSection>
```

---

### 7. ADD GAMIFICATION ELEMENTS
**Impact: Medium | Effort: Medium**

Reward users for engagement to build habit loops.

**Current Problem:** No incentive to return or engage deeply.

**Solutions:**
- **Daily check-in streak** - "5-day streak - don't break it!"
- **Prediction badges** - "You correctly predicted silver $75!"
- **Early alert badges** - "You were in the first 1% to see this alert"
- **Share achievements** - "Your shares have reached 500 people"

```tsx
// Example: Achievement Toast
<Toast>
  <Trophy className="w-6 h-6 text-amber-400" />
  <div>
    <div className="font-bold">Early Watcher</div>
    <div className="text-sm text-gray-400">
      You've checked fault.watch 7 days in a row!
    </div>
  </div>
</Toast>
```

---

### 8. IMPROVE MOBILE EXPERIENCE
**Impact: Medium | Effort: Medium**

Mobile users need a different, swipeable experience.

**Current Problem:** Desktop layout squeezed onto mobile.

**Solutions:**
- **Swipeable cards** for sections (Tinder-style navigation)
- **Bottom sheet modals** instead of full-screen modals
- **Floating action button** for screenshot/share
- **Pull-to-refresh** gesture

---

### 9. ADD SOUND EFFECTS (Optional)
**Impact: Low-Medium | Effort: Low**

Subtle audio cues increase immersion for engaged users.

**Solutions:**
- **Alert sound** when indicator status changes
- **Ticker click** as live ticker scrolls
- **Achievement chime** for badges
- **Toggle to enable/disable** sounds

---

### 10. ADD PERSONALIZED DASHBOARD VIEW
**Impact: Medium | Effort: High**

Let power users create their own view.

**Solutions:**
- **Drag-and-drop widgets** to rearrange
- **Save multiple layouts** (Crisis view, Quick view, etc.)
- **Widget size options** (compact, normal, expanded)
- **Custom color themes**

---

## Implementation Priority Matrix

| Recommendation | Impact | Effort | Priority |
|----------------|--------|--------|----------|
| 1. Live Urgency Indicators | High | Low | **P0 - Do First** |
| 2. What-If Scenarios | High | Medium | **P1** |
| 3. Personalized Alerts | High | Medium | **P1** |
| 4. Historical Charts | High | Medium | **P1** |
| 5. Social Proof | Medium | Medium | **P2** |
| 6. Collapsible Sections | Medium | Low | **P2** |
| 7. Gamification | Medium | Medium | **P3** |
| 8. Mobile UX | Medium | Medium | **P3** |
| 9. Sound Effects | Low | Low | **P4** |
| 10. Personalized Dashboard | Medium | High | **P4** |

---

## Quick Wins (Can Do Today)

1. **Add live viewer count** (even if simulated initially)
2. **Add "Since your arrival" change indicator**
3. **Add collapsible section toggles**
4. **Add section jump navigation**
5. **Add sparkline mini-charts in stat boxes**
6. **Add countdown timers with projections**

---

## Metrics to Track

After implementing changes, measure:

| Metric | Target | Why |
|--------|--------|-----|
| Time on Site | +50% | More engagement = more time |
| Return Visits | +100% | Alerts/streaks drive returns |
| Shares | +200% | Interactive features are more shareable |
| Section Expansion | 80%+ | Users exploring more content |
| Alert Sign-ups | 10%+ conversion | Users want to be notified |

---

## Conclusion

The visual foundation is strong. The site looks dramatic and professional. But without **interactivity, personalization, and reasons to return**, users will view it once and forget about it.

**The #1 priority is making users feel like they're watching something LIVE and URGENT.** Add real-time counters, live viewer counts, and change indicators. Then layer in interactive scenarios and alerts to create habit loops.

The goal: Turn passive viewers into engaged monitors who check fault.watch daily.
