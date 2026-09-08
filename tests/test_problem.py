import csv
import math
import random

from tsp.problem import Location, clean_location_name, load_distance_matrix, load_locations


def test_tour_cost_optimal_square(square_problem):
    assert math.isclose(square_problem.tour_cost([0, 1, 2, 3]), 4.0)


def test_tour_cost_crossing_diagonal_is_worse(square_problem):
    crossing_cost = square_problem.tour_cost([0, 2, 1, 3])
    assert crossing_cost > square_problem.tour_cost([0, 1, 2, 3])


def test_tour_cost_is_rotation_invariant(square_problem):
    assert math.isclose(
        square_problem.tour_cost([0, 1, 2, 3]),
        square_problem.tour_cost([1, 2, 3, 0]),
    )


def test_random_tour_is_a_permutation(square_problem):
    tour = square_problem.random_tour(random.Random(42))
    assert sorted(tour) == [0, 1, 2, 3]


def test_load_locations(tmp_path):
    csv_path = tmp_path / "locations.csv"
    csv_path.write_text(
        "location_name,latitude,longitude,source_note\n"
        "Spot A,21.03,105.85,note\n"
        "Spot B,21.04,105.86,note\n",
        encoding="utf-8",
    )
    assert load_locations(str(csv_path)) == [
        Location("Spot A", 21.03, 105.85),
        Location("Spot B", 21.04, 105.86),
    ]


def test_clean_location_name_drops_marketing_suffix():
    assert clean_location_name("Nộm Bò Khô Long Vi Dung - Địa chỉ nộm...") == "Nộm Bò Khô Long Vi Dung"


def test_clean_location_name_leaves_plain_names_unchanged():
    assert clean_location_name("Xôi Yến") == "Xôi Yến"


def test_load_distance_matrix(tmp_path):
    csv_path = tmp_path / "distance_matrix.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["", "Spot A", "Spot B"])
        writer.writerow(["Spot A", "0.0", "5.0"])
        writer.writerow(["Spot B", "5.0", "0.0"])
    assert load_distance_matrix(str(csv_path)) == [[0.0, 5.0], [5.0, 0.0]]
