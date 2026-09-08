from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from tsp.problem import TSPProblem


@dataclass
class SAConfig:
    alpha: float = 0.9995
    min_temperature_fraction: float = 1e-4
    max_iterations: int = 20_000


@dataclass
class SAResult:
    best_tour: list[int]
    best_cost: float
    cost_history: list[float]
    iterations: int
    runtime_seconds: float


def initial_temperature(problem: TSPProblem, tour: list[int]) -> float:
    return problem.tour_cost(tour) / problem.n


def swap_neighbor(tour: list[int], rng: random.Random) -> list[int]:
    neighbor = list(tour)
    i, j = rng.sample(range(len(tour)), 2)
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    return neighbor


def run_simulated_annealing(
    problem: TSPProblem, config: SAConfig | None = None, rng: random.Random | None = None
) -> SAResult:
    if config is None:
        config = SAConfig()
    rng = rng or random.Random()
    start_time = time.perf_counter()

    current = problem.random_tour(rng)
    current_cost = problem.tour_cost(current)
    best, best_cost = current, current_cost

    # Scaling the floor to the starting temperature (rather than an
    # absolute constant) keeps the schedule sensible regardless of
    # whether costs are in meters, kilometers, or unitless test fixtures.
    temperature = initial_temperature(problem, current)
    min_temperature = temperature * config.min_temperature_fraction

    cost_history = [best_cost]
    iterations = 0

    while temperature > min_temperature and iterations < config.max_iterations:
        candidate = swap_neighbor(current, rng)
        candidate_cost = problem.tour_cost(candidate)
        delta = candidate_cost - current_cost
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            current, current_cost = candidate, candidate_cost
            if current_cost < best_cost:
                best, best_cost = current, current_cost
        cost_history.append(best_cost)
        iterations += 1
        temperature *= config.alpha

    return SAResult(
        best_tour=best,
        best_cost=best_cost,
        cost_history=cost_history,
        iterations=iterations,
        runtime_seconds=time.perf_counter() - start_time,
    )
