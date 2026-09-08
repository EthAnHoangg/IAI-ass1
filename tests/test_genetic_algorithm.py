import math
import random

from tsp.genetic_algorithm import (
    GAConfig,
    order_crossover,
    run_genetic_algorithm,
    swap_mutate,
    tournament_select,
)


def test_order_crossover_produces_a_valid_permutation():
    rng = random.Random(1)
    parent_a = [0, 1, 2, 3, 4]
    parent_b = [4, 3, 2, 1, 0]
    child = order_crossover(parent_a, parent_b, rng)
    assert sorted(child) == [0, 1, 2, 3, 4]


def test_order_crossover_preserves_the_sliced_segment_from_parent_a(monkeypatch):
    parent_a = [0, 1, 2, 3, 4]
    parent_b = [4, 3, 2, 1, 0]
    rng = random.Random(2)
    monkeypatch.setattr(rng, "sample", lambda population, k: [1, 3])
    child = order_crossover(parent_a, parent_b, rng)
    assert child[1:4] == parent_a[1:4]
    assert sorted(child) == [0, 1, 2, 3, 4]


def test_swap_mutate_changes_exactly_two_positions_and_stays_a_permutation():
    rng = random.Random(3)
    tour = [0, 1, 2, 3]
    mutated = swap_mutate(tour, rng)
    diffs = sum(1 for a, b in zip(tour, mutated) if a != b)
    assert diffs == 2
    assert sorted(mutated) == sorted(tour)


def test_tournament_select_with_full_population_picks_the_fittest():
    population = [[0, 1, 2], [2, 1, 0], [1, 0, 2]]
    fitnesses = [5.0, 1.0, 3.0]
    rng = random.Random(4)
    selected = tournament_select(population, fitnesses, k=3, rng=rng)
    assert selected == population[1]


def test_ga_finds_optimal_tour_on_square(square_problem):
    config = GAConfig(population_size=20, max_generations=100, no_improvement_stop=20)
    result = run_genetic_algorithm(square_problem, config, random.Random(0))
    assert math.isclose(result.best_cost, 4.0, rel_tol=1e-9)
    assert sorted(result.best_tour) == [0, 1, 2, 3]


def test_ga_is_reproducible_with_same_seed(square_problem):
    config = GAConfig(population_size=20, max_generations=30, no_improvement_stop=30)
    result_a = run_genetic_algorithm(square_problem, config, random.Random(9))
    result_b = run_genetic_algorithm(square_problem, config, random.Random(9))
    assert result_a.best_tour == result_b.best_tour
    assert result_a.cost_history == result_b.cost_history


def test_ga_cost_history_is_non_increasing(square_problem):
    config = GAConfig(population_size=20, max_generations=30, no_improvement_stop=30)
    result = run_genetic_algorithm(square_problem, config, random.Random(5))
    assert all(
        result.cost_history[i] >= result.cost_history[i + 1]
        for i in range(len(result.cost_history) - 1)
    )
