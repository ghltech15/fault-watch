# STRUCTURE.md
> Directory layout and organization for fault-watch

**Last Updated:** 2026-01-11

---

## Directory Layout

```
fault-watch/
├── .claude/                    # Claude Code configuration
│   ├── commands/gsd/           # GSD slash commands
│   └── get-shit-done/          # GSD system files
├── .git/                       # Git repository
├── .github/                    # GitHub Actions (referenced in README)
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── .planning/                  # GSD planning documents
│   └── codebase/               # This codebase analysis
├── fault-watch-production/     # Production build artifacts
├── venv/                       # Python virtual environment
│
├── fault_watch.py              # MAIN APPLICATION (54KB, 1269 lines)
├── fault_watch_v2.py           # Previous version (22KB)
├── fault_watch_v3.py           # Previous version (45KB)
├── fault_watch_v4.py           # Duplicate of current (54KB)
│
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── fly.toml                    # Fly.io deployment config
├── supabase_schema.sql         # Database schema
│
├── README.md                   # Project documentation
├── SETUP_GUIDE.md              # Detailed setup instructions
├── ms_collapse_analysis.md     # Analysis document
│
├── .dockerignore               # Docker ignore rules
├── .env                        # Environment variables (gitignored)
└── .env.example                # Environment template
```

---

## Key Locations

| Purpose | Location |
|---------|----------|
| Main App | `fault_watch.py` |
| Dependencies | `requirements.txt` |
| Database Schema | `supabase_schema.sql` |
| Deployment | `Dockerfile`, `fly.toml` |
| Documentation | `README.md`, `SETUP_GUIDE.md` |

---

## Organization Notes

**Single-File Application:**
The entire application logic is in `fault_watch.py`. No src/, lib/, or component directories.

**Version Files:**
Multiple versions exist (`v2`, `v3`, `v4`) - these appear to be development iterations. `fault_watch.py` is the active version (identical to `v4`).

**No Test Directory:**
No `tests/`, `__tests__/`, or `*_test.py` files detected.

**No Configuration Directory:**
Configuration is inline in `fault_watch.py` as Python constants.

---

## File Purposes

| File | Lines | Purpose |
|------|-------|---------|
| `fault_watch.py` | 1269 | Main Streamlit dashboard |
| `supabase_schema.sql` | 257 | Database tables, RLS, functions |
| `requirements.txt` | 28 | Python package dependencies |
| `Dockerfile` | 38 | Production container |
| `fly.toml` | 33 | Fly.io hosting config |
| `README.md` | 222 | User documentation |
