from __future__ import annotations

import csv
import random
import statistics
from dataclasses import dataclass

from tsp.genetic_algorithm import GAConfig, GAResult, run_genetic_algorithm
from tsp.problem import TSPProblem
from tsp.simulated_annealing import SAConfig, SAResult, run_simulated_annealing


@dataclass
class TrialSummary:
    algorithm: str
    best_cost: float
    mean_cost: float
    std_cost: float
    mean_runtime_seconds: float
    mean_steps_to_best: float
    mean_evals_to_best: float
    best_tour: list[int]
    mean_cost_history: list[float]


def run_sa_trials(
    problem: TSPProblem, config: SAConfig, n_trials: int, seed: int
) -> list[SAResult]:
    return [
        run_simulated_annealing(problem, config, random.Random(seed + i))
        for i in range(n_trials)
    ]


def run_ga_trials(
    problem: TSPProblem, config: GAConfig, n_trials: int, seed: int
) -> list[GAResult]:
    return [
        run_genetic_algorithm(problem, config, random.Random(seed + i))
        for i in range(n_trials)
    ]


def average_histories(histories: list[list[float]]) -> list[float]:
    max_len = max(len(h) for h in histories)
    padded = [h + [h[-1]] * (max_len - len(h)) for h in histories]
    return [sum(values) / len(values) for values in zip(*padded)]


def steps_to_best(cost_history: list[float], best_cost: float) -> int:
    for step, cost in enumerate(cost_history):
        if cost == best_cost:
            return step
    return len(cost_history) - 1


def _summarize(algorithm: str, results: list, evals_per_step: int) -> TrialSummary:
    costs = [r.best_cost for r in results]
    runtimes = [r.runtime_seconds for r in results]
    steps = [steps_to_best(r.cost_history, r.best_cost) for r in results]
    best_result = min(results, key=lambda r: r.best_cost)
    return TrialSummary(
        algorithm=algorithm,
        best_cost=best_result.best_cost,
        mean_cost=statistics.mean(costs),
        std_cost=statistics.pstdev(costs) if len(costs) > 1 else 0.0,
        mean_runtime_seconds=statistics.mean(runtimes),
        mean_steps_to_best=statistics.mean(steps),
        mean_evals_to_best=statistics.mean(step * evals_per_step for step in steps),
        best_tour=best_result.best_tour,
        mean_cost_history=average_histories([r.cost_history for r in results]),
    )


def summarize_sa(results: list[SAResult]) -> TrialSummary:
    return _summarize("Simulated Annealing", results, evals_per_step=1)


def summarize_ga(results: list[GAResult], population_size: int) -> TrialSummary:
    return _summarize("Genetic Algorithm", results, evals_per_step=population_size)


def save_summary_csv(summaries: list[TrialSummary], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "algorithm",
                "best_cost",
                "mean_cost",
                "std_cost",
                "mean_runtime_seconds",
                "mean_steps_to_best",
                "mean_evals_to_best",
            ]
        )
        for s in summaries:
            writer.writerow(
                [
                    s.algorithm,
                    s.best_cost,
                    s.mean_cost,
                    s.std_cost,
                    s.mean_runtime_seconds,
                    s.mean_steps_to_best,
                    s.mean_evals_to_best,
                ]
            )
