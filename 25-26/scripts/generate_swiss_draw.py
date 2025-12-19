#!/usr/bin/env python3
"""
Generate Swiss-style draw for Rundisliga Cup.
Each team plays 10 opponents (half the league) with seeded randomization.
"""

import sqlite3
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"

# Cup schedule: round number -> gameweek
ROUND_TO_GAMEWEEK = {
    1: 21,
    2: 22,
    3: 23,
    4: 24,
    5: 25,
    # GW26 is break
    6: 27,
    7: 28,
    8: 29,
    9: 30,
    10: 31,
    # GW32 is break (potential playoff)
    # Knockouts
    11: 33,  # QF 1st leg
    12: 34,  # QF 2nd leg
    # GW35 is break
    13: 36,  # SF 1st leg
    14: 37,  # SF 2nd leg
    15: 38,  # Final
}


def get_managers():
    """Get all managers from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT fpl_id, name, team_name FROM managers ORDER BY fpl_id")
    managers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return managers


def get_seeding_from_fpl_standings():
    """
    Get seeding based on current FPL league standings.
    For now, we'll use a placeholder - this should be run after GW20.
    Returns list of manager fpl_ids in seeding order (1st = best).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Try to get from h2h standings if available
    cursor.execute("""
        SELECT entry_1_id as fpl_id, SUM(entry_1_points) as total_points
        FROM h2h_matches
        GROUP BY entry_1_id
        UNION
        SELECT entry_2_id as fpl_id, SUM(entry_2_points) as total_points
        FROM h2h_matches
        GROUP BY entry_2_id
        ORDER BY total_points DESC
    """)
    standings = cursor.fetchall()
    conn.close()

    if standings:
        # Aggregate by fpl_id
        points_by_manager = defaultdict(int)
        for row in standings:
            points_by_manager[row['fpl_id']] += row['total_points'] or 0

        # Sort by total points descending
        sorted_managers = sorted(points_by_manager.items(), key=lambda x: x[1], reverse=True)
        return [m[0] for m in sorted_managers]

    # Fallback: random seeding
    managers = get_managers()
    fpl_ids = [m['fpl_id'] for m in managers]
    random.shuffle(fpl_ids)
    return fpl_ids


def generate_swiss_fixtures(seeding):
    """
    Generate 10 rounds of fixtures where each team plays 10 different opponents.
    Uses backtracking to ensure valid pairings with no rematches.
    """
    n = len(seeding)  # Should be 20
    if n != 20:
        raise ValueError(f"Expected 20 managers, got {n}")

    # Track who has played whom (global across all rounds)
    played = defaultdict(set)

    # Track home/away balance
    home_count = defaultdict(int)
    away_count = defaultdict(int)

    fixtures = []

    def can_pair(team1, team2):
        """Check if two teams can be paired (haven't played each other yet)."""
        return team2 not in played[team1]

    def find_valid_pairing(unpaired_list, current_pairs):
        """
        Recursively find a valid pairing for all teams using backtracking.
        Returns list of pairs or None if no valid pairing exists.
        """
        if len(unpaired_list) == 0:
            return current_pairs

        if len(unpaired_list) == 2:
            t1, t2 = unpaired_list
            if can_pair(t1, t2):
                return current_pairs + [(t1, t2)]
            return None

        # Take first team and try pairing with each possible opponent
        team1 = unpaired_list[0]
        remaining = unpaired_list[1:]

        # Shuffle remaining to add randomness
        candidates = [t for t in remaining if can_pair(team1, t)]
        random.shuffle(candidates)

        for team2 in candidates:
            # Try this pairing
            new_remaining = [t for t in remaining if t != team2]
            result = find_valid_pairing(new_remaining, current_pairs + [(team1, team2)])
            if result is not None:
                return result

        return None

    for round_num in range(1, 11):
        # Shuffle teams for this round
        teams = list(seeding)
        random.shuffle(teams)

        # Find valid pairing using backtracking
        pairs = find_valid_pairing(teams, [])

        if pairs is None:
            raise ValueError(f"Could not find valid pairing for round {round_num}")

        round_fixtures = []
        for team1, team2 in pairs:
            # Record the match
            played[team1].add(team2)
            played[team2].add(team1)

            # Determine home/away based on balance
            t1_home_deficit = home_count[team1] - away_count[team1]
            t2_home_deficit = home_count[team2] - away_count[team2]

            if t1_home_deficit < t2_home_deficit:
                home, away = team1, team2
            elif t2_home_deficit < t1_home_deficit:
                home, away = team2, team1
            else:
                # Equal balance - randomize
                if random.random() < 0.5:
                    home, away = team1, team2
                else:
                    home, away = team2, team1

            home_count[home] += 1
            away_count[away] += 1

            round_fixtures.append({
                'round': round_num,
                'gameweek': ROUND_TO_GAMEWEEK[round_num],
                'home': home,
                'away': away
            })

        fixtures.extend(round_fixtures)

    return fixtures


