# Rundisliga Cup 25/26 - Claude Context

## CRITICAL: Verify Current Date First
```bash
date
```
The season is **2025-26**. Gameweek calculations depend on knowing the current date.

## Project Overview
Fantasy Football Cup competition for the Rundisliga FPL league (League ID: 156772).
20 managers compete in a Swiss-style tournament inspired by the UEFA Champions League.

## Quick Reference

### FPL API
- **League ID**: 156772
- **H2H Standings**: `https://fantasy.premierleague.com/api/leagues-h2h/156772/standings/`
- **H2H Matches**: `https://fantasy.premierleague.com/api/leagues-h2h-matches/league/156772/?event={gameweek}`

### Database
- **Location**: `db/fantasy_cup.db` (SQLite)
- **Tables**: managers, gameweeks, cup_fixtures, cup_standings, h2h_matches

### Cup Format
- **Group Stage**: 10 rounds (GW21-31), each team plays 10 different opponents
- **Scoring**: Win=3pts, Draw=1pt, Loss=0pts
- **Qualification**: Top 8 qualify for knockouts
- **Playoff**: If teams tied for 8th place, highest FPL score in GW32 qualifies
- **Knockouts**: QF (GW33-34), SF (GW36-37), Final (GW38)
- **Tiebreakers**: 1) Points, 2) Total FPL points, 3) Head-to-head

## Key Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| Results Image | `python3 scripts/generate_results_image.py <gw>` | Create styled results image |
| Standings Image | `python3 scripts/generate_standings_image.py` | Create standings table image |
| Swiss Draw | `python3 scripts/generate_swiss_draw.py` | Generate fixtures (already done) |
| WhatsApp Messages | `python3 scripts/generate_whatsapp_message.py <cmd>` | Generate ALLCAPS messages |

### WhatsApp Message Commands
```bash
python3 scripts/generate_whatsapp_message.py announcement  # Cup announcement
python3 scripts/generate_whatsapp_message.py draw          # Draw + Round 1 fixtures
python3 scripts/generate_whatsapp_message.py pre <gw>      # Pre-gameweek reminder
python3 scripts/generate_whatsapp_message.py post <gw>     # Post-gameweek results
python3 scripts/generate_whatsapp_message.py notcup <gw>   # Break week reminder
```

## Full Schedule

```
GROUP STAGE
Round 1 - GW21 (Jan 6, 2026)
Round 2 - GW22 (Jan 17)
Round 3 - GW23 (Jan 24)
Round 4 - GW24 (Jan 31)
Round 5 - GW25 (Feb 6)
Break - GW26 (Feb 10)
Round 6 - GW27 (Feb 21)
Round 7 - GW28 (Feb 27)
Round 8 - GW29 (Mar 4)
Round 9 - GW30 (Mar 14)
Round 10 - GW31 (Mar 21)

KNOCKOUTS
Playoff - GW32 (Apr 11) - if needed
QF 1st Leg - GW33 (Apr 18)
QF 2nd Leg - GW34 (Apr 25)
Break - GW35 (May 2)
SF 1st Leg - GW36 (May 9)
SF 2nd Leg - GW37 (May 17)
FINAL - GW38 (May 24)
```

## Scheduled Tasks (35 total in ~/.claude/scheduler.db)

| Task | Date | Action |
|------|------|--------|
| **Draw Day** | Sun Jan 4, 2026 @ 6pm | Generate fixtures & send announcement |
| Pre-GW reminders | 1 day before deadline | Send fixture reminder |
| Post-GW results | Day after deadline | Send results + standings images |
| Break reminders | GW26, GW35 | Send "not a cup week" message |

## Task Workflow

### 1. Draw Day (Jan 4, 2026)
```bash
python3 scripts/generate_whatsapp_message.py draw
```
Send message to WhatsApp group.

### 2. Pre-Gameweek Reminder
```bash
python3 scripts/generate_whatsapp_message.py pre <gw>
```
Send message to WhatsApp group.

### 3. Post-Gameweek Results
```bash
python3 scripts/generate_results_image.py <gw>
python3 scripts/generate_standings_image.py
python3 scripts/generate_whatsapp_message.py post <gw>
```
Send images + message to WhatsApp group.

### 4. Break Week
```bash
python3 scripts/generate_whatsapp_message.py notcup <gw>
```
Send message to WhatsApp group.

## Message Style
All WhatsApp messages use **ALLCAPS** style with 🚨 emojis.
See `context/whatsapp-templates.md` for full templates.

## Managers (20)

| # | Manager | Team |
|---|---------|------|
| 1 | Steve Keeble | The Mask of Porro FC |
| 2 | Jonathan Lane | AllIWatchNowIsBluey |
| 3 | Phil Bateman | AC Philan |
| 4 | Jack Haslam | SakaSpuds |
| 5 | Ruben Pillai | Gyok Stock & 6 Goals |
| 6 | Andy Carr | Carrlton Athletic FC |
| 7 | Adetokumbo Ayorinde | Schieß ein Tor FC |
| 8 | George Asiedu | Georgedoes FC |
| 9 | Reyhan Pillai | YRUgueye |
| 10 | Hadi Shakeri | The Red Zone Rejects |
| 11 | Kris Butler | Titus Shambles |
| 12 | Arash Khanjani | Red, Green & YANITED |
| 13 | Ben Nuttall | Crafty Pocket Frank |
| 14 | Nick Willis | Gangsters Allardyce |
| 15 | Martin Dempsey | mcdfc |
| 16 | Gareth Hutton | Tiki Saka Football |
| 17 | Alex Carr | Carrlton Athletic FC |
| 18 | Ciaran McCullough | Gyökamole |
| 19 | Tim Elliott | FC TimBuktu |
| 20 | Jack Rogers | Too Eze For Kudus |

## Files Structure
```
rundisliga-cup/
├── README.md
└── 25-26/
    ├── CLAUDE.md (this file)
    ├── README.md
    ├── fixtures.md              # Full fixture list
    ├── context/
    │   ├── cup-format.md        # Detailed rules
    │   └── whatsapp-templates.md
    ├── db/fantasy_cup.db        # SQLite database
    ├── images/                  # Generated images
    ├── scripts/                 # Python scripts
    └── tasks/                   # Scheduled task files
```

## Global Scheduler
- **Location**: `~/.claude/scheduler/`
- **Database**: `~/.claude/scheduler.db`
- **LaunchAgent**: `~/Library/LaunchAgents/com.claude.scheduler.plist` (hourly checks)
- **Notifications**: macOS terminal-notifier with click-to-open

## GitHub
- **URL**: https://github.com/telliott22/rundisliga-cup
- **Branch**: main
