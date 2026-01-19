# fault.watch v0.dev Prompt

> Copy everything below this line and paste into v0.dev

---

Create a real-time financial crisis monitoring dashboard called "fault.watch" with these specifications:

## Design System

### Theme
- Mode: Dark mode only
- Background: #0d0d0d (deep black)
- Surface: #141414 (cards, elevated surfaces)
- Border: #2a2a2a (subtle borders)

### Accent Colors
- Primary/Danger: #e31837 (crisis red) - alerts, critical states
- Warning: #ffc300 (amber) - elevated states, approaching thresholds
- Success: #4ade80 (green) - stable states, positive changes
- Info: #0066cc (blue) - neutral information, Fed data

### Typography
- Font: Inter or system sans-serif
- Hero numbers: 96-120px, font-weight 900, tabular-nums
- Headings: 24-32px, font-weight 700, uppercase, letter-spacing 1px
- Body: 16px, font-weight 400, #e0e0e0
- Captions: 13px, #a0a0a0, uppercase, letter-spacing 2px
- Monospace: For prices, percentages, countdowns

### Spacing
- Base unit: 4px
- Card padding: 20px
- Grid gap: 16px
- Section margin: 24px

## Layout Structure

### Header Bar (sticky, 60px height)
- Left: Logo "fault.watch" in white, font-weight 900
- Center: Empty (or alert message when critical)
- Right: Dual countdown timers side-by-side
  - "LLOYD'S: 20d 14h 32m"
  - "SEC: 34d 16h 25m"
  - Amber when <14 days, red when <7 days, pulse when <3 days
- Far right: "Updated 12s ago" in gray caption text

