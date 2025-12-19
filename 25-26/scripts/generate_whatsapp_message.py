#!/usr/bin/env python3
"""Generate WhatsApp messages for Rundisliga Cup announcements."""

import sqlite3
import requests
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"
LEAGUE_ID = "156772"

# Gameweek to Cup Round mapping
GAMEWEEK_TO_ROUND = {
    21: 1, 22: 2, 23: 3, 24: 4, 25: 5,
    27: 6, 28: 7, 29: 8, 30: 9, 31: 10,
    32: "PLAYOFF",
    33: "QF1", 34: "QF2",
    36: "SF1", 37: "SF2",
    38: "FINAL"
}

# Non-cup gameweeks
NON_CUP_WEEKS = [26, 35]


def get_db_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_managers():
    """Get all managers as dict keyed by fpl_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fpl_id, name, team_name FROM managers")
    managers = {row['fpl_id']: dict(row) for row in cursor.fetchall()}
    conn.close()
    return managers


def get_gameweek_info(gw):
    """Get gameweek deadline info."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT deadline_time FROM gameweeks WHERE id = ?", (gw,))
    row = cursor.fetchone()
    conn.close()
    if row:
        dt = datetime.fromisoformat(row['deadline_time'].replace('Z', '+00:00'))
        return dt.strftime('%a %b %d, %Y').upper()
    return "TBD"


def get_fixtures_for_round(round_num):
    """Get fixtures for a cup round from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM cup_fixtures WHERE round = ?
        ORDER BY id
    """, (round_num,))
    fixtures = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return fixtures


def get_results_for_gameweek(gw):
    """Get H2H results for a gameweek from FPL API."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    url = f"https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{LEAGUE_ID}/?event={gw}&page=1"
    response = session.get(url)
    return response.json().get("results", [])


def get_standings():
    """Get current H2H standings from FPL API."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    url = f"https://fantasy.premierleague.com/api/leagues-h2h/{LEAGUE_ID}/standings/"
    response = session.get(url)
    data = response.json()
    return data.get('standings', {}).get('results', [])


def format_fixture_list(fixtures, managers):
    """Format fixtures as text list."""
    lines = []
    for f in fixtures:
        home = managers.get(f['home_manager_id'], {}).get('name', 'Unknown')
        away = managers.get(f['away_manager_id'], {}).get('name', 'Unknown')
        lines.append(f"{home.upper()} VS {away.upper()}")
    return "\n".join(lines)


def format_results_list(results):
    """Format results as text list."""
    lines = []
    for r in results:
        p1 = r.get('entry_1_player_name', '???').upper()
        p2 = r.get('entry_2_player_name', '???').upper()
        s1 = r.get('entry_1_points', 0) or 0
        s2 = r.get('entry_2_points', 0) or 0

        # Indicate winner
        if s1 > s2:
            lines.append(f"* {p1} {s1} - {s2} {p2}")
        elif s2 > s1:
            lines.append(f"{p1} {s1} - {s2} {p2} *")
        else:
            lines.append(f"{p1} {s1} - {s2} {p2}")
    return "\n".join(lines)


def format_standings_top_n(standings, n=10):
    """Format top N standings."""
    lines = []
    for i, team in enumerate(standings[:n], 1):
        name = team['player_name'].upper()
        pts = team['total']
        fpl = team.get('points_for', 0)
        lines.append(f"{i}. {name} - {pts} PTS ({fpl} FPL)")
    return "\n".join(lines)


# ============ MESSAGE GENERATORS ============

def generate_announcement_message():
    """Generate cup announcement message."""
    return """🚨 RUNDISLIGA CUP 25/26 ANNOUNCEMENT 🚨

THE RUNDISLIGA CUP IS BACK FOR ANOTHER SEASON

🏆 20 MANAGERS WILL COMPETE IN A 10-GAME SWISS-STYLE GROUP STAGE
🏆 TOP 8 QUALIFY FOR KNOCKOUT ROUNDS
🏆 QUARTER-FINALS AND SEMI-FINALS ARE 2-LEG TIES
🏆 FINAL ON THE LAST DAY OF THE SEASON (GW38)

🚨 CUP STARTS GAMEWEEK 21 (TUE JAN 6, 2026) 🚨

FULL FIXTURE LIST AND DRAW COMING SOON"""


