# Rundisliga Fantasy Football Cup 25-26

## CRITICAL: Verify Current Date/Time First

**Before doing ANYTHING in this project, confirm the current date and time:**

```bash
date
```

The season is **2025-26**. If you think the year is 2024, you are WRONG. Always verify.

This is critical because:
- Gameweek calculations depend on knowing the current date
- Scheduled messages need accurate timing
- Score lookups require knowing which GWs have finished

## On Every Session Start

1. **Check the date** (run `date`)
2. **Sync gameweek data:**
```bash
python3 scripts/fetch_fpl_gameweeks.py
```

Gameweek deadlines can change due to match rescheduling. This syncs the latest from the FPL API.

## Project Structure

```
25-26/
├── db/
│   └── fantasy_cup.db      # SQLite database (managers, fixtures, scores, gameweeks)
├── scripts/
│   ├── fetch_fpl_gameweeks.py  # Sync gameweek data from FPL API
│   ├── init_db.py              # Database initialization
│   └── db_utils.py             # Helper functions
├── tasks/                  # Scheduled task files
├── decisions/              # Decision log (markdown files)
├── context/                # Reference material
│   ├── fpl-data.md         # FPL API info and data management
│   └── README.md
└── temp/                   # Working/scratch files
```

## Key Information

- **Current Season**: 2025-26 Premier League
- **Gameweeks**: 38 total (GW1 through GW38)
- **Data source**: Official FPL API (https://fantasy.premierleague.com/api/)

## Database Tables

- `managers` - Cup participants
- `gameweeks` - FPL gameweek schedule (synced from API)
- `rounds` - Cup rounds (Round of 32, Quarter-finals, etc.)
- `fixtures` - Head-to-head matches
- `gameweek_scores` - Individual GW performances
- `notes` - Decision log

## Scheduled Messages

The cup requires messages to be sent:
1. **Before each relevant gameweek** - Fixture announcements, reminders
2. **After each relevant gameweek** - Scores, results, who advances

Use the global scheduler (`~/.claude/scheduler.db`) to schedule these.
