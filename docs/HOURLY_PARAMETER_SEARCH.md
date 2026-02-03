# Fault.Watch Hourly Parameter Search System

Automated system that runs every hour (05:00-22:00 EST) to execute configured searches across 5 parameter sheets and persist results to Supabase.

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────────┐     ┌──────────────┐
│  Fly.io Cron    │────▶│  Next.js API Route   │────▶│   Supabase   │
│  (hourly UTC)   │     │  /api/hourly-param-  │     │   Database   │
│                 │     │  search              │     │              │
└─────────────────┘     └──────────────────────┘     └──────────────┘
                                  │
                                  ▼
                        ┌──────────────────────┐
                        │  Fly.io Backend API  │
                        │  (FastAPI collectors)│
                        └──────────────────────┘
```

## Components

### 1. Supabase Tables

Run `supabase_parameter_search_schema.sql` in your Supabase SQL Editor:

- **fault_watch_parameters_sheet1** - Regulators & Official Filings (SEC, FDIC, OCC, Fed)
- **fault_watch_parameters_sheet2** - News, Research, and RSS
- **fault_watch_parameters_sheet3** - Social Media & Sentiment (Reddit, Twitter)
- **fault_watch_parameters_sheet4** - Market Structure & Data Feeds (COMEX, LBMA, Fed repo)
- **fault_watch_parameters_sheet5** - Price/Alert Triggers

Supporting tables:
- **fault_watch_parameter_runs** - Run metadata and status
- **fault_watch_parameter_results** - Per-parameter results per run

### 2. Next.js API Route

`/api/hourly-parameter-search` (POST)

- Validates EST window (05:00-22:00)
- Iterates through enabled parameters in all 5 sheets
- Calls backend APIs for each search type
- Persists results to Supabase
- Returns JSON run payload

### 3. Fly.io Cron Process

The `cron` process defined in `fly.toml` runs the hourly worker:
- Executes every hour (UTC time)
- Calls the API endpoint with service role auth
- Logs results to stdout (visible in Fly logs)

## Configuration

### Environment Variables

Set these via `fly secrets set`:

```bash
# Required: Supabase service role key
fly secrets set SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Optional: Separate API key for the cron worker (defaults to service role key)
fly secrets set HOURLY_SEARCH_API_KEY=your_api_key
```

Already set in fly.toml:
- `HOURLY_SEARCH_API_URL` - URL of the API endpoint

### Parameter Sheet Configuration

Each parameter row has these common fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | text | Short label for the search |
| `description` | text | Detailed description |
| `is_enabled` | boolean | Whether to run this search |
| `priority` | int (1-5) | Processing order (1 = highest) |
| `search_query` | text | Base search query |
| `keywords` | text[] | Keywords to match |
| `sources` | text[] | Data sources to query |
| `search_type` | enum | `regulatory_filings`, `news`, `social`, `market_data`, `price_trigger` |
| `max_results_per_run` | int | Limit results per run |
| `max_runs_per_day` | int | Skip after N runs per day |
| `cooldown_minutes` | int | Minimum time between runs |
| `severity_level` | enum | `info`, `watch`, `warning`, `critical` |

Sheet-specific fields are documented in the schema file.

## Deployment

### 1. Apply Database Schema

```bash
# Copy schema to clipboard and paste into Supabase SQL Editor
# Or use Supabase CLI:
supabase db push --db-url postgresql://...
```

### 2. Set Secrets

```bash
cd frontend
fly secrets set SUPABASE_SERVICE_ROLE_KEY=your_key
```

### 3. Deploy

```bash
fly deploy
```

### 4. Scale Cron Process

By default, Fly.io will run one instance of each process. To ensure the cron worker runs:

```bash
# Check process status
fly status

# Scale cron process (usually 1 is enough)
fly scale count cron=1 app=1
```

## Monitoring

### View Logs

```bash
# All logs
fly logs

# Cron process only
fly logs --process cron
```

### Check Run Status

```sql
-- Latest run
SELECT * FROM fault_watch_latest_run;

-- Last 24 hours stats
SELECT * FROM fault_watch_run_stats_24h;

-- Recent runs
SELECT run_id, status, run_started_at_utc, total_new_items, total_errors
FROM fault_watch_parameter_runs
ORDER BY run_started_at_utc DESC
LIMIT 10;
```

### API Health Check

```bash
curl https://fault-watch-ui.fly.dev/api/hourly-parameter-search
```

Returns:
```json
{
  "status": "ok",
  "service": "hourly-parameter-search",
  "timestamp": "2026-02-03T10:00:00.000Z",
  "est_time": "2026-02-03T05:00:00.000Z",
  "within_active_window": true,
  "active_window": "05:00-22:00 EST"
}
```

## Local Development

### Run API Server

```bash
cd frontend
npm run dev
```

### Test API Endpoint

```bash
curl -X POST http://localhost:3000/api/hourly-parameter-search \
  -H "Content-Type: application/json" \
  -d '{"mode": "hourly_parameter_search"}'
```

### Run Cron Worker Locally

```bash
cd frontend
npm run cron:test
```

## Run Payload Format

```json
{
  "run_id": "uuid",
  "status": "completed",
  "run_started_at_utc": "2026-02-03T10:00:00Z",
  "run_completed_at_utc": "2026-02-03T10:02:15Z",
  "est_hour_start": "2026-02-03T05:00:00-05:00",
  "est_hour_end": "2026-02-03T06:00:00-05:00",
  "sheets": [
    {
      "sheet_number": 1,
      "rows_processed": 4,
      "new_items": 7,
      "updated_items": 0,
      "skipped_rows": 0,
      "errors": 0,
      "notes": null
    }
  ]
}
```

## Troubleshooting

### "Outside EST active window"

Normal behavior. The cron runs 24/7 UTC but the API only executes searches during 05:00-22:00 EST.

### "Failed to initialize database connection"

Check that `SUPABASE_SERVICE_ROLE_KEY` is set:
```bash
fly secrets list
```

### "Backend API error"

The backend FastAPI server may be down. Check:
```bash
curl https://fault-watch-api.fly.dev/api/dashboard
```

### Parameter Not Running

1. Check `is_enabled = true`
2. Check `cooldown_minutes` hasn't been exceeded
3. Check `max_runs_per_day` hasn't been exceeded
4. Check priority (lower number = higher priority)

## Adding New Parameters

Insert new rows into the appropriate sheet table:

```sql
INSERT INTO fault_watch_parameters_sheet1 (
  name, description, search_query, keywords, sources,
  filing_types, entities, priority, severity_level
) VALUES (
  'New SEC Watch',
  'Monitor new SEC filings for specific keywords',
  'SEC filing silver manipulation',
  ARRAY['silver', 'manipulation', 'enforcement'],
  ARRAY['sec'],
  ARRAY['8-K', 'Enforcement'],
  ARRAY['MS', 'JPM'],
  2,
  'warning'
);
```

## Future Enhancements

- [ ] Add email/Slack notifications for critical alerts
- [ ] Implement result diffing for better change detection
- [ ] Add retry logic for failed searches
- [ ] Support custom search intervals per parameter
- [ ] Add dashboard UI for managing parameters