def generate_draw_message(round1_fixtures=None):
    """Generate draw announcement message."""
    managers = get_managers()

    if round1_fixtures is None:
        round1_fixtures = get_fixtures_for_round(1)

    fixture_list = format_fixture_list(round1_fixtures, managers)

    return f"""🚨 RUNDISLIGA CUP 25/26 DRAW COMPLETE 🚨

THE SWISS DRAW HAS BEEN MADE

EACH TEAM WILL PLAY 10 OPPONENTS OVER 10 ROUNDS
WIN = 3 POINTS | DRAW = 1 POINT | LOSS = 0 POINTS

TOP 8 AFTER 10 ROUNDS QUALIFY FOR THE KNOCKOUT STAGES

🚨 ROUND 1 FIXTURES (GW21 - TUE JAN 6) 🚨

{fixture_list}

GOOD LUCK TO ALL MANAGERS 🍀"""


def generate_pre_gameweek_message(gw):
    """Generate pre-gameweek fixture reminder."""
    round_num = GAMEWEEK_TO_ROUND.get(gw)

    if gw in NON_CUP_WEEKS:
        return generate_not_cup_week_message(gw)

    if round_num is None:
        return f"🚨 GAMEWEEK {gw} IS NOT A CUP GAMEWEEK 🚨"

    if isinstance(round_num, str):
        # Knockout round
        return generate_knockout_reminder(gw, round_num)

    managers = get_managers()
    fixtures = get_fixtures_for_round(round_num)
    fixture_list = format_fixture_list(fixtures, managers)
    deadline = get_gameweek_info(gw)

    return f"""🚨 RUNDISLIGA CUP REMINDER 🚨

GAMEWEEK {gw} IS CUP ROUND {round_num}

THIS WEEK'S FIXTURES:
{fixture_list}

DEADLINE: {deadline}

GOOD LUCK TO ALL MANAGERS 🍀"""


def generate_post_gameweek_message(gw):
    """Generate post-gameweek results message."""
    round_num = GAMEWEEK_TO_ROUND.get(gw)

    if round_num is None or gw in NON_CUP_WEEKS:
        return None

    if isinstance(round_num, str):
        # Knockout round
        return generate_knockout_results(gw, round_num)

    results = get_results_for_gameweek(gw)
    standings = get_standings()

    results_list = format_results_list(results)
    standings_text = format_standings_top_n(standings, 10)
    remaining = 10 - round_num

    return f"""🚨 RUNDISLIGA CUPDATE INCOMING 🚨

GAMEWEEK {gw} RESULTS (ROUND {round_num})

{results_list}

CURRENT STANDINGS (TOP 10):
{standings_text}

{remaining} ROUNDS REMAINING"""


def generate_not_cup_week_message(gw):
    """Generate 'not a cup week' message."""
    # Find next cup gameweek
    next_gw = None
    next_round = None
    for check_gw in range(gw + 1, 39):
        if check_gw in GAMEWEEK_TO_ROUND and check_gw not in NON_CUP_WEEKS:
            next_gw = check_gw
            next_round = GAMEWEEK_TO_ROUND[check_gw]
            break

    msg = f"""🚨 GAMEWEEK {gw} IS NOT A CUP GAMEWEEK 🚨
🚨 I REPEAT, GAMEWEEK {gw} IS NOT A CUP GAMEWEEK 🚨"""

    if next_gw:
        if isinstance(next_round, str):
            round_text = next_round
        else:
            round_text = f"ROUND {next_round}"
        msg += f"\n\nNEXT CUP ROUND: {round_text} (GW{next_gw})"

    return msg


def generate_knockout_reminder(gw, round_code):
    """Generate knockout round reminder."""
    deadline = get_gameweek_info(gw)

    round_names = {
        "QF1": "QUARTER-FINAL 1ST LEG",
        "QF2": "QUARTER-FINAL 2ND LEG",
        "SF1": "SEMI-FINAL 1ST LEG",
        "SF2": "SEMI-FINAL 2ND LEG",
        "FINAL": "THE FINAL",
        "PLAYOFF": "PLAYOFF"
    }

    round_name = round_names.get(round_code, round_code)

    return f"""🚨 RUNDISLIGA CUP REMINDER 🚨

GAMEWEEK {gw} IS THE {round_name}

DEADLINE: {deadline}

🚨 GOOD LUCK 🍀 🚨"""


