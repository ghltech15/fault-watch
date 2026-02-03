# Claude Code Instructions for fault.watch

## Session Startup Protocol

**ALWAYS** at the start of every session:

1. Run `/gsd:progress` to check current project status
2. Review the checklist below to see where we left off
3. Update the checklist as work progresses

## Session Checklist

Use this to track progress across sessions. Update after completing work.

### Current Status
- **Last Session**: 2026-02-03
- **Current Phase**: Phase 02 - Content Export Engine (COMPLETE - 3/3 plans)
- **Next Up**: Phase 03 - Auto-Clip Generator (needs planning)
- **Note**: Return to `/gsd:plan-phase 3` after hourly parameter search implementation

### Parallel Work (Non-GSD)
- **Hourly Parameter Search System**: IMPLEMENTED (2026-02-03)
  - SQL schema: `supabase_parameter_search_schema.sql`
  - API route: `frontend/app/api/hourly-parameter-search/route.ts`
  - Cron worker: `frontend/scripts/hourly-cron.ts`
  - Docs: `docs/HOURLY_PARAMETER_SEARCH.md`
  - **Deployment TODO**: Run schema SQL, set secrets, deploy to Fly.io

### Quick Reference
- Project: fault.watch UI Redesign & TikTok Content Engine
- Planning docs: `.planning/`
- Phase plans: `.planning/phases/`

### Before Ending Any Session
1. Update "Last Session" date above
2. Update "Current Phase" and "Current Task"
3. Run `/gsd:pause-work` if stopping mid-phase
4. Commit any changes

## GSD Commands Reference
- `/gsd:progress` - Check status and next action
- `/gsd:resume-work` - Resume from previous session
- `/gsd:execute-plan` - Execute current phase plan
- `/gsd:pause-work` - Create handoff when pausing
- `/gsd:help` - See all commands
