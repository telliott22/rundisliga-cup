# Rundisliga Cup - Playoff (GW32)

## Task
Check if playoff is needed. If yes, send reminder.

## Steps
1. Check standings - are teams tied for 8th place?
2. If YES: Generate playoff announcement
3. If NO: Send "not a cup week" message

## Commands
- Standings: `python3 scripts/generate_standings_image.py`
- Not cup week: `python3 scripts/generate_whatsapp_message.py notcup 32`

## Deadline
Sat Apr 11, 2026 12:30
