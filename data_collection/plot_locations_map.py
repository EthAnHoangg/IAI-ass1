import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tsp.problem import Location, clean_location_name, load_locations
from tsp.visualize import INK, LINE, MUTED, SA_COLOR, SURFACE

CSV_PATH = "locations.csv"
OUTPUT_PATH = "locations_map.png"


def plot_map(locations: list[Location], output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 9), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    lons = [loc.lon for loc in locations]
    lats = [loc.lat for loc in locations]
    ax.scatter(lons, lats, c=SA_COLOR, s=110, edgecolors=SURFACE, linewidths=0.8, zorder=3)

    for loc in locations:
        ax.annotate(
            clean_location_name(loc.name),
            (loc.lon, loc.lat),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=7.5,
            color=INK,
            zorder=4,
        )

    ax.set_title("Hanoi Old Quarter Locations", color=INK, fontsize=14, pad=14)
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
    print(f"Saved map to {output_path}")


if __name__ == "__main__":
    plot_map(load_locations(CSV_PATH), OUTPUT_PATH)