def generate_knockout_results(gw, round_code):
    """Generate knockout round results."""
    results = get_results_for_gameweek(gw)
    results_list = format_results_list(results)

    round_names = {
        "QF1": "QUARTER-FINAL 1ST LEG",
        "QF2": "QUARTER-FINALS",
        "SF1": "SEMI-FINAL 1ST LEG",
        "SF2": "SEMI-FINALS",
        "FINAL": "FINAL",
        "PLAYOFF": "PLAYOFF"
    }

    round_name = round_names.get(round_code, round_code)

    return f"""🚨 RUNDISLIGA CUP {round_name} RESULTS 🚨

{results_list}

🚨 MORE DETAILS TO FOLLOW 🚨"""


def generate_group_complete_message(qualified_teams):
    """Generate group stage completion message."""
    qualified_list = "\n".join([f"🏆 {team.upper()}" for team in qualified_teams])

    return f"""🚨 RUNDISLIGA CUP GROUP STAGE COMPLETE 🚨

🚨 CONGRATULATIONS TO THE 8 TEAMS QUALIFYING FOR THE KNOCKOUT ROUNDS 🚨

{qualified_list}

QUARTER-FINAL DRAW COMING SOON

🚨 QUARTER-FINALS BEGIN GW33 (SAT APR 18, 2026) 🚨"""


def generate_playoff_announcement(tied_teams, points, spots_needed):
    """Generate playoff announcement if teams are tied."""
    teams_list = "\n".join([f"- {team.upper()}" for team in tied_teams])

    return f"""🚨 RUNDISLIGA CUP PLAYOFF ANNOUNCEMENT 🚨

{len(tied_teams)} TEAMS ARE TIED ON {points} POINTS FOR THE FINAL QUALIFICATION SPOT(S)

{teams_list}

🚨 THESE TEAMS WILL PLAY OFF ON GAMEWEEK 32 🚨

THE {spots_needed} TEAM(S) WITH THE HIGHEST FPL SCORE IN GW32 WILL QUALIFY FOR THE KNOCKOUT ROUNDS

🚨 THAT'S THE MAGIC OF THE PLAYOFFS, SO HARD TO PREDICT 🚨"""


def generate_final_announcement(team1, team2):
    """Generate final announcement."""
    return f"""🚨 RUNDISLIGA CUP FINAL ANNOUNCEMENT 🚨

🏆🏆🏆 THE FINAL IS SET 🏆🏆🏆

{team1.upper()} VS {team2.upper()}

GAMEWEEK 38 - SUN MAY 24, 2026
THE LAST DAY OF THE SEASON

🚨 MAY THE BEST MANAGER WIN 🚨"""


def generate_winner_message(winner_name, winner_team, score):
    """Generate cup winner announcement."""
    return f"""🚨🏆 RUNDISLIGA CUP 25/26 WINNER 🏆🚨

{winner_name.upper()}
{winner_team.upper()}

{score}

🏆🏆🏆 CONGRATULATIONS TO {winner_name.upper()} 🏆🏆🏆

THE 2025/26 RUNDISLIGA CUP CHAMPION

THANK YOU TO ALL 20 MANAGERS FOR ANOTHER GREAT CUP SEASON"""


# ============ MAIN ============

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: generate_whatsapp_message.py <command> [args]")
        print("")
        print("Commands:")
        print("  announcement       - Cup announcement message")
        print("  draw              - Draw complete message")
        print("  pre <gw>          - Pre-gameweek reminder")
        print("  post <gw>         - Post-gameweek results")
        print("  notcup <gw>       - Not a cup week message")
        sys.exit(1)

    command = sys.argv[1]

    if command == "announcement":
        print(generate_announcement_message())

    elif command == "draw":
        print(generate_draw_message())

    elif command == "pre":
        if len(sys.argv) < 3:
            print("Usage: generate_whatsapp_message.py pre <gameweek>")
            sys.exit(1)
        gw = int(sys.argv[2])
        print(generate_pre_gameweek_message(gw))

    elif command == "post":
        if len(sys.argv) < 3:
            print("Usage: generate_whatsapp_message.py post <gameweek>")
            sys.exit(1)
        gw = int(sys.argv[2])
        msg = generate_post_gameweek_message(gw)
        if msg:
            print(msg)
        else:
            print(f"No cup results for GW{gw}")

    elif command == "notcup":
        if len(sys.argv) < 3:
            print("Usage: generate_whatsapp_message.py notcup <gameweek>")
            sys.exit(1)
        gw = int(sys.argv[2])
        print(generate_not_cup_week_message(gw))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
