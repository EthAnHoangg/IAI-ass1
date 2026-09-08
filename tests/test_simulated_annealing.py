import math
import random

from tsp.simulated_annealing import (
    SAConfig,
    initial_temperature,
    run_simulated_annealing,
    swap_neighbor,
)


def test_swap_neighbor_is_a_permutation_that_differs_from_input():
    rng = random.Random(1)
    tour = [0, 1, 2, 3]
    neighbor = swap_neighbor(tour, rng)
    assert sorted(neighbor) == [0, 1, 2, 3]
    assert neighbor != tour


def test_swap_neighbor_changes_exactly_two_positions():
    rng = random.Random(1)
    tour = [0, 1, 2, 3]
    neighbor = swap_neighbor(tour, rng)
    diffs = sum(1 for a, b in zip(tour, neighbor) if a != b)
    assert diffs == 2


def test_initial_temperature_is_average_edge_cost(square_problem):
    # perimeter tour: all 4 edges have length 1.0
    assert math.isclose(initial_temperature(square_problem, [0, 1, 2, 3]), 1.0)


def test_sa_finds_optimal_tour_on_square(square_problem):
    config = SAConfig(alpha=0.9, min_temperature_fraction=1e-4, max_iterations=2000)
    result = run_simulated_annealing(square_problem, config, random.Random(42))
    assert math.isclose(result.best_cost, 4.0, rel_tol=1e-9)
    assert sorted(result.best_tour) == [0, 1, 2, 3]


def test_sa_is_reproducible_with_same_seed(square_problem):
    config = SAConfig(alpha=0.9, min_temperature_fraction=1e-4, max_iterations=500)
    result_a = run_simulated_annealing(square_problem, config, random.Random(7))
    result_b = run_simulated_annealing(square_problem, config, random.Random(7))
    assert result_a.best_tour == result_b.best_tour
    assert result_a.cost_history == result_b.cost_history


def test_sa_cost_history_is_non_increasing(square_problem):
    config = SAConfig(alpha=0.9, min_temperature_fraction=1e-4, max_iterations=500)
    result = run_simulated_annealing(square_problem, config, random.Random(3))
    assert all(
        result.cost_history[i] >= result.cost_history[i + 1]
        for i in range(len(result.cost_history) - 1)
    )
