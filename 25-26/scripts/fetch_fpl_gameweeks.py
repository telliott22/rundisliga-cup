#!/usr/bin/env python3
"""Fetch gameweek schedule from the official FPL API."""

import requests
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"


def fetch_gameweeks():
    """Fetch gameweek data from FPL API."""
    print("Fetching gameweek data from FPL API...")
    response = requests.get(FPL_API_URL)
    response.raise_for_status()
    data = response.json()
    return data.get('events', [])


def init_gameweeks_table():
    """Create gameweeks table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gameweeks (
            id INTEGER PRIMARY KEY,
            name TEXT,
            deadline_time DATETIME,
            deadline_time_epoch INTEGER,
            is_previous BOOLEAN,
            is_current BOOLEAN,
            is_next BOOLEAN,
            finished BOOLEAN,
            data_checked BOOLEAN,
            highest_score INTEGER,
            average_score INTEGER,
            most_selected INTEGER,
            most_transferred_in INTEGER,
            most_captained INTEGER,
            most_vice_captained INTEGER,
            chip_plays TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def store_gameweeks(gameweeks):
    """Store gameweeks in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for gw in gameweeks:
        cursor.execute("""
            INSERT OR REPLACE INTO gameweeks (
                id, name, deadline_time, deadline_time_epoch,
                is_previous, is_current, is_next, finished, data_checked,
                highest_score, average_score,
                most_selected, most_transferred_in, most_captained, most_vice_captained,
                chip_plays, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gw['id'],
            gw['name'],
            gw['deadline_time'],
            gw['deadline_time_epoch'],
            gw['is_previous'],
            gw['is_current'],
            gw['is_next'],
            gw['finished'],
            gw['data_checked'],
            gw.get('highest_score'),
            gw.get('average_entry_score'),
            gw.get('most_selected'),
            gw.get('most_transferred_in'),
            gw.get('most_captained'),
            gw.get('most_vice_captained'),
            str(gw.get('chip_plays', [])),
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()
    print(f"Stored {len(gameweeks)} gameweeks in database")


def get_gameweek_summary():
    """Get a summary of gameweeks from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, deadline_time, finished, is_current, is_next
        FROM gameweeks
        ORDER BY id
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def main():
    """Main entry point."""
    init_gameweeks_table()
    gameweeks = fetch_gameweeks()
    store_gameweeks(gameweeks)

    # Print summary
    print("\n=== Gameweek Schedule ===")
    summary = get_gameweek_summary()

    current_gw = None
    for gw in summary:
        status = ""
        if gw['is_current']:
            status = " <- CURRENT"
            current_gw = gw
        elif gw['is_next']:
            status = " <- NEXT"
        elif gw['finished']:
            status = " (finished)"

        deadline = datetime.fromisoformat(gw['deadline_time'].replace('Z', '+00:00'))
        print(f"GW{gw['id']:2d}: {deadline.strftime('%Y-%m-%d %H:%M')} UTC{status}")

    return summary


if __name__ == "__main__":
    main()
