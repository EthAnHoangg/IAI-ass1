import math

import pytest

from tsp.problem import Location, TSPProblem


@pytest.fixture
def square_problem() -> TSPProblem:
    """4 cities at unit-square corners; optimal closed tour = perimeter = 4.0."""
    coords = [(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)]
    locations = [Location(name, lat, lon) for name, (lat, lon) in zip("ABCD", coords)]
    matrix = [[math.dist(coords[i], coords[j]) for j in range(4)] for i in range(4)]
    return TSPProblem(locations, matrix)
