from __future__ import annotations

import csv
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lon: float


def load_locations(path: str) -> list[Location]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Location(
                name=row["location_name"],
                lat=float(row["latitude"]),
                lon=float(row["longitude"]),
            )
            for row in reader
        ]


def clean_location_name(name: str) -> str:
    return name.split(" - ")[0]


def load_distance_matrix(path: str) -> list[list[float]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header row: "", name1, name2, ...
        return [[float(v) for v in row[1:]] for row in reader]


class TSPProblem:
    def __init__(self, locations: list[Location], distance_matrix: list[list[float]]):
        if len(locations) != len(distance_matrix):
            raise ValueError("locations and distance_matrix size mismatch")
        self.locations = locations
        self.distance_matrix = distance_matrix
        self.n = len(locations)

    def tour_cost(self, tour: list[int]) -> float:
        n = len(tour)
        return sum(
            self.distance_matrix[tour[i]][tour[(i + 1) % n]] for i in range(n)
        )

    def random_tour(self, rng: random.Random) -> list[int]:
        tour = list(range(self.n))
        rng.shuffle(tour)
        return tour
