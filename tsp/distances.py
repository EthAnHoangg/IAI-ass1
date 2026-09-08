from __future__ import annotations

import csv
import json
import math
from datetime import UTC, datetime

import requests

from tsp.problem import Location

OSRM_BASE_URL = "https://router.project-osrm.org/table/v1/foot"
OSRM_ROUTE_BASE_URL = "https://router.project-osrm.org/route/v1/foot"


def build_osrm_url(locations: list[Location], base_url: str = OSRM_BASE_URL) -> str:
    coords = ";".join(f"{loc.lon},{loc.lat}" for loc in locations)
    return f"{base_url}/{coords}?annotations=distance"


def fetch_distance_matrix(
    locations: list[Location], base_url: str = OSRM_BASE_URL, timeout: float = 30.0
) -> list[list[float | None]]:
    url = build_osrm_url(locations, base_url)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "Ok":
        raise RuntimeError(f"OSRM error: {payload.get('code')} - {payload.get('message', '')}")
    return payload["distances"]


def build_osrm_route_url(locations: list[Location], base_url: str = OSRM_ROUTE_BASE_URL) -> str:
    coords = ";".join(f"{loc.lon},{loc.lat}" for loc in locations)
    return f"{base_url}/{coords}?overview=full&geometries=geojson&steps=false"


def fetch_route_geometry(
    locations: list[Location],
    base_url: str = OSRM_ROUTE_BASE_URL,
    timeout: float = 30.0,
) -> list[tuple[float, float]]:
    if len(locations) < 2:
        if not locations:
            return []
        loc = locations[0]
        return [(loc.lon, loc.lat)]

    url = build_osrm_route_url(locations, base_url)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != "Ok":
        raise RuntimeError(f"OSRM error: {payload.get('code')} - {payload.get('message', '')}")
    coordinates = payload["routes"][0]["geometry"]["coordinates"]
    return [(float(lon), float(lat)) for lon, lat in coordinates]


def haversine_distance(a: Location, b: Location) -> float:
    radius_m = 6_371_000.0
    lat1, lon1, lat2, lon2 = map(math.radians, (a.lat, a.lon, b.lat, b.lon))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius_m * math.asin(math.sqrt(h))


def fill_missing_with_haversine(
    matrix: list[list[float | None]], locations: list[Location]
) -> list[list[float]]:
    filled = []
    for i, row in enumerate(matrix):
        filled_row = []
        for j, value in enumerate(row):
            if value is None:
                fallback = haversine_distance(locations[i], locations[j])
                print(
                    f"Warning: OSRM had no route for "
                    f"'{locations[i].name}' -> '{locations[j].name}'; "
                    f"using haversine fallback ({fallback:.1f}m)"
                )
                filled_row.append(fallback)
            else:
                filled_row.append(float(value))
        filled.append(filled_row)
    return filled


def save_distance_matrix(
    matrix: list[list[float]],
    locations: list[Location],
    csv_path: str,
    meta_path: str,
    source_url: str,
) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([""] + [loc.name for loc in locations])
        for loc, row in zip(locations, matrix):
            writer.writerow([loc.name] + row)

    meta = {
        "fetched_at": datetime.now(UTC).isoformat(),
        "source_url": source_url,
        "profile": "foot",
        "n_locations": len(locations),
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
