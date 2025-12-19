# FPL Data Management

## Important: Check for Updates Every Session

**Every time you start working on this project, run the gameweek update script:**

```bash
python3 scripts/fetch_fpl_gameweeks.py
```

This ensures we have the latest gameweek deadlines. The Premier League occasionally reschedules matches which affects gameweek deadlines.

## Data Sources

### Official FPL API
- Base URL: `https://fantasy.premierleague.com/api/`
- Bootstrap endpoint: `bootstrap-static/` - Contains all gameweeks, teams, players
- No authentication required for read-only access

### Useful Endpoints
- `/api/bootstrap-static/` - All static data (gameweeks, players, teams)
- `/api/entry/{team_id}/` - Manager's team info
- `/api/entry/{team_id}/event/{gw}/picks/` - Manager's picks for a gameweek
- `/api/entry/{team_id}/history/` - Manager's full history
- `/api/leagues-classic/{league_id}/standings/` - League standings

## Database Schema

### gameweeks table
Stores the FPL gameweek schedule:
- `id` - Gameweek number (1-38)
- `name` - "Gameweek 1", etc.
- `deadline_time` - ISO datetime when transfers lock
- `finished` - Whether all matches are complete
- `is_current` / `is_next` - Current state
- `last_updated` - When we last synced from API

## Key Dates to Track

For each gameweek we need to know:
1. **Deadline** - When transfers lock (for pre-GW messages)
2. **When finished** - All matches complete (for post-GW score updates)

## Checking for Changes

Signs that gameweeks may have been rescheduled:
- Blank gameweeks (some teams don't play)
- Double gameweeks (some teams play twice)
- Match postponements

Always check FPL news sources:
- https://fantasy.premierleague.com/
- FPL Twitter/X accounts
- r/FantasyPL subreddit
