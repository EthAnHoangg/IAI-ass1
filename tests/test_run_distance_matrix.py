import json

import run_distance_matrix


def test_main_fetches_fills_and_saves(tmp_path, monkeypatch):
    locations_csv = tmp_path / "locations.csv"
    locations_csv.write_text(
        "location_name,latitude,longitude,source_note\n"
        "A,0.0,0.0,note\nB,1.0,0.0,note\n",
        encoding="utf-8",
    )
    dist_csv = tmp_path / "distance_matrix.csv"
    meta_json = tmp_path / "distance_matrix_meta.json"

    monkeypatch.setattr(run_distance_matrix, "LOCATIONS_PATH", str(locations_csv))
    monkeypatch.setattr(run_distance_matrix, "DISTANCE_MATRIX_PATH", str(dist_csv))
    monkeypatch.setattr(run_distance_matrix, "DISTANCE_MATRIX_META_PATH", str(meta_json))
    monkeypatch.setattr(
        run_distance_matrix,
        "fetch_distance_matrix",
        lambda locs: [[0.0, None], [None, 0.0]],
    )

    run_distance_matrix.main()

    assert dist_csv.exists()
    meta = json.loads(meta_json.read_text(encoding="utf-8"))
    assert meta["n_locations"] == 2
