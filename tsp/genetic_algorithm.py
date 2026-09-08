from __future__ import annotations

import random
import time
from dataclasses import dataclass

from tsp.problem import TSPProblem


@dataclass
class GAConfig:
    population_size: int = 100
    tournament_size: int = 3
    crossover_rate: float = 0.9
    mutation_rate: float = 0.02
    elite_count: int = 2
    max_generations: int = 300
    no_improvement_stop: int = 50


@dataclass
class GAResult:
    best_tour: list[int]
    best_cost: float
    cost_history: list[float]
    generations: int
    runtime_seconds: float


def tournament_select(
    population: list[list[int]], fitnesses: list[float], k: int, rng: random.Random
) -> list[int]:
    contenders = rng.sample(range(len(population)), k)
    winner = min(contenders, key=lambda idx: fitnesses[idx])
    return population[winner]


def order_crossover(parent_a: list[int], parent_b: list[int], rng: random.Random) -> list[int]:
    n = len(parent_a)
    i, j = sorted(rng.sample(range(n), 2))
    child: list[int | None] = [None] * n
    child[i : j + 1] = parent_a[i : j + 1]
    # OX1: fill remaining slots with parent_b's cities, in parent_b's
    # order, skipping any city already placed by the parent_a segment —
    # this is what guarantees the child is always a valid permutation.
    fill_values = [city for city in parent_b if city not in child]
    pos = 0
    for k in range(n):
        if child[k] is None:
            child[k] = fill_values[pos]
            pos += 1
    return child  # type: ignore[return-value]


def swap_mutate(tour: list[int], rng: random.Random) -> list[int]:
    mutated = list(tour)
    i, j = rng.sample(range(len(tour)), 2)
    mutated[i], mutated[j] = mutated[j], mutated[i]
    return mutated


def run_genetic_algorithm(
    problem: TSPProblem, config: GAConfig | None = None, rng: random.Random | None = None
) -> GAResult:
    if config is None:
        config = GAConfig()
    rng = rng or random.Random()
    start_time = time.perf_counter()

    population = [problem.random_tour(rng) for _ in range(config.population_size)]
    fitnesses = [problem.tour_cost(t) for t in population]
    best_idx = min(range(config.population_size), key=lambda i: fitnesses[i])
    best, best_cost = population[best_idx], fitnesses[best_idx]
    cost_history = [best_cost]

    no_improvement = 0
    generation = 0
    for generation in range(config.max_generations):
        ranked = sorted(range(config.population_size), key=lambda i: fitnesses[i])
        next_population = [population[i] for i in ranked[: config.elite_count]]

        while len(next_population) < config.population_size:
            parent_a = tournament_select(population, fitnesses, config.tournament_size, rng)
            parent_b = tournament_select(population, fitnesses, config.tournament_size, rng)
            if rng.random() < config.crossover_rate:
                child = order_crossover(parent_a, parent_b, rng)
            else:
                child = list(parent_a)
            if rng.random() < config.mutation_rate:
                child = swap_mutate(child, rng)
            next_population.append(child)

        population = next_population
        fitnesses = [problem.tour_cost(t) for t in population]
        gen_best_idx = min(range(config.population_size), key=lambda i: fitnesses[i])

        if fitnesses[gen_best_idx] < best_cost:
            best, best_cost = population[gen_best_idx], fitnesses[gen_best_idx]
            no_improvement = 0
        else:
            no_improvement += 1

        cost_history.append(best_cost)
        if no_improvement >= config.no_improvement_stop:
            break

    return GAResult(
        best_tour=best,
        best_cost=best_cost,
        cost_history=cost_history,
        generations=generation + 1,
        runtime_seconds=time.perf_counter() - start_time,
    )
