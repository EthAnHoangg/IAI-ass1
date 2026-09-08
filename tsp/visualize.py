from __future__ import annotations

from math import cos, log, pi, tan

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from staticmap import CircleMarker, Line, StaticMap

from tsp.problem import Location, TSPProblem, clean_location_name

SA_COLOR = "#2a78d6"
GA_COLOR = "#d6552a"
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#898781"
LINE = "#e1e0d9"


def lonlat_to_px(static_map: StaticMap, lon: float, lat: float) -> tuple[int, int]:
    scale = 2**static_map.zoom
    x_tile = (lon + 180.0) / 360.0 * scale
    y_tile = (1 - log(tan(lat * pi / 180) + 1 / cos(lat * pi / 180)) / pi) / 2 * scale
    return (
        round((x_tile - static_map.x_center) * static_map.tile_size + static_map.width / 2),
        round((y_tile - static_map.y_center) * static_map.tile_size + static_map.height / 2),
    )


def plot_convergence(
    sa_history: list[float],
    ga_history: list[float],
    output_path: str,
    ga_evals_per_generation: int,
) -> None:
    sa_x_values = list(range(len(sa_history)))
    ga_x_values = [i * ga_evals_per_generation for i in range(len(ga_history))]

    fig, ax = plt.subplots(figsize=(9, 6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.plot(sa_x_values, sa_history, color=SA_COLOR, label="Simulated Annealing", linewidth=1.5)
    ax.plot(ga_x_values, ga_history, color=GA_COLOR, label="Genetic Algorithm", linewidth=1.5)
    ax.set_title("Convergence: best cost so far (mean over trials)", color=INK, fontsize=13)
    ax.set_xlabel("Cost evaluations", color=MUTED)
    ax.set_ylabel("Tour cost (meters)", color=MUTED)
    ax.tick_params(colors=MUTED)
    for spine in ax.spines.values():
        spine.set_color(LINE)
    ax.grid(True, color=LINE, linewidth=0.8)
    ax.legend(facecolor=SURFACE, edgecolor=LINE, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def ordered_tour_locations(problem: TSPProblem, tour: list[int], close_loop: bool = True) -> list[Location]:
    ordered = [problem.locations[i] for i in tour]
    if close_loop and ordered:
        ordered.append(ordered[0])
    return ordered


def plot_route(
    problem: TSPProblem,
    tour: list[int],
    title: str,
    output_path: str,
    route_coords: list[tuple[float, float]] | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(11, 9), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    if route_coords:
        lons = [lon for lon, _ in route_coords]
        lats = [lat for _, lat in route_coords]
    else:
        ordered = tour + [tour[0]]
        lons = [problem.locations[i].lon for i in ordered]
        lats = [problem.locations[i].lat for i in ordered]

    ax.plot(lons, lats, color=SA_COLOR, linewidth=1.2, zorder=2)
    stop_lons = [problem.locations[i].lon for i in tour]
    stop_lats = [problem.locations[i].lat for i in tour]
    ax.scatter(
        stop_lons, stop_lats, c=SA_COLOR, s=110, edgecolors=SURFACE, linewidths=0.8, zorder=3
    )

    for order, idx in enumerate(tour):
        loc = problem.locations[idx]
        ax.annotate(
            f"{order + 1}. {clean_location_name(loc.name)}",
            (loc.lon, loc.lat),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=7.5,
            color=INK,
            zorder=4,
        )

    ax.set_title(title, color=INK, fontsize=14, pad=14)
    ax.set_xlabel("Longitude", color=MUTED)
    ax.set_ylabel("Latitude", color=MUTED)
    ax.ticklabel_format(useOffset=False, style="plain", axis="x")
    ax.tick_params(colors=MUTED)
    ax.margins(x=0.18, y=0.08)
    for spine in ax.spines.values():
        spine.set_color(LINE)
    ax.grid(True, color=LINE, linewidth=0.8, zorder=0)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, facecolor=SURFACE)
    plt.close(fig)


def plot_route_map(
    problem: TSPProblem,
    tour: list[int],
    title: str,
    output_path: str,
    route_coords: list[tuple[float, float]],
    width: int = 1100,
    height: int = 900,
) -> None:
    import matplotlib.font_manager as fm
    from PIL import Image, ImageDraw, ImageFont

    static_map = StaticMap(width, height, padding_x=50, padding_y=50)
    static_map.add_line(Line(route_coords, SA_COLOR, 4))

    for idx in tour:
        loc = problem.locations[idx]
        static_map.add_marker(CircleMarker((loc.lon, loc.lat), SA_COLOR, 18))
        static_map.add_marker(CircleMarker((loc.lon, loc.lat), SURFACE, 11))

    image = static_map.render().convert("RGB")
    draw = ImageDraw.Draw(image)
    badge_font = ImageFont.truetype(fm.findfont("DejaVu Sans:bold"), 11)

    for order, idx in enumerate(tour):
        x, y = lonlat_to_px(static_map, problem.locations[idx].lon, problem.locations[idx].lat)
        label = str(order + 1)
        box = draw.textbbox((0, 0), label, font=badge_font)
        text_x = x - (box[2] - box[0]) / 2 - box[0]
        text_y = y - (box[3] - box[1]) / 2 - box[1]
        draw.text((text_x, text_y), label, fill=SURFACE, font=badge_font)

    header_h = 48
    canvas = Image.new("RGB", (width, height + header_h), SURFACE)
    canvas.paste(image, (0, header_h))
    header_draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(fm.findfont("DejaVu Sans:bold"), 20)
    subtitle_font = ImageFont.truetype(fm.findfont("DejaVu Sans"), 11)
    header_draw.text((16, 10), title, fill=INK, font=title_font)
    header_draw.text(
        (16, 32),
        "Walking route via OSRM · basemap © OpenStreetMap contributors",
        fill=MUTED,
        font=subtitle_font,
    )
    canvas.save(output_path)
