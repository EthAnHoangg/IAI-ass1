import sys
from pathlib import Path

import matplotlib.font_manager as fm
from PIL import Image, ImageDraw, ImageFont
from staticmap import CircleMarker, StaticMap

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tsp.problem import Location, clean_location_name, load_locations
from tsp.visualize import INK, SURFACE, lonlat_to_px

CSV_PATH = "locations.csv"
OUTPUT_PATH = "locations_basemap.png"

MAP_W, MAP_H = 1000, 900
LEGEND_W = 380
TITLE_H = 64
BADGE_R = 12
ANCHOR_R = 3
MIN_BADGE_GAP = 2 * (BADGE_R + 3) + 6  # badge diameter + halo + a little breathing room

MUTED = "#6b6a64"
MARKER = "#7c3aed"
OUTLINE = "#3d1d78"

BOLD = fm.findfont("DejaVu Sans:bold")
REGULAR = fm.findfont("DejaVu Sans")
title_font = ImageFont.truetype(BOLD, 22)
subtitle_font = ImageFont.truetype(REGULAR, 12)
legend_font = ImageFont.truetype(REGULAR, 13)
map_badge_font = ImageFont.truetype(BOLD, 12)
legend_badge_font = ImageFont.truetype(BOLD, 10)


def declutter(points: list[tuple[int, int]], min_gap: float) -> list[tuple[int, int]]:
    """Nudge points that sit closer than min_gap apart until none overlap."""
    pts = [list(p) for p in points]
    for _ in range(60):
        settled = True
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                dx, dy = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
                dist = (dx * dx + dy * dy) ** 0.5 or 0.01
                if dist < min_gap:
                    push = (min_gap - dist) / 2
                    ox, oy = dx / dist * push, dy / dist * push
                    pts[i][0] -= ox
                    pts[i][1] -= oy
                    pts[j][0] += ox
                    pts[j][1] += oy
                    settled = False
        if settled:
            break
    return [(round(x), round(y)) for x, y in pts]


def draw_badge(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, radius: int, fnt: ImageFont.FreeTypeFont) -> None:
    halo_r = radius + 3
    draw.ellipse((x - halo_r, y - halo_r, x + halo_r, y + halo_r), outline="white", width=3)
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=MARKER, outline=OUTLINE, width=2)
    box = draw.textbbox((0, 0), label, font=fnt)
    draw.text((x - (box[2] - box[0]) / 2 - box[0], y - (box[3] - box[1]) / 2 - box[1]), label, fill="white", font=fnt)


def build_map(locations: list[Location]) -> Image.Image:
    m = StaticMap(MAP_W, MAP_H, padding_x=40, padding_y=40)
    for loc in locations:
        # Small anchor dot at the true coordinate; badges (drawn after render,
        # possibly nudged by declutter()) are drawn on top separately.
        m.add_marker(CircleMarker((loc.lon, loc.lat), MARKER, ANCHOR_R * 2))

    image = m.render().convert("RGB")
    draw = ImageDraw.Draw(image)

    true_pts = [lonlat_to_px(m, loc.lon, loc.lat) for loc in locations]
    badge_pts = declutter(true_pts, MIN_BADGE_GAP)

    for i, (true_pt, pos) in enumerate(zip(true_pts, badge_pts), start=1):
        draw.ellipse((true_pt[0] - ANCHOR_R, true_pt[1] - ANCHOR_R, true_pt[0] + ANCHOR_R, true_pt[1] + ANCHOR_R), outline="white", width=1)
        if pos != true_pt:
            draw.line([true_pt, pos], fill=OUTLINE, width=1)
        draw_badge(draw, pos[0], pos[1], str(i), BADGE_R, map_badge_font)

    return image


def build_canvas(locations: list[Location]) -> Image.Image:
    canvas = Image.new("RGB", (MAP_W + LEGEND_W, TITLE_H + MAP_H), SURFACE)
    draw = ImageDraw.Draw(canvas)

    draw.text((24, 16), "Hanoi Old Quarter — Food & Drink Spots", fill=INK, font=title_font)
    draw.text((24, 44), f"{len(locations)} locations · basemap © OpenStreetMap contributors", fill=MUTED, font=subtitle_font)
    canvas.paste(build_map(locations), (0, TITLE_H))

    x, y = MAP_W + 20, TITLE_H + 16
    row_h = min((MAP_H - 24) / len(locations), 40)
    for i, loc in enumerate(locations, start=1):
        draw_badge(draw, x + BADGE_R, round(y + BADGE_R), str(i), BADGE_R, legend_badge_font)
        draw.text((x + 2 * BADGE_R + 12, y + BADGE_R - 8), clean_location_name(loc.name), fill=INK, font=legend_font)
        y += row_h

    return canvas


if __name__ == "__main__":
    build_canvas(load_locations(CSV_PATH)).save(OUTPUT_PATH)
    print(f"Saved map to {OUTPUT_PATH}")
