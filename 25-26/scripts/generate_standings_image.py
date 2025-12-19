#!/usr/bin/env python3
"""Generate styled standings images for Rundisliga Cup."""

import sqlite3
import requests
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
from collections import defaultdict

OUTPUT_DIR = Path(__file__).parent.parent / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(__file__).parent.parent / "db" / "fantasy_cup.db"

# Color scheme (matching results image)
COLORS = {
    "bg_gradient_top": (25, 25, 112),      # Midnight blue
    "bg_gradient_bottom": (75, 0, 130),     # Indigo
    "header_bg": (138, 43, 226),            # Blue violet
    "qualify": (46, 204, 113),              # Green - qualifying positions
    "danger": (231, 76, 60),                # Red - bottom positions
    "mid": (241, 196, 15),                  # Yellow - mid table
    "text_white": (255, 255, 255),
    "text_light": (200, 200, 220),
    "row_odd": (40, 40, 80, 180),           # Semi-transparent
    "row_even": (60, 60, 100, 180),
    "gold": (255, 215, 0),
    "silver": (192, 192, 192),
    "cutoff_line": (255, 215, 0),           # Gold line at position 8
}

LEAGUE_ID = "156772"


def create_gradient(width, height, color1, color2):
    """Create a vertical gradient background."""
    img = Image.new('RGB', (width, height))
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    return img


def get_font(size, bold=False):
    """Get a font, falling back to default if needed."""
    try:
        if bold:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size, index=1)
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default()


def get_managers_from_db():
    """Get all managers from database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT fpl_id, name, team_name FROM managers")
    managers = {row['fpl_id']: dict(row) for row in cursor.fetchall()}
    conn.close()
    return managers


def calculate_standings_from_db(through_round=None):
    """Calculate standings from cup_fixtures table."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT * FROM cup_fixtures
        WHERE round <= 10 AND home_score IS NOT NULL AND away_score IS NOT NULL
    """
    if through_round:
        query += f" AND round <= {through_round}"

    cursor.execute(query)
    matches = cursor.fetchall()
    conn.close()

    standings = defaultdict(lambda: {
        'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
        'points': 0, 'fpl_total': 0
    })

    for match in matches:
        home_id = match['home_manager_id']
        away_id = match['away_manager_id']
        home_score = match['home_score']
        away_score = match['away_score']

        # Update played count
        standings[home_id]['played'] += 1
        standings[away_id]['played'] += 1

        # Update FPL totals
        standings[home_id]['fpl_total'] += home_score
        standings[away_id]['fpl_total'] += away_score

        # Determine result
        if home_score > away_score:
            standings[home_id]['won'] += 1
            standings[home_id]['points'] += 3
            standings[away_id]['lost'] += 1
        elif away_score > home_score:
            standings[away_id]['won'] += 1
            standings[away_id]['points'] += 3
            standings[home_id]['lost'] += 1
        else:
            standings[home_id]['drawn'] += 1
            standings[away_id]['drawn'] += 1
            standings[home_id]['points'] += 1
            standings[away_id]['points'] += 1

    return standings


def calculate_standings_from_h2h(through_gameweek=None):
    """Calculate standings from FPL H2H league data (for testing before cup starts)."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })

    # Get H2H standings
    url = f"https://fantasy.premierleague.com/api/leagues-h2h/{LEAGUE_ID}/standings/"
    response = session.get(url)
    data = response.json()

    standings_list = []
    for entry in data.get('standings', {}).get('results', []):
        standings_list.append({
            'fpl_id': entry['entry'],
            'name': entry['player_name'],
            'team_name': entry['entry_name'],
            'played': entry['matches_played'],
            'won': entry['matches_won'],
            'drawn': entry['matches_drawn'],
            'lost': entry['matches_lost'],
            'points': entry['total'],  # H2H points (3 for win, 1 for draw)
            'fpl_total': entry.get('points_for', 0),  # Total FPL points scored
        })

    return standings_list


