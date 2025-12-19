#!/usr/bin/env python3
"""Initialize the Fantasy Football Cup SQLite database with base schema."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Managers/Teams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team_name TEXT,
            fpl_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Cup rounds table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gameweek_start INTEGER,
            gameweek_end INTEGER,
            status TEXT DEFAULT 'pending'
        )
    """)

    # Fixtures table (matches between managers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fixtures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER,
            home_manager_id INTEGER,
            away_manager_id INTEGER,
            home_score REAL,
            away_score REAL,
            winner_id INTEGER,
            gameweek INTEGER,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (round_id) REFERENCES rounds(id),
            FOREIGN KEY (home_manager_id) REFERENCES managers(id),
            FOREIGN KEY (away_manager_id) REFERENCES managers(id),
            FOREIGN KEY (winner_id) REFERENCES managers(id)
        )
    """)

    # Gameweek scores table (track individual GW performances)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gameweek_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manager_id INTEGER,
            gameweek INTEGER,
            points INTEGER,
            transfers_cost INTEGER DEFAULT 0,
            net_points INTEGER,
            FOREIGN KEY (manager_id) REFERENCES managers(id),
            UNIQUE(manager_id, gameweek)
        )
    """)

    # Notes/Log table for tracking decisions and events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_database()