def save_fixtures_to_db(fixtures):
    """Save fixtures to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Clear existing group stage fixtures
    cursor.execute("DELETE FROM cup_fixtures WHERE round <= 10")

    for f in fixtures:
        cursor.execute("""
            INSERT INTO cup_fixtures (round, gameweek, home_manager_id, away_manager_id)
            VALUES (?, ?, ?, ?)
        """, (f['round'], f['gameweek'], f['home'], f['away']))

    conn.commit()
    conn.close()
    print(f"Saved {len(fixtures)} fixtures to database")


def get_manager_name(fpl_id, managers_dict):
    """Get manager name from fpl_id."""
    return managers_dict.get(fpl_id, {}).get('name', f'Unknown ({fpl_id})')


def print_fixtures(fixtures, managers_dict):
    """Print fixtures in a readable format."""
    current_round = 0

    for f in fixtures:
        if f['round'] != current_round:
            current_round = f['round']
            gw = f['gameweek']
            print(f"\n=== ROUND {current_round} (GW{gw}) ===")

        home_name = get_manager_name(f['home'], managers_dict)
        away_name = get_manager_name(f['away'], managers_dict)
        print(f"  {home_name:<25} vs {away_name}")


def verify_fixtures(fixtures, n_teams=20):
    """Verify the fixtures are valid."""
    games_per_team = defaultdict(int)
    opponents = defaultdict(set)
    home_games = defaultdict(int)
    away_games = defaultdict(int)

    for f in fixtures:
        home = f['home']
        away = f['away']

        games_per_team[home] += 1
        games_per_team[away] += 1

        opponents[home].add(away)
        opponents[away].add(home)

        home_games[home] += 1
        away_games[away] += 1

    print("\n=== FIXTURE VERIFICATION ===")

    # Check games per team
    games_ok = all(g == 10 for g in games_per_team.values())
    print(f"All teams play 10 games: {'✓' if games_ok else '✗'}")
    if not games_ok:
        for team, games in games_per_team.items():
            if games != 10:
                print(f"  Team {team}: {games} games")

    # Check unique opponents
    opponents_ok = all(len(opps) == 10 for opps in opponents.values())
    print(f"All teams face 10 different opponents: {'✓' if opponents_ok else '✗'}")

    # Check home/away balance
    print("\nHome/Away balance:")
    for team in sorted(games_per_team.keys()):
        h = home_games[team]
        a = away_games[team]
        print(f"  Team {team}: {h}H / {a}A")


def main():
    """Main entry point."""
    print("=== RUNDISLIGA CUP 25/26 SWISS DRAW ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Get managers
    managers = get_managers()
    managers_dict = {m['fpl_id']: m for m in managers}
    print(f"\nManagers: {len(managers)}")

    # Get seeding
    print("\nGenerating seeding...")
    seeding = get_seeding_from_fpl_standings()
    print("Seeding order:")
    for i, fpl_id in enumerate(seeding, 1):
        name = get_manager_name(fpl_id, managers_dict)
        print(f"  {i:2d}. {name}")

    # Generate fixtures
    print("\nGenerating fixtures...")
    fixtures = generate_swiss_fixtures(seeding)

    # Print fixtures
    print_fixtures(fixtures, managers_dict)

    # Verify
    verify_fixtures(fixtures)

    # Save to database
    save_fixtures_to_db(fixtures)

    print("\n✓ Draw complete!")


if __name__ == "__main__":
    main()