def generate_standings_image(standings_data=None, title_suffix="", round_num=None):
    """Generate a styled standings image."""

    if standings_data is None:
        # Try to get from H2H league for testing
        standings_data = calculate_standings_from_h2h()

    if not standings_data:
        print("No standings data found")
        return None

    # Sort by points, then FPL total
    standings_data.sort(key=lambda x: (-x['points'], -x['fpl_total']))

    # Image dimensions
    width = 900
    header_height = 120
    column_header_height = 40
    row_height = 45
    footer_height = 50
    height = header_height + column_header_height + (len(standings_data) * row_height) + footer_height

    # Create gradient background
    img = create_gradient(width, height, COLORS["bg_gradient_top"], COLORS["bg_gradient_bottom"])
    draw = ImageDraw.Draw(img, 'RGBA')

    # Fonts
    font_title = get_font(38, bold=True)
    font_subtitle = get_font(18)
    font_header = get_font(14, bold=True)
    font_row = get_font(14)
    font_row_bold = get_font(14, bold=True)
    font_footer = get_font(12)

    # Header
    title = f"RUNDISLIGA CUP STANDINGS{title_suffix}"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 25), title, fill=COLORS["gold"], font=font_title)

    subtitle = "25/26 SEASON"
    if round_num:
        subtitle = f"AFTER ROUND {round_num}"
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_width = sub_bbox[2] - sub_bbox[0]
    draw.text(((width - sub_width) // 2, 75), subtitle, fill=COLORS["text_light"], font=font_subtitle)

    # Column positions
    col_pos = 30
    col_name = 70
    col_team = 250
    col_p = 500
    col_w = 550
    col_d = 600
    col_l = 650
    col_pts = 710
    col_fpl = 790

    # Column headers
    y_offset = header_height
    draw.rectangle([(20, y_offset), (width - 20, y_offset + column_header_height - 5)],
                   fill=(80, 80, 120, 200), outline=None)

    draw.text((col_pos, y_offset + 10), "#", fill=COLORS["text_white"], font=font_header)
    draw.text((col_name, y_offset + 10), "MANAGER", fill=COLORS["text_white"], font=font_header)
    draw.text((col_team, y_offset + 10), "TEAM", fill=COLORS["text_white"], font=font_header)
    draw.text((col_p, y_offset + 10), "P", fill=COLORS["text_white"], font=font_header)
    draw.text((col_w, y_offset + 10), "W", fill=COLORS["text_white"], font=font_header)
    draw.text((col_d, y_offset + 10), "D", fill=COLORS["text_white"], font=font_header)
    draw.text((col_l, y_offset + 10), "L", fill=COLORS["text_white"], font=font_header)
    draw.text((col_pts, y_offset + 10), "PTS", fill=COLORS["text_white"], font=font_header)
    draw.text((col_fpl, y_offset + 10), "FPL", fill=COLORS["text_white"], font=font_header)

    y_offset += column_header_height

    # Draw standings rows
    for i, team in enumerate(standings_data):
        pos = i + 1

        # Row background
        row_color = COLORS["row_odd"] if i % 2 == 0 else COLORS["row_even"]
        draw.rectangle([(20, y_offset), (width - 20, y_offset + row_height - 3)],
                      fill=row_color, outline=None)

        # Qualification indicator (left bar)
        if pos <= 8:
            # Qualifying positions - green bar
            draw.rectangle([(20, y_offset), (25, y_offset + row_height - 3)],
                          fill=COLORS["qualify"], outline=None)

        # Position color
        if pos <= 8:
            pos_color = COLORS["qualify"]
        else:
            pos_color = COLORS["text_light"]

        # Draw row data
        draw.text((col_pos, y_offset + 12), str(pos), fill=pos_color, font=font_row_bold)

        name = team.get('name', 'Unknown')[:20]
        draw.text((col_name, y_offset + 12), name, fill=COLORS["text_white"], font=font_row)

        team_name = team.get('team_name', '')[:25]
        draw.text((col_team, y_offset + 12), team_name, fill=COLORS["text_light"], font=font_row)

        draw.text((col_p, y_offset + 12), str(team['played']), fill=COLORS["text_white"], font=font_row)
        draw.text((col_w, y_offset + 12), str(team['won']), fill=COLORS["text_white"], font=font_row)
        draw.text((col_d, y_offset + 12), str(team['drawn']), fill=COLORS["text_white"], font=font_row)
        draw.text((col_l, y_offset + 12), str(team['lost']), fill=COLORS["text_white"], font=font_row)
        draw.text((col_pts, y_offset + 12), str(team['points']), fill=COLORS["gold"], font=font_row_bold)
        draw.text((col_fpl, y_offset + 12), str(team['fpl_total']), fill=COLORS["text_light"], font=font_row)

        y_offset += row_height

        # Draw qualification cutoff line after position 8
        if pos == 8:
            draw.line([(20, y_offset - 2), (width - 20, y_offset - 2)],
                     fill=COLORS["cutoff_line"], width=2)

    # Legend
    legend_y = y_offset + 10
    draw.rectangle([(30, legend_y), (35, legend_y + 15)], fill=COLORS["qualify"], outline=None)
    draw.text((45, legend_y), "Qualified for Knockout Rounds", fill=COLORS["text_light"], font=font_footer)

    # Footer
    footer_text = f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} | fantasy.premierleague.com"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    footer_width = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_width) // 2, height - 30), footer_text,
             fill=COLORS["text_light"], font=font_footer)

    # Save image
    filename = "standings"
    if round_num:
        filename = f"standings_round{round_num}"
    output_path = OUTPUT_DIR / f"{filename}.png"
    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")

    return output_path


if __name__ == "__main__":
    import sys
    round_num = int(sys.argv[1]) if len(sys.argv) > 1 else None
    generate_standings_image(round_num=round_num)
