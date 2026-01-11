# STACK.md
> Technology stack and dependencies for fault-watch

**Last Updated:** 2026-01-11

---

## Languages

**Primary:**
- Python 3.11 - All application code (`fault_watch.py`)

**Secondary:**
- SQL - Database schema (`supabase_schema.sql`)
- TOML - Deployment config (`fly.toml`)

---

## Runtime

- **Python:** 3.11 (specified in `Dockerfile`)
- **Container:** Docker with python:3.11-slim base image
- **Production Server:** Gunicorn (in `requirements.txt`, not actively used - Streamlit handles serving)

---

## Frameworks

| Framework | Version | Purpose | Config File |
|-----------|---------|---------|-------------|
| Streamlit | 1.40.0 | Web dashboard framework | `fault_watch.py` |
| Plotly | 5.18.0 | Interactive charts | `fault_watch.py` |
| Pandas | 2.2.0 | Data manipulation | `fault_watch.py` |
| NumPy | 1.26.3 | Numerical operations | `fault_watch.py` |

---

## Dependencies

**Core (`requirements.txt`):**
```
streamlit==1.40.0      # Web framework
pandas==2.2.0          # Data processing
numpy==1.26.3          # Numerical ops
yfinance==0.2.36       # Stock data
requests==2.31.0       # HTTP client
plotly==5.18.0         # Charts
supabase==2.3.4        # Database client
python-dotenv==1.0.0   # Environment vars
gunicorn==21.2.0       # WSGI server
```

---

## Configuration

| Config | Location | Purpose |
|--------|----------|---------|
| Environment | `.env` (gitignored) | Supabase credentials |
| Deployment | `fly.toml` | Fly.io hosting config |
| Container | `Dockerfile` | Production container |
| Streamlit | Environment vars in `fly.toml` | Theme, headless mode |

**Environment Variables:**
- `SUPABASE_URL` - Database endpoint
- `SUPABASE_KEY` - Anonymous API key
- `STREAMLIT_THEME_BASE` - "dark"
- `STREAMLIT_THEME_PRIMARY_COLOR` - "#ff3b5c"

---

## Platform

| Layer | Service |
|-------|---------|
| Hosting | Fly.io (San Jose region) |
| Database | Supabase (PostgreSQL) |
| Container | Docker |
| CI/CD | GitHub Actions |
