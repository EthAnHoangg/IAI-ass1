from pathlib import Path

import requests

import run_tsp_compare
from tsp.genetic_algorithm import GAConfig
from tsp.simulated_annealing import SAConfig


def test_main_runs_end_to_end_and_writes_outputs(tmp_path, monkeypatch):
    locations_csv = tmp_path / "locations.csv"
    locations_csv.write_text(
        "location_name,latitude,longitude,source_note\n"
        "A,0.0,0.0,note\nB,0.0,1.0,note\nC,1.0,1.0,note\nD,1.0,0.0,note\n",
        encoding="utf-8",
    )
    distance_csv = tmp_path / "distance_matrix.csv"
    distance_csv.write_text(
        ",A,B,C,D\n"
        "A,0.0,1.0,1.4142135624,1.0\n"
        "B,1.0,0.0,1.0,1.4142135624\n"
        "C,1.4142135624,1.0,0.0,1.0\n"
        "D,1.0,1.4142135624,1.0,0.0\n",
        encoding="utf-8",
    )
    results_dir = tmp_path / "results"

    monkeypatch.setattr(run_tsp_compare, "LOCATIONS_PATH", str(locations_csv))
    monkeypatch.setattr(run_tsp_compare, "DISTANCE_MATRIX_PATH", str(distance_csv))
    monkeypatch.setattr(run_tsp_compare, "RESULTS_DIR", str(results_dir))
    monkeypatch.setattr(run_tsp_compare, "N_TRIALS", 2)
    monkeypatch.setattr(
        run_tsp_compare,
        "SAConfig",
        lambda: SAConfig(alpha=0.9, min_temperature_fraction=1e-2, max_iterations=100),
    )
    monkeypatch.setattr(
        run_tsp_compare,
        "GAConfig",
        lambda: GAConfig(population_size=10, max_generations=20, no_improvement_stop=20),
    )
    monkeypatch.setattr(
        run_tsp_compare,
        "fetch_route_geometry",
        lambda locations: [(loc.lon, loc.lat) for loc in locations],
    )
    monkeypatch.setattr(
        run_tsp_compare,
        "plot_route_map",
        lambda *args, **kwargs: Path(args[3]).write_bytes(b"fake-map-bytes"),
    )

    run_tsp_compare.main()

    assert (results_dir / "comparison_summary.csv").exists()
    assert (results_dir / "convergence.png").exists()
    assert (results_dir / "best_route.png").exists()
    assert (results_dir / "best_route_map.png").exists()
    assert (results_dir / "run_meta.json").exists()


def test_main_falls_back_to_straight_lines_when_route_geometry_fetch_fails(tmp_path, monkeypatch):
    locations_csv = tmp_path / "locations.csv"
    locations_csv.write_text(
        "location_name,latitude,longitude,source_note\n"
        "A,0.0,0.0,note\nB,0.0,1.0,note\nC,1.0,1.0,note\nD,1.0,0.0,note\n",
        encoding="utf-8",
    )
    distance_csv = tmp_path / "distance_matrix.csv"
    distance_csv.write_text(
        ",A,B,C,D\n"
        "A,0.0,1.0,1.4142135624,1.0\n"
        "B,1.0,0.0,1.0,1.4142135624\n"
        "C,1.4142135624,1.0,0.0,1.0\n"
        "D,1.0,1.4142135624,1.0,0.0\n",
        encoding="utf-8",
    )
    results_dir = tmp_path / "results"

    monkeypatch.setattr(run_tsp_compare, "LOCATIONS_PATH", str(locations_csv))
    monkeypatch.setattr(run_tsp_compare, "DISTANCE_MATRIX_PATH", str(distance_csv))
    monkeypatch.setattr(run_tsp_compare, "RESULTS_DIR", str(results_dir))
    monkeypatch.setattr(run_tsp_compare, "N_TRIALS", 2)
    monkeypatch.setattr(
        run_tsp_compare,
        "SAConfig",
        lambda: SAConfig(alpha=0.9, min_temperature_fraction=1e-2, max_iterations=100),
    )
    monkeypatch.setattr(
        run_tsp_compare,
        "GAConfig",
        lambda: GAConfig(population_size=10, max_generations=20, no_improvement_stop=20),
    )

    def raise_connection_error(locations):
        raise requests.exceptions.ConnectionError("simulated network failure")

    monkeypatch.setattr(run_tsp_compare, "fetch_route_geometry", raise_connection_error)

    run_tsp_compare.main()

    assert (results_dir / "comparison_summary.csv").exists()
    assert (results_dir / "convergence.png").exists()
    assert (results_dir / "best_route.png").exists()
    assert (results_dir / "run_meta.json").exists()
    assert not (results_dir / "best_route_map.png").exists()
