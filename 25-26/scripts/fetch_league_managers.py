#!/usr/bin/env python3
"""Fetch league managers and match results from FPL."""

import os
import requests
import sqlite3
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"
FPL_BASE_URL = "https://fantasy.premierleague.com/api"

# League ID from env or default
LEAGUE_ID = os.getenv("FPL_LEAGUE_ID", "156772")


def get_session():
    """Create a requests session (no auth needed for public league data)."""
    session = requests.Session()

    # Set headers to look like a browser
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://fantasy.premierleague.com/",
    })

    return session


def fetch_league_h2h_matches(session, gameweek=1):
    """Fetch head-to-head matches for a specific gameweek."""
    url = f"{FPL_BASE_URL}/leagues-h2h-matches/league/{LEAGUE_ID}/?event={gameweek}&page=1"

    all_matches = []
    page = 1

    while True:
        page_url = f"{FPL_BASE_URL}/leagues-h2h-matches/league/{LEAGUE_ID}/?event={gameweek}&page={page}"
        response = session.get(page_url)

        if response.status_code != 200:
            print(f"Error fetching page {page}: {response.status_code}")
            break

        data = response.json()
        matches = data.get("results", [])

        if not matches:
            break

        all_matches.extend(matches)

        if not data.get("has_next"):
            break

        page += 1

    return all_matches


def fetch_league_standings(session):
    """Fetch league standings to get all managers."""
    url = f"{FPL_BASE_URL}/leagues-h2h/{LEAGUE_ID}/standings/"

    all_entries = []
    page = 1

    while True:
        page_url = f"{url}?page_standings={page}"
        response = session.get(page_url)

        if response.status_code != 200:
            print(f"Error fetching standings page {page}: {response.status_code}")
            break

        data = response.json()
        standings = data.get("standings", {})
        entries = standings.get("results", [])

        if not entries:
            break

        all_entries.extend(entries)

        if not standings.get("has_next"):
            break

        page += 1

    return all_entries, data.get("league", {})


def store_managers(managers, league_info):
    """Store managers in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add league_name column if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS league_info (
            id INTEGER PRIMARY KEY,
            name TEXT,
            created DATETIME,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Store league info
    cursor.execute("""
        INSERT OR REPLACE INTO league_info (id, name, last_updated)
        VALUES (?, ?, ?)
    """, (league_info.get("id"), league_info.get("name"), datetime.now().isoformat()))

    # Update managers table to include FPL-specific fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team_name TEXT,
            fpl_id INTEGER UNIQUE,
            fpl_entry_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    for manager in managers:
        cursor.execute("""
            INSERT OR REPLACE INTO managers (fpl_id, name, team_name, fpl_entry_name)
            VALUES (?, ?, ?, ?)
        """, (
            manager.get("entry"),
            manager.get("player_name"),
            manager.get("entry_name"),
            manager.get("entry_name")
        ))

    conn.commit()
    conn.close()
    print(f"Stored {len(managers)} managers in database")


def store_h2h_results(matches, gameweek):
    """Store H2H match results in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create h2h_matches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS h2h_matches (
            id INTEGER PRIMARY KEY,
            gameweek INTEGER,
            entry_1_id INTEGER,
            entry_1_name TEXT,
            entry_1_player_name TEXT,
            entry_1_points INTEGER,
            entry_2_id INTEGER,
            entry_2_name TEXT,
            entry_2_player_name TEXT,
            entry_2_points INTEGER,
            is_knockout BOOLEAN,
            winner INTEGER,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(gameweek, entry_1_id, entry_2_id)
        )
    """)

    for match in matches:
        cursor.execute("""
            INSERT OR REPLACE INTO h2h_matches (
                id, gameweek,
                entry_1_id, entry_1_name, entry_1_player_name, entry_1_points,
                entry_2_id, entry_2_name, entry_2_player_name, entry_2_points,
                is_knockout, winner, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match.get("id"),
            match.get("event"),
            match.get("entry_1_entry"),
            match.get("entry_1_name"),
            match.get("entry_1_player_name"),
            match.get("entry_1_points"),
            match.get("entry_2_entry"),
            match.get("entry_2_name"),
            match.get("entry_2_player_name"),
            match.get("entry_2_points"),
            match.get("is_knockout"),
            match.get("winner"),
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()
    print(f"Stored {len(matches)} H2H matches for GW{gameweek}")


def get_managers_from_db():
    """Get all managers from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM managers ORDER BY name")
    managers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return managers


def main():
    """Main entry point."""
    print("Fetching league data from FPL...")

    session = get_session()

    # Fetch league standings (gets all managers)
    print(f"\nFetching league {LEAGUE_ID} standings...")
    managers, league_info = fetch_league_standings(session)

    if managers:
        print(f"\nLeague: {league_info.get('name')}")
        print(f"Found {len(managers)} managers")
        store_managers(managers, league_info)

        print("\n=== Managers ===")
        for m in managers:
            print(f"  {m.get('player_name'):<25} - {m.get('entry_name')}")
    else:
        print("No managers found. Check your session cookie.")
        return

    # Fetch GW1 matches to see the structure
    print("\nFetching GW1 H2H matches...")
    matches = fetch_league_h2h_matches(session, gameweek=1)

    if matches:
        store_h2h_results(matches, gameweek=1)
        print(f"\n=== GW1 Matches ({len(matches)}) ===")
        for m in matches[:5]:  # Show first 5
            p1 = m.get("entry_1_player_name", "???")
            p2 = m.get("entry_2_player_name", "???")
            s1 = m.get("entry_1_points", 0)
            s2 = m.get("entry_2_points", 0)
            print(f"  {p1} ({s1}) vs ({s2}) {p2}")
        if len(matches) > 5:
            print(f"  ... and {len(matches) - 5} more matches")


if __name__ == "__main__":
    main()