### Hero Section (centered, 200px height)
- Massive risk index number: 120px font, centered
- Number has colored glow/shadow effect matching its severity
- Color logic: green (#4ade80) if <4, amber (#ffc300) if 4-7, red (#e31837) if >7
- Below number: "SYSTEMIC RISK INDEX" in uppercase caption
- Below that: Badge showing "CRITICAL" / "ELEVATED" / "STABLE" with matching color

### Alert Banner (conditional, below hero)
- Only shows when alerts exist
- Full-width red (#e31837) background with 0.9 opacity
- White text: "[BREAKING]" label + alert message
- Subtle pulse animation
- X button to dismiss (but reappears on new alert)

### Main Card Grid
- Desktop (>1024px): 3 columns, 2 rows
- Tablet (768-1024px): 2 columns, 3 rows
- Mobile (<768px): 1 column, stacked

## Card Definitions

### Card 1: Live Prices
- Header: "LIVE PRICES" with pulse dot indicator
- Data source: GET /api/prices
- Layout:
  - Silver price HUGE (48px) with change badge (+6.8% in green or red)
  - Below: 2x2 grid of smaller prices:
    - Gold: $4,596 (+2.4%)
    - VIX: 14.5 (-6.2%)
    - MS Stock: $135 (-0.2%)
    - Gold/Silver Ratio: 54.6
  - Each has mini sparkline (last 5 data points)
- Click action: Expands to full price table with all 20+ assets
- Refresh: Every 60 seconds, flash green/red on change

### Card 2: Bank Exposure
- Header: "BANK EXPOSURE" with danger icon
- Data source: GET /api/banks
- Layout:
  - Top 3 banks listed vertically:
    1. Citigroup - $343B loss - red progress bar at 196% of equity
    2. Morgan Stanley - $319B loss - red progress bar at 319% of equity
    3. JPMorgan - +$40B gain - green (they're LONG)
  - Each row: Bank name | Paper Loss | Visual bar
  - "INSOLVENT" badge appears when loss > equity
- Click action: Slide-over panel showing all 10 banks with full details
- Each bank row in expanded view shows:
  - Current stock price + daily change
  - Position (SHORT/LONG) + ounces
  - PM derivatives exposure
  - Insolvency price threshold

### Card 3: Scenario Calculator
- Header: "SCENARIO ANALYSIS"
- Data source: GET /api/scenarios/{price}
- Layout:
  - Large slider: Silver price $30 - $200
  - Current position marker on slider
  - Below slider, updating in real-time as slider moves:
    - MS Loss: $413B (with "INSOLVENT" badge if applicable)
    - Citi Loss: $443B (with "INSOLVENT" badge if applicable)
    - JPM Gain: $52B
    - Total Short Loss: $856B
    - Fed Coverage: 5.9% (progress bar, red when <20%)
- Preset buttons: $50 | $75 | $100 | $150 | $200
- Animate number changes with count-up effect

### Card 4: Domino Cascade
- Header: "DOMINO EFFECT"
- Data source: GET /api/dominoes
- Layout:
  - 5 connected boxes in horizontal chain (vertical on mobile)
  - Each box is a "domino" with:
    - Icon representing the factor
    - Label (MS Stock, Silver, Citi, Regional Banks, VIX)
    - Status badge (STABLE/WARNING/CRITICAL)
    - Current value
  - Connecting lines between boxes
  - Lines glow/pulse when domino status changes
  - Color coding: Green stable, amber warning, red critical
- Visual: When one domino goes critical, animate a "falling" effect to the next

### Card 5: Active Alerts
- Header: "ALERTS" with count badge (e.g., "3")
- Data source: GET /api/alerts
- Layout:
  - Scrollable list of alert items
  - Each alert:
    - Severity icon (red ! for critical, amber ! for warning)
    - Title in bold
    - Detail text in gray
    - Action text in blue (clickable)
  - Critical alerts have subtle red background
  - Empty state: Green checkmark "No active alerts"
- Click action: Expands to full alert management view

### Card 6: Content Studio
- Header: "TIKTOK CONTENT"
- Data source: GET /api/content/files, POST /api/content/generate/daily
- Layout:
  - Preview thumbnail of last generated image (if exists)
  - Two prominent buttons:
    - "Generate Daily Summary" (primary, red)
    - "Generate Price Alert" (secondary, outlined)
  - Toggle switch: "Video mode" (on/off)
  - Recent files list (last 3) with download icons
- Click action: Full content management panel with all templates

## Shared Components

### CountdownTimer
- Props: deadline (ISO string), label (string), warningDays (number), criticalDays (number)
- Display: "20d 14h 32m" format
- Color changes at thresholds
- Pulse animation when critical

### RiskGauge
- Props: value (0-10), size ("sm" | "md" | "lg")
- Circular or semi-circular gauge
- Needle pointing to current value
- Color segments: green (0-4), amber (4-7), red (7-10)
- Glow effect on needle

### PriceDisplay
- Props: value (number), change (number), label (string), size ("sm" | "md" | "lg")
- Formats number with $ and commas
- Change shown as badge with arrow (up green, down red)
- Optional sparkline

### StatusBadge
- Props: status (string), variant ("critical" | "warning" | "stable" | "info")
- Rounded pill shape
- Color matches variant
- Pulse animation for critical

### BankRiskBar
- Props: loss (number), equity (number), name (string)
- Horizontal progress bar
- Red fill, shows percentage
- "INSOLVENT" badge when >100%

## Data Integration

### API Endpoints
| Endpoint | Method | Component | Refresh |
|----------|--------|-----------|---------|
| /api/dashboard | GET | All cards initial load | 60s |
| /api/prices | GET | Live Prices card | 60s |
| /api/prices/{asset} | GET | Price detail | On demand |
| /api/countdowns | GET | Header timers | 60s |
| /api/alerts | GET | Alerts card | 30s |
| /api/banks | GET | Bank Exposure card | 60s |
| /api/banks/{ticker} | GET | Bank detail panel | On demand |
| /api/scenarios | GET | Scenario presets | On demand |
| /api/scenarios/{price} | GET | Scenario calculator | On slider change |
| /api/dominoes | GET | Domino Cascade | 60s |
| /api/content/generate/daily | POST | Content Studio | On click |
| /api/content/files | GET | Content Studio list | On mount |

### Base URL Configuration
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

### React Query Setup
- staleTime: 30000 (30 seconds)
- refetchInterval: 60000 for dashboard data
- refetchOnWindowFocus: true

## Animations

### Entry Animations
- Cards: Fade in + slide up, staggered 100ms each
- Hero number: Scale from 0.8 to 1.0 + count up from 0
- Duration: 500ms
- Easing: ease-out

### Number Animations
- All prices/values count up on initial load
- Duration: 1000ms for hero, 500ms for cards
- Use framer-motion's useSpring or useMotionValue

### Status Transitions
- Color changes: 300ms transition
- Badge appears: Scale + fade in
- Alert banner: Slide down from top

### Interactions
- Card hover: Subtle lift (translateY -2px) + shadow increase
- Button hover: Background lighten
- Clickable items: Scale 0.98 on press

### Loading States
- Skeleton loaders matching content shape
- Subtle shimmer animation
- Use Shadcn Skeleton component

## Responsive Behavior

### Desktop (>1024px)
- Full 3-column grid
- Expanded header with all elements
- Side panels for detail views

### Tablet (768-1024px)
- 2-column grid
- Countdown timers stack vertically in header
- Detail views as modals

### Mobile (<768px)
- Single column stack
- Sticky header with hamburger menu
- Bottom nav for quick section access
- Full-screen detail views
- Swipe gestures for cards (optional)

## Tech Stack
- Framework: Next.js 14 App Router
- Components: Shadcn/ui (Card, Badge, Button, Slider, Sheet, Dialog)
- Styling: Tailwind CSS
- Animations: Framer Motion
- Charts: Recharts (for sparklines)
- Data: React Query or SWR
- Icons: Lucide React

## Additional Requirements

1. All numbers should use tabular-nums font-feature for alignment
2. Prices should show 2 decimal places, percentages 1 decimal
3. Large numbers should use abbreviations (e.g., $343B not $343,000,000,000)
4. Times should be relative ("Updated 12s ago") with auto-refresh
5. Error states should show retry buttons
6. Empty states should have helpful messages

Generate the main dashboard page showing all 6 cards, the hero section with risk gauge, the header with countdowns, and the conditional alert banner. Include the expanded Bank Exposure slide-over panel as a secondary view.
