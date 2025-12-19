#!/usr/bin/env python3
"""Schedule all Rundisliga Cup tasks for the season."""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

# Add scheduler to path
sys.path.insert(0, str(Path.home() / ".claude" / "scheduler"))
from db_utils import add_task

PROJECT_PATH = str(Path(__file__).parent.parent)
TASKS_DIR = Path(__file__).parent.parent / "tasks"
DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"

# Cup schedule
CUP_SCHEDULE = {
    # Group stage
    21: {"round": 1, "type": "group"},
    22: {"round": 2, "type": "group"},
    23: {"round": 3, "type": "group"},
    24: {"round": 4, "type": "group"},
    25: {"round": 5, "type": "group"},
    26: {"type": "break"},  # Mid-group break
    27: {"round": 6, "type": "group"},
    28: {"round": 7, "type": "group"},
    29: {"round": 8, "type": "group"},
    30: {"round": 9, "type": "group"},
    31: {"round": 10, "type": "group"},
    32: {"type": "playoff"},  # Playoff if needed
    # Knockouts
    33: {"round": "QF1", "type": "knockout"},
    34: {"round": "QF2", "type": "knockout"},
    35: {"type": "break"},  # Pre-SF break
    36: {"round": "SF1", "type": "knockout"},
    37: {"round": "SF2", "type": "knockout"},
    38: {"round": "Final", "type": "final"},
}


def get_gameweek_deadlines():
    """Get gameweek deadlines from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, deadline_time FROM gameweeks")
    deadlines = {row['id']: datetime.fromisoformat(row['deadline_time'].replace('Z', '+00:00')) for row in cursor.fetchall()}
    conn.close()
    return deadlines


def create_pre_gameweek_task(gw, info, deadline):
    """Create pre-gameweek reminder task file."""
    round_type = info.get("type")
    round_num = info.get("round", "")

    if round_type == "group":
        title = f"Round {round_num} Pre-Gameweek Reminder"
        content = f"""# Rundisliga Cup - Round {round_num} (GW{gw}) Reminder

## Task
Generate and send the pre-gameweek reminder message for Round {round_num}.

## Steps
1. Run: `python3 scripts/generate_whatsapp_message.py pre {gw}`
2. Copy the generated message
3. Send to WhatsApp group
4. Optionally generate fixtures image if needed

## Deadline
{deadline.strftime('%a %b %d, %Y %H:%M')}
"""
    elif round_type == "knockout":
        title = f"{round_num} Pre-Match Reminder"
        content = f"""# Rundisliga Cup - {round_num} (GW{gw}) Reminder

## Task
Generate and send the pre-match reminder for {round_num}.

## Steps
1. Run: `python3 scripts/generate_whatsapp_message.py pre {gw}`
2. Copy the generated message
3. Send to WhatsApp group

## Deadline
{deadline.strftime('%a %b %d, %Y %H:%M')}
"""
    elif round_type == "final":
        title = "FINAL Pre-Match Reminder"
        content = f"""# Rundisliga Cup - FINAL (GW{gw}) Reminder

## Task
Generate and send the FINAL pre-match reminder.

## Steps
1. Run: `python3 scripts/generate_whatsapp_message.py pre {gw}`
2. Copy the generated message
3. Send to WhatsApp group

## Deadline
{deadline.strftime('%a %b %d, %Y %H:%M')}

THIS IS THE FINAL - MAKE IT COUNT!
"""
    elif round_type == "break":
        title = f"GW{gw} Break Week Reminder"
        content = f"""# Rundisliga Cup - GW{gw} Break Week

## Task
Send the "not a cup week" reminder.

## Steps
1. Run: `python3 scripts/generate_whatsapp_message.py notcup {gw}`
2. Copy the generated message
3. Send to WhatsApp group

## Deadline
{deadline.strftime('%a %b %d, %Y %H:%M')}
"""
    elif round_type == "playoff":
        title = "Playoff Reminder (If Needed)"
        content = f"""# Rundisliga Cup - Playoff (GW{gw})

## Task
Check if playoff is needed. If yes, send reminder.

## Steps
1. Check standings - are teams tied for 8th place?
2. If YES: Generate playoff announcement
3. If NO: Send "not a cup week" message

## Commands
- Standings: `python3 scripts/generate_standings_image.py`
- Not cup week: `python3 scripts/generate_whatsapp_message.py notcup {gw}`

