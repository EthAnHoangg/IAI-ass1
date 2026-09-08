import dataclasses
import json
import math
import os

import requests

from tsp.compare import (
    run_ga_trials,
    run_sa_trials,
    save_summary_csv,
    summarize_ga,
    summarize_sa,
)
from tsp.distances import fetch_route_geometry
from tsp.genetic_algorithm import GAConfig
from tsp.problem import TSPProblem, load_distance_matrix, load_locations
from tsp.simulated_annealing import SAConfig
from tsp.visualize import ordered_tour_locations, plot_convergence, plot_route, plot_route_map

LOCATIONS_PATH = "data_collection/locations.csv"
DISTANCE_MATRIX_PATH = "data/distance_matrix.csv"
RESULTS_DIR = "results"
N_TRIALS = 10
SEED = 42


def main() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    locations = load_locations(LOCATIONS_PATH)
    distance_matrix = load_distance_matrix(DISTANCE_MATRIX_PATH)
    problem = TSPProblem(locations, distance_matrix)

    sa_config = SAConfig()
    ga_config = GAConfig()

    sa_results = run_sa_trials(problem, sa_config, N_TRIALS, SEED)
    ga_results = run_ga_trials(problem, ga_config, N_TRIALS, SEED)

    sa_summary = summarize_sa(sa_results)
    ga_summary = summarize_ga(ga_results, ga_config.population_size)

    save_summary_csv(
        [sa_summary, ga_summary], os.path.join(RESULTS_DIR, "comparison_summary.csv")
    )

    plot_convergence(
        sa_summary.mean_cost_history,
        ga_summary.mean_cost_history,
        os.path.join(RESULTS_DIR, "convergence.png"),
        ga_evals_per_generation=ga_config.population_size,
    )

    with open(os.path.join(RESULTS_DIR, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "n_trials": N_TRIALS,
                "seed": SEED,
                "sa_config": dataclasses.asdict(sa_config),
                "ga_config": dataclasses.asdict(ga_config),
            },
            f,
            indent=2,
        )

    if math.isclose(sa_summary.best_cost, ga_summary.best_cost, rel_tol=1e-9):
        overall_best = sa_summary
        tie_note = (
            " (tied with Genetic Algorithm on best cost — see mean cost and runtime"
            " for the deciding comparison)"
        )
    else:
        overall_best = min([sa_summary, ga_summary], key=lambda s: s.best_cost)
        tie_note = ""

    try:
        route_coords = fetch_route_geometry(
            ordered_tour_locations(problem, overall_best.best_tour)
        )
    except (requests.exceptions.RequestException, RuntimeError) as e:
        print(f"Warning: could not fetch real route geometry ({e}); using straight lines instead.")
        route_coords = None

    plot_route(
        problem,
        overall_best.best_tour,
        f"Best food tour route ({overall_best.algorithm}, {overall_best.best_cost:.0f}m)",
        os.path.join(RESULTS_DIR, "best_route.png"),
        route_coords=route_coords,
    )
    if route_coords is not None:
        plot_route_map(
            problem,
            overall_best.best_tour,
            f"Best food tour route ({overall_best.algorithm}, {overall_best.best_cost:.0f}m)",
            os.path.join(RESULTS_DIR, "best_route_map.png"),
            route_coords=route_coords,
        )
    else:
        print("Skipping best_route_map.png (needs real route geometry).")

    header = f"{'Algorithm':<22}{'Best (m)':>12}{'Mean (m)':>12}{'Std (m)':>10}{'Mean time (s)':>16}"
    print(header)
    for s in (sa_summary, ga_summary):
        print(
            f"{s.algorithm:<22}{s.best_cost:>12.1f}{s.mean_cost:>12.1f}"
            f"{s.std_cost:>10.1f}{s.mean_runtime_seconds:>16.3f}"
        )
    print(f"\nBest overall: {overall_best.algorithm} at {overall_best.best_cost:.1f}m{tie_note}")


if __name__ == "__main__":
    main()
