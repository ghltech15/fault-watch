# fault.watch Architecture

Event-sourcing architecture for financial crisis monitoring with truth-tier verification.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     COLLECTOR JOBS (Python)                      │
│  SEC │ CFTC │ OCC │ FDIC │ Fed │ COMEX │ Reddit │ News │ Dealers │
└──────────────────────────┬──────────────────────────────────────┘
                           │ events/claims
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EVENT STORE (Postgres)                        │
│  events │ entities │ sources │ claims │ corroborations          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ projections
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCORING ENGINE                                │
│  funding_stress │ enforcement_heat │ deliverability_stress       │
│                    composite_risk (0-10)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI + NEXT.JS UI                          │
│  Risk Dashboard │ Claims Triage │ Event Explorer                 │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
fault-watch/
├── api.py                    # FastAPI backend
├── fault_watch.py            # Core business logic
├── config/                   # Configuration files
│   ├── keywords.py           # Alert keywords
│   ├── sources.py            # Data source configs
│   └── alerts.py             # Alert thresholds
├── data/                     # Data processing modules
│   ├── prices.py             # Price monitoring
│   ├── fed.py                # Federal Reserve data
│   ├── comex.py              # COMEX inventory
│   ├── sec_monitor.py        # SEC EDGAR filings
│   ├── alerts.py             # Alert management
│   ├── credibility.py        # Credibility scoring
│   ├── database.py           # Supabase integration
│   └── aggregator.py         # Data aggregation
├── scrapers/                 # Web scrapers
│   ├── reddit_scraper.py     # Reddit/social
│   ├── news_scraper.py       # RSS/news
│   ├── dealer_scraper.py     # Physical dealers
│   └── regulatory_scraper.py # CFTC/Fed/FDIC
├── services/                 # Background services
│   └── collector/            # Data collection jobs
│       ├── runner.py         # APScheduler job runner
│       ├── fetcher.py        # HTTP fetcher with backoff
│       └── jobs/             # Individual collectors
│           ├── base.py       # Base collector class
│           ├── regulatory/   # Tier 1 collectors
│           └── claims/       # Tier 3 collectors
├── packages/                 # Shared utilities
│   └── core/                 # Core package
│       ├── trust.py          # Trust tier policy
│       ├── entities.py       # Entity resolution
│       ├── scoring/          # Risk scoring engines
│       ├── claims/           # Claim processing
│       └── indicators/       # Z-score/regime detection
├── db/                       # Database
│   ├── event_store.py        # PostgreSQL interface
│   └── migrations/           # SQL migrations
├── frontend/                 # Next.js frontend
│   ├── app/                  # App router pages
│   ├── components/           # React components
│   └── lib/                  # API client
└── docs/                     # Documentation
```

## Core Concepts

### Trust Tiers

| Tier | Sources | Creates | Description |
|------|---------|---------|-------------|
| 1 | SEC, CFTC, OCC, FDIC, Fed, Courts | Events | Official facts - highest trust |
| 2 | Reuters, Bloomberg, WSJ, FT | Events + Claims | Credible press - verified but not official |
| 3 | Reddit, Twitter, Blogs | Claims only | Unverified assertions |

### Event vs Claim

- **Event**: Verified fact from Tier 1/2 source. Immutable, append-only.
- **Claim**: Unverified assertion from Tier 3 source. Has lifecycle:
  - `new` → `triage` → `corroborating` → `confirmed`/`debunked` → `stale`

### Three-Score System

1. **Funding Stress (0-100)**: Credit spreads, TED spread, rate dislocations, facility usage
2. **Enforcement Heat (0-100)**: Regulatory actions, multi-agency coordination, tempo
3. **Deliverability Stress (0-100)**: COMEX metrics, dealer tightness, delivery velocity

### Composite Risk (0-10)

Weighted combination of three scores with cascade detection:
- 2-of-3 high scores (≥50) → cascade triggered
- Extreme score (≥70) + another high → amplified

Risk labels:
- 0-1.5: STABLE (green)
- 1.5-2.5: MONITOR (blue)
- 2.5-4: WATCH (yellow)
- 4-6: WARNING (orange)
- 6-8: DANGER (red)
- 8-10: CRISIS (darkred)

## Database Schema

### entities
Master table for tracked entities (banks, regulators, metals, exchanges).

### sources
Data sources with trust tier classification.

### events
Append-only event store for verified facts.

### claims
Unverified assertions with lifecycle tracking.

### corroborations
Links claims to confirming events.

### scores_daily
Computed risk scores per entity per day.

### scores_market
Aggregate market-wide risk scores.

## API Endpoints

### Dashboard
- `GET /api/dashboard` - Full dashboard data
- `GET /api/prices` - Current prices
- `GET /api/alerts` - Active alerts

### Pipeline
- `GET /api/pipeline/status` - Pipeline health
- `GET /api/pipeline/stress` - Stress indicators
- `GET /api/pipeline/sec` - SEC filings
- `GET /api/pipeline/alerts` - Pipeline alerts
- `GET /api/pipeline/social` - Social data
- `GET /api/pipeline/news` - News data
- `GET /api/pipeline/dealers` - Dealer data
- `GET /api/pipeline/regulatory` - Regulatory data

### Events (new)
- `GET /api/events` - Query events
- `GET /api/events/{id}` - Get event by ID

### Claims (new)
- `GET /api/claims` - Query claims
- `GET /api/claims/triage` - Claims awaiting triage
- `PATCH /api/claims/{id}` - Update claim status

### Scores (new)
- `GET /api/scores/latest` - Latest scores
- `GET /api/scores/entity/{id}` - Entity score history
- `GET /api/scores/market` - Market-wide scores

## Local Development

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Run migrations
psql $DATABASE_URL -f db/migrations/001_entities.sql
psql $DATABASE_URL -f db/migrations/002_sources.sql
psql $DATABASE_URL -f db/migrations/003_events.sql
psql $DATABASE_URL -f db/migrations/004_claims.sql
psql $DATABASE_URL -f db/migrations/005_scores.sql

# Start API
uvicorn api:app --reload

# Start collector (optional)
python -m services.collector.runner

# Start frontend
cd frontend && npm run dev
```

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/faultwatch_events

# Existing Supabase (auth/user data)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx

# API Keys
FRED_API_KEY=xxx
FINNHUB_API_KEY=xxx
SEC_USER_AGENT="FaultWatch/2.0 (contact@fault.watch)"

# Reddit (optional)
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
```
