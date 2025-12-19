#!/usr/bin/env python3
"""Utility functions for interacting with the Fantasy Cup database."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"


def get_connection():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_manager(name, team_name=None, fpl_id=None):
    """Add a new manager to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO managers (name, team_name, fpl_id) VALUES (?, ?, ?)",
        (name, team_name, fpl_id)
    )
    conn.commit()
    manager_id = cursor.lastrowid
    conn.close()
    return manager_id


def add_note(content, category=None):
    """Add a note/log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (content, category) VALUES (?, ?)",
        (content, category)
    )
    conn.commit()
    conn.close()


def get_all_managers():
    """Get all managers."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM managers")
    managers = cursor.fetchall()
    conn.close()
    return [dict(m) for m in managers]


def record_gameweek_score(manager_id, gameweek, points, transfers_cost=0):
    """Record a manager's gameweek score."""
    net_points = points - transfers_cost
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO gameweek_scores
        (manager_id, gameweek, points, transfers_cost, net_points)
        VALUES (?, ?, ?, ?, ?)
    """, (manager_id, gameweek, points, transfers_cost, net_points))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # Quick test
    managers = get_all_managers()
    print(f"Current managers: {managers}")
