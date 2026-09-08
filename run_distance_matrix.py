import os

from tsp.distances import (
    build_osrm_url,
    fetch_distance_matrix,
    fill_missing_with_haversine,
    save_distance_matrix,
)
from tsp.problem import load_locations

LOCATIONS_PATH = "data_collection/locations.csv"
DISTANCE_MATRIX_PATH = "data/distance_matrix.csv"
DISTANCE_MATRIX_META_PATH = "data/distance_matrix_meta.json"


def main() -> None:
    locations = load_locations(LOCATIONS_PATH)
    print(f"Fetching walking-distance matrix for {len(locations)} locations from OSRM...")
    raw_matrix = fetch_distance_matrix(locations)
    matrix = fill_missing_with_haversine(raw_matrix, locations)
    os.makedirs(os.path.dirname(DISTANCE_MATRIX_PATH), exist_ok=True)
    save_distance_matrix(
        matrix,
        locations,
        DISTANCE_MATRIX_PATH,
        DISTANCE_MATRIX_META_PATH,
        build_osrm_url(locations),
    )
    print(f"Saved distance matrix to {DISTANCE_MATRIX_PATH}")


if __name__ == "__main__":
    main()