## Deadline
{deadline.strftime('%a %b %d, %Y %H:%M')}
"""
    else:
        return None, None

    return title, content


def create_post_gameweek_task(gw, info, deadline):
    """Create post-gameweek results task file."""
    round_type = info.get("type")
    round_num = info.get("round", "")

    # Post-gameweek tasks should run ~2 hours after deadline (when matches finish)
    post_time = deadline + timedelta(hours=26)  # Next day evening

    if round_type == "group":
        title = f"Round {round_num} Results"
        content = f"""# Rundisliga Cup - Round {round_num} (GW{gw}) Results

## Task
Generate and send results for Round {round_num}.

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py {gw}`
2. Generate standings image: `python3 scripts/generate_standings_image.py`
3. Generate message: `python3 scripts/generate_whatsapp_message.py post {gw}`
4. Send results image to WhatsApp
5. Send standings image to WhatsApp
6. Send message to WhatsApp

## Files Generated
- images/gw{gw}_results.png
- images/standings.png
"""
    elif round_type == "knockout":
        title = f"{round_num} Results"
        content = f"""# Rundisliga Cup - {round_num} (GW{gw}) Results

## Task
Generate and send results for {round_num}.

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py {gw}`
2. Generate message: `python3 scripts/generate_whatsapp_message.py post {gw}`
3. Send results image to WhatsApp
4. Send message to WhatsApp
5. If 2nd leg - include aggregate scores and who advances

## Files Generated
- images/gw{gw}_results.png
"""
    elif round_type == "final":
        title = "FINAL Results - CROWN THE WINNER!"
        content = f"""# Rundisliga Cup - FINAL (GW{gw}) Results

## Task
ANNOUNCE THE WINNER OF THE RUNDISLIGA CUP 25/26!

## Steps
1. Generate results image: `python3 scripts/generate_results_image.py {gw}`
2. Use the winner message template
3. Send results image to WhatsApp
4. Send winner announcement to WhatsApp
5. CELEBRATE!

## Winner Message
Use `generate_winner_message(winner_name, winner_team, score)` from generate_whatsapp_message.py

THIS IS THE MOMENT WE'VE ALL BEEN WAITING FOR!
"""
    elif round_type == "playoff":
        title = "Playoff Results (If Played)"
        content = f"""# Rundisliga Cup - Playoff (GW{gw}) Results

## Task
If a playoff was held, announce the results and who qualified.

## Steps
1. Check if playoff was needed
2. If YES: Announce who qualified based on FPL scores
3. Generate quarter-final draw

## Commands
- `python3 scripts/generate_standings_image.py`
"""
    elif round_type == "break":
        return None, None
    else:
        return None, None

    return title, content


def main():
    """Main entry point."""
    print("=== SCHEDULING RUNDISLIGA CUP TASKS ===")
    print()

    deadlines = get_gameweek_deadlines()
    tasks_created = 0
    files_created = 0

    for gw, info in CUP_SCHEDULE.items():
        if gw not in deadlines:
            print(f"Warning: GW{gw} not in gameweeks database")
            continue

        deadline = deadlines[gw]

        # Create pre-gameweek task (1 day before deadline)
        pre_time = deadline - timedelta(days=1)
        title, content = create_pre_gameweek_task(gw, info, deadline)

        if title and content:
            task_file = f"tasks/gw{gw}_pre.md"
            file_path = Path(PROJECT_PATH) / task_file

            with open(file_path, 'w') as f:
                f.write(content)
            files_created += 1

            task_id = add_task(
                summary=f"Rundisliga Cup: {title}",
                project_path=PROJECT_PATH,
                task_file=task_file,
                scheduled_at=pre_time,
                priority=3
            )
            tasks_created += 1
            print(f"Created: GW{gw} pre ({title}) - {pre_time.strftime('%Y-%m-%d %H:%M')}")

        # Create post-gameweek task (day after deadline)
        if info.get("type") != "break":
            post_time = deadline + timedelta(hours=26)
            title, content = create_post_gameweek_task(gw, info, deadline)

            if title and content:
                task_file = f"tasks/gw{gw}_post.md"
                file_path = Path(PROJECT_PATH) / task_file

                with open(file_path, 'w') as f:
                    f.write(content)
                files_created += 1

                task_id = add_task(
                    summary=f"Rundisliga Cup: {title}",
                    project_path=PROJECT_PATH,
                    task_file=task_file,
                    scheduled_at=post_time,
                    priority=3
                )
                tasks_created += 1
                print(f"Created: GW{gw} post ({title}) - {post_time.strftime('%Y-%m-%d %H:%M')}")

    print()
    print(f"=== COMPLETE ===")
    print(f"Task files created: {files_created}")
    print(f"Scheduled tasks created: {tasks_created}")


if __name__ == "__main__":
    main()
