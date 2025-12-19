# Rundisliga Cup 25/26

A fantasy football cup competition management system for the Rundisliga FPL league.

## Overview

20 managers compete in a Swiss-style tournament format inspired by the UEFA Champions League:

- **Group Stage**: 10 rounds where each team plays 10 different opponents (half the league)
- **Knockout Stage**: Top 8 qualify for Quarter-Finals, Semi-Finals, and Final
- **Season**: GW21 (January 2026) to GW38 (May 2026)

## Format

### Group Stage Scoring
| Result | Points |
|--------|--------|
| Win    | 3      |
| Draw   | 1      |
| Loss   | 0      |

### Tiebreakers
1. Total points
2. Total FPL points scored across group stage
3. Head-to-head result (if they played each other)

### Playoff Rule
If multiple teams are tied for 8th place (last qualification spot), they compete in a playoff during GW32. The team(s) with the highest FPL score that gameweek qualify.

### Knockout Rounds
- **Quarter-Finals**: GW33-34 (2 legs)
- **Semi-Finals**: GW36-37 (2 legs)
- **Final**: GW38 (single match)

Knockout tiebreakers:
1. Aggregate score
2. Away goals rule
3. Higher score in 2nd leg

## Scripts

| Script | Description |
|--------|-------------|
| `scripts/generate_swiss_draw.py` | Generates the 10-round fixture list |
| `scripts/generate_results_image.py` | Creates styled results images |
| `scripts/generate_standings_image.py` | Creates standings table images |
| `scripts/generate_whatsapp_message.py` | Generates WhatsApp messages |
| `scripts/schedule_cup_tasks.py` | Schedules automated reminders |

### Usage Examples

```bash
# Generate results image for a gameweek
python3 scripts/generate_results_image.py 21

# Generate standings image
python3 scripts/generate_standings_image.py

# Generate WhatsApp messages
python3 scripts/generate_whatsapp_message.py announcement
python3 scripts/generate_whatsapp_message.py pre 21      # Pre-gameweek reminder
python3 scripts/generate_whatsapp_message.py post 21     # Post-gameweek results
python3 scripts/generate_whatsapp_message.py notcup 26   # Break week reminder

# Regenerate the Swiss draw
python3 scripts/generate_swiss_draw.py
```

## Schedule

### Group Stage
| Round | Gameweek | Date |
|-------|----------|------|
| 1 | GW21 | Tue Jan 6, 2026 |
| 2 | GW22 | Sat Jan 17, 2026 |
| 3 | GW23 | Sat Jan 24, 2026 |
| 4 | GW24 | Sat Jan 31, 2026 |
| 5 | GW25 | Fri Feb 6, 2026 |
| *Break* | GW26 | Feb 10, 2026 |
| 6 | GW27 | Sat Feb 21, 2026 |
| 7 | GW28 | Fri Feb 27, 2026 |
| 8 | GW29 | Wed Mar 4, 2026 |
| 9 | GW30 | Sat Mar 14, 2026 |
| 10 | GW31 | Sat Mar 21, 2026 |

### Knockouts
| Round | Gameweek | Date |
|-------|----------|------|
| *Playoff (if needed)* | GW32 | Apr 11, 2026 |
| QF 1st Leg | GW33 | Sat Apr 18, 2026 |
| QF 2nd Leg | GW34 | Sat Apr 25, 2026 |
| *Break* | GW35 | May 2, 2026 |
| SF 1st Leg | GW36 | Sat May 9, 2026 |
| SF 2nd Leg | GW37 | Sun May 17, 2026 |
| **FINAL** | **GW38** | **Sun May 24, 2026** |

## Managers

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

## Data

- **FPL League ID**: 156772
- **Database**: `db/fantasy_cup.db` (SQLite)
- **Images**: Generated to `images/` directory

## Files

```
25-26/
├── README.md
├── fixtures.md              # Full fixture list
├── context/
│   ├── cup-format.md        # Detailed format & rules
│   └── whatsapp-templates.md # Message templates
├── db/
│   └── fantasy_cup.db       # SQLite database
├── images/
│   ├── gw*_results.png      # Results images
│   └── standings.png        # Standings table
├── scripts/
│   ├── generate_results_image.py
│   ├── generate_standings_image.py
│   ├── generate_swiss_draw.py
│   ├── generate_whatsapp_message.py
│   └── schedule_cup_tasks.py
└── tasks/
    └── gw*_pre.md, gw*_post.md  # Scheduled task files
```

## License

Private competition - not for redistribution.
