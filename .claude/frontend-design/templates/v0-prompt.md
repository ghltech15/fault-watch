# v0.dev Prompt Template

Use this template to generate v0.dev prompts from API analysis.

---

## Template Structure

```
Create a [PROJECT_TYPE] dashboard called "[PROJECT_NAME]" with these specifications:

## Design System

### Theme
- Mode: [dark/light/system]
- Background: [HEX_COLOR] ([COLOR_NAME])
- Primary accent: [HEX_COLOR] ([PURPOSE])
- Secondary accent: [HEX_COLOR] ([PURPOSE])
- Success: [HEX_COLOR]
- Warning: [HEX_COLOR]
- Danger: [HEX_COLOR]

### Typography
- Font family: [FONT_STACK]
- Hero numbers: [SIZE]px, [WEIGHT], [STYLE]
- Headings: [SIZE]px, [WEIGHT]
- Body: [SIZE]px
- Captions: [SIZE]px, [COLOR]
- Monospace for: [DATA_TYPES]

### Spacing
- Base unit: [N]px
- Card padding: [N]px
- Grid gap: [N]px
- Section margin: [N]px

## Layout Structure

### Header (sticky)
[HEADER_COMPONENTS]

### Hero Section
[HERO_COMPONENTS]

### Alert Banner (conditional)
[ALERT_BEHAVIOR]

### Main Content Grid
- Desktop: [COLUMNS] columns
- Tablet: [COLUMNS] columns
- Mobile: [COLUMNS] column

[CARD_DEFINITIONS]

## Components

### Card: [CARD_NAME]
- Purpose: [DESCRIPTION]
- Data source: [API_ENDPOINT]
- Primary display: [FIELD_NAME] as [DISPLAY_TYPE]
- Secondary info: [FIELD_LIST]
- Status indicator: [FIELD] shows [STATES]
- Click action: [EXPAND_BEHAVIOR]

[REPEAT FOR EACH CARD]

### Shared Components

#### [COMPONENT_NAME]
- Props: [PROP_LIST]
- States: [STATE_LIST]
- Behavior: [DESCRIPTION]

[REPEAT FOR EACH SHARED COMPONENT]

## Data Integration

### API Endpoints
| Endpoint | Method | Component | Refresh |
|----------|--------|-----------|---------|
[ENDPOINT_TABLE]

### Loading States
- Initial load: [SKELETON_TYPE]
- Refresh: [INDICATOR_TYPE]
- Error: [ERROR_DISPLAY]

### Data Mapping
[ENDPOINT_TO_COMPONENT_MAPPING]

## Animations

### Entry
- Cards: [ANIMATION_TYPE] with [TIMING]
- Stagger: [DELAY]ms between items

### Numbers
- Count up from 0 on load
- Duration: [MS]ms
- Easing: [EASING_FUNCTION]

### Transitions
- View changes: [TRANSITION_TYPE]
- Status changes: [COLOR_TRANSITION]
- Hover effects: [EFFECT_TYPE]

## Responsive Behavior

### Breakpoints
- Desktop: >[WIDTH]px
- Tablet: [WIDTH]-[WIDTH]px
- Mobile: <[WIDTH]px

### Mobile Adaptations
[MOBILE_SPECIFIC_CHANGES]

## Tech Stack
- Framework: Next.js 14 App Router
- Components: Shadcn/ui
- Styling: Tailwind CSS
- Animations: Framer Motion
- Charts: Recharts
- Data fetching: React Query / SWR

Generate the main dashboard page with all cards visible, plus expanded detail views for clickable cards.
```

---

## Field Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `[PROJECT_TYPE]` | Type of dashboard | "financial monitoring", "analytics", "admin" |
| `[PROJECT_NAME]` | App name | "fault.watch", "DataHub" |
| `[HEX_COLOR]` | Color in hex | "#0d0d0d", "#e31837" |
| `[API_ENDPOINT]` | Full endpoint path | "GET /api/dashboard" |
| `[FIELD_NAME]` | Data field name | "risk_index", "price" |
| `[DISPLAY_TYPE]` | How to show data | "large number", "badge", "chart" |
| `[ANIMATION_TYPE]` | Animation name | "fade-in", "slide-up", "scale" |

---

## Component Patterns

### Hero Metric
```
Large centered number ([SIZE]px+)
Colored glow effect when [CONDITION]
Label below: "[LABEL_TEXT]"
Subtitle badge showing status
```

### Data Card
```
Header with icon and title
Primary metric prominently displayed
Secondary metrics in smaller text
Status indicator (colored dot/badge)
Trend indicator (up/down arrow with %)
Click to expand for details
```

### Countdown Timer
```
Format: [Dd] [Hh] [Mm] [Ss]
Color changes: [THRESHOLDS]
Pulse animation when urgent
Label showing deadline name
```

### Alert Banner
```
Full-width, colored background
Icon + message text
Dismiss button (optional)
Auto-show on condition: [CONDITION]
```

### Status Badge
```
Rounded pill shape
Background color by status
Text: [STATUS_TEXT]
Optional pulse for critical
```

---

## Example: Financial Dashboard

```
Create a real-time financial crisis monitoring dashboard called "fault.watch" with these specifications:

## Design System
- Theme: Dark mode only, deep black (#0d0d0d) background
- Primary accent: Crisis red (#e31837)
- Secondary: Warning amber (#ffc300)
- Success: Stable green (#4ade80)
- Typography: Bold, news-style headlines, monospace for numbers
- Style: CNN/Bloomberg breaking news aesthetic

## Layout Structure

### Header Bar (sticky)
- Logo "fault.watch" left-aligned, white text
- Dual countdown timers right-aligned
- Last updated timestamp, subtle gray

### Hero Section
- Massive centered risk index number (0-10 scale)
- Number size: 120px+, with colored glow effect
- Color changes: green (<4), amber (4-7), red (>7)
- Label below: "SYSTEMIC RISK INDEX"

### Main Card Grid (2x3 on desktop, 1 column mobile)

**Card 1: Live Prices**
- Data source: GET /api/prices
- Silver price HUGE with % change
- Gold, VIX, MS stock smaller below
- Click → full price table

**Card 2: Bank Exposure**
- Data source: GET /api/banks
- Top 3 at-risk banks with risk bars
- Paper loss amounts in billions
- Click → full bank analysis

[Continue for all cards...]

## Tech Stack
- Next.js 14 App Router
- Shadcn/ui components
- Tailwind CSS
- Framer Motion for animations
- Recharts for sparklines
- React Query for data fetching

Generate the main dashboard page with all cards visible.
```
