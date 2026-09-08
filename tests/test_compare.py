import math

from tsp.compare import (
    TrialSummary,
    average_histories,
    run_ga_trials,
    run_sa_trials,
    save_summary_csv,
    steps_to_best,
    summarize_ga,
    summarize_sa,
)
from tsp.genetic_algorithm import GAConfig
from tsp.simulated_annealing import SAConfig


def test_average_histories_pads_shorter_lists_with_their_last_value():
    result = average_histories([[10.0, 8.0, 6.0], [10.0, 9.0]])
    assert result == [10.0, 8.5, 7.5]


def test_steps_to_best_returns_first_index_reaching_best_cost():
    assert steps_to_best([10.0, 8.0, 8.0, 8.0], 8.0) == 1


def test_run_sa_trials_returns_one_result_per_trial(square_problem):
    config = SAConfig(alpha=0.9, min_temperature_fraction=1e-4, max_iterations=200)
    results = run_sa_trials(square_problem, config, n_trials=3, seed=1)
    assert len(results) == 3


def test_run_ga_trials_returns_one_result_per_trial(square_problem):
    config = GAConfig(population_size=10, max_generations=20, no_improvement_stop=20)
    results = run_ga_trials(square_problem, config, n_trials=3, seed=1)
    assert len(results) == 3


def test_summarize_sa_finds_optimal_best_cost_on_square(square_problem):
    config = SAConfig(alpha=0.9, min_temperature_fraction=1e-4, max_iterations=500)
    summary = summarize_sa(run_sa_trials(square_problem, config, n_trials=5, seed=1))
    assert isinstance(summary, TrialSummary)
    assert math.isclose(summary.best_cost, 4.0, rel_tol=1e-9)
    assert summary.algorithm == "Simulated Annealing"


def test_summarize_ga_finds_optimal_best_cost_on_square(square_problem):
    config = GAConfig(population_size=20, max_generations=50, no_improvement_stop=20)
    summary = summarize_ga(
        run_ga_trials(square_problem, config, n_trials=5, seed=1), population_size=20
    )
    assert math.isclose(summary.best_cost, 4.0, rel_tol=1e-9)
    assert summary.algorithm == "Genetic Algorithm"


def test_save_summary_csv_writes_expected_header_and_row_count(tmp_path, square_problem):
    sa_config = SAConfig(alpha=0.9, min_temperature_fraction=1e-4, max_iterations=200)
    ga_config = GAConfig(population_size=10, max_generations=20, no_improvement_stop=20)
    sa_summary = summarize_sa(run_sa_trials(square_problem, sa_config, n_trials=2, seed=1))
    ga_summary = summarize_ga(
        run_ga_trials(square_problem, ga_config, n_trials=2, seed=1), population_size=10
    )

    out_path = tmp_path / "summary.csv"
    save_summary_csv([sa_summary, ga_summary], str(out_path))

    lines = out_path.read_text(encoding="utf-8").splitlines()
    assert (
        lines[0]
        == "algorithm,best_cost,mean_cost,std_cost,mean_runtime_seconds,mean_steps_to_best,mean_evals_to_best"
    )
    assert len(lines) == 3
