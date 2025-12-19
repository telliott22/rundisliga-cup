#!/usr/bin/env python3
"""Generate styled results images for gameweek H2H matches."""

import requests
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent.parent / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color scheme
COLORS = {
    "bg_gradient_top": (25, 25, 112),      # Midnight blue
    "bg_gradient_bottom": (75, 0, 130),     # Indigo
    "header_bg": (138, 43, 226),            # Blue violet
    "win": (46, 204, 113),                  # Green
    "lose": (231, 76, 60),                  # Red
    "draw": (241, 196, 15),                 # Yellow
    "text_white": (255, 255, 255),
    "text_light": (200, 200, 220),
    "row_odd": (40, 40, 80, 180),           # Semi-transparent
    "row_even": (60, 60, 100, 180),
    "gold": (255, 215, 0),
    "silver": (192, 192, 192),
}

LEAGUE_ID = "156772"


def fetch_gameweek_results(gameweek):
    """Fetch H2H results for a gameweek."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })

    url = f"https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{LEAGUE_ID}/?event={gameweek}&page=1"
    response = session.get(url)
    return response.json().get("results", [])


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


def generate_results_image(gameweek, matches=None):
    """Generate a styled results image for a gameweek."""

    if matches is None:
        matches = fetch_gameweek_results(gameweek)

    if not matches:
        print(f"No matches found for GW{gameweek}")
        return None

    # Image dimensions - increased row height for team names
    width = 800
    row_height = 80  # Increased to fit team name
    header_height = 120
    footer_height = 50
    height = header_height + (len(matches) * row_height) + footer_height

    # Create gradient background
    img = create_gradient(width, height, COLORS["bg_gradient_top"], COLORS["bg_gradient_bottom"])
    draw = ImageDraw.Draw(img, 'RGBA')

    # Fonts
    font_title = get_font(42, bold=True)
    font_subtitle = get_font(20)
    font_name = get_font(20)
    font_team = get_font(14)  # Smaller font for team names
    font_score = get_font(32, bold=True)
    font_footer = get_font(14)

    # Header
    title = f"GAMEWEEK {gameweek} RESULTS"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 25), title, fill=COLORS["gold"], font=font_title)

    subtitle = "RUNDISLIGA CUP 25/26"
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_width = sub_bbox[2] - sub_bbox[0]
    draw.text(((width - sub_width) // 2, 75), subtitle, fill=COLORS["text_light"], font=font_subtitle)

    # Draw matches
    y_offset = header_height

    for i, match in enumerate(matches):
        p1 = match.get("entry_1_player_name", "???")
        t1 = match.get("entry_1_name", "")  # Team name
        s1 = match.get("entry_1_points", 0) or 0
        p2 = match.get("entry_2_player_name", "???")
        t2 = match.get("entry_2_name", "")  # Team name
        s2 = match.get("entry_2_points", 0) or 0

        # Row background
        row_color = COLORS["row_odd"] if i % 2 == 0 else COLORS["row_even"]
        draw.rectangle([(20, y_offset), (width - 20, y_offset + row_height - 5)],
                      fill=row_color, outline=None)

        # Determine winner colors
        if s1 > s2:
            color1, color2 = COLORS["win"], COLORS["lose"]
        elif s2 > s1:
            color1, color2 = COLORS["lose"], COLORS["win"]
        else:
            color1, color2 = COLORS["draw"], COLORS["draw"]

        # Player 1 name and team (left aligned)
        draw.text((40, y_offset + 10), p1[:22], fill=color1, font=font_name)
        draw.text((40, y_offset + 35), t1[:28], fill=COLORS["text_light"], font=font_team)

        # Score in center
        score_text = f"{s1}  -  {s2}"
        score_bbox = draw.textbbox((0, 0), score_text, font=font_score)
        score_width = score_bbox[2] - score_bbox[0]
        draw.text(((width - score_width) // 2, y_offset + 20), score_text,
                 fill=COLORS["text_white"], font=font_score)

        # Player 2 name and team (right aligned)
        p2_bbox = draw.textbbox((0, 0), p2[:22], font=font_name)
        p2_width = p2_bbox[2] - p2_bbox[0]
        draw.text((width - 40 - p2_width, y_offset + 10), p2[:22], fill=color2, font=font_name)

        t2_bbox = draw.textbbox((0, 0), t2[:28], font=font_team)
        t2_width = t2_bbox[2] - t2_bbox[0]
        draw.text((width - 40 - t2_width, y_offset + 35), t2[:28], fill=COLORS["text_light"], font=font_team)

        y_offset += row_height

    # Footer
    footer_text = f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} | fantasy.premierleague.com"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    footer_width = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_width) // 2, height - 35), footer_text,
             fill=COLORS["text_light"], font=font_footer)

    # Save image
    output_path = OUTPUT_DIR / f"gw{gameweek}_results.png"
    img.save(output_path, "PNG")
    print(f"Saved: {output_path}")

    return output_path


if __name__ == "__main__":
    import sys
    gw = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    generate_results_image(gw)
