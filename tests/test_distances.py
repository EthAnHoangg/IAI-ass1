import json
import math

import pytest

from tsp.distances import (
    build_osrm_route_url,
    build_osrm_url,
    fetch_distance_matrix,
    fetch_route_geometry,
    fill_missing_with_haversine,
    haversine_distance,
    save_distance_matrix,
)
from tsp.problem import Location


def test_build_osrm_route_url_orders_lon_lat_and_requests_geojson():
    locations = [Location("A", 21.03, 105.85), Location("B", 21.04, 105.86)]
    url = build_osrm_route_url(locations, base_url="https://example.test/route/v1/foot")
    assert url == (
        "https://example.test/route/v1/foot/105.85,21.03;105.86,21.04"
        "?overview=full&geometries=geojson&steps=false"
    )


def test_fetch_route_geometry_calls_osrm_and_parses_coordinates(monkeypatch):
    locations = [Location("A", 0.0, 0.0), Location("B", 1.0, 0.0)]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "code": "Ok",
                "routes": [{"geometry": {"coordinates": [[0.0, 0.0], [0.5, 0.0], [1.0, 0.0]]}}],
            }

    captured = {}

    def fake_get(url, timeout):
        captured["url"] = url
        return FakeResponse()

    monkeypatch.setattr("tsp.distances.requests.get", fake_get)

    coords = fetch_route_geometry(locations, base_url="https://example.test/route/v1/foot")

    assert coords == [(0.0, 0.0), (0.5, 0.0), (1.0, 0.0)]
    assert captured["url"].startswith("https://example.test/route/v1/foot/")


def test_fetch_route_geometry_raises_on_osrm_error(monkeypatch):
    locations = [Location("A", 0.0, 0.0), Location("B", 1.0, 0.0)]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"code": "InvalidQuery", "message": "bad input"}

    monkeypatch.setattr("tsp.distances.requests.get", lambda url, timeout: FakeResponse())

    with pytest.raises(RuntimeError, match="InvalidQuery"):
        fetch_route_geometry(locations)


def test_build_osrm_url_orders_lon_lat_and_appends_annotation():
    locations = [Location("A", 21.03, 105.85), Location("B", 21.04, 105.86)]
    url = build_osrm_url(locations, base_url="https://example.test/table/v1/foot")
    assert url == (
        "https://example.test/table/v1/foot/105.85,21.03;105.86,21.04"
        "?annotations=distance"
    )


def test_haversine_distance_zero_for_same_point():
    a = Location("A", 21.03, 105.85)
    assert haversine_distance(a, a) == 0.0


def test_haversine_distance_known_pair():
    a = Location("A", 0.0, 0.0)
    b = Location("B", 1.0, 0.0)
    assert math.isclose(haversine_distance(a, b), 111_195, rel_tol=0.01)


def test_fill_missing_with_haversine_replaces_nulls(capsys):
    locations = [Location("A", 0.0, 0.0), Location("B", 1.0, 0.0)]
    matrix = [[0.0, None], [None, 0.0]]
    filled = fill_missing_with_haversine(matrix, locations)
    assert filled[0][0] == 0.0
    assert math.isclose(filled[0][1], haversine_distance(locations[0], locations[1]))
    assert "Warning" in capsys.readouterr().out


def test_fetch_distance_matrix_calls_osrm_and_parses_distances(monkeypatch):
    locations = [Location("A", 0.0, 0.0), Location("B", 1.0, 0.0)]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"code": "Ok", "distances": [[0.0, 111195.0], [111195.0, 0.0]]}

    captured = {}

    def fake_get(url, timeout):
        captured["url"] = url
        return FakeResponse()

    monkeypatch.setattr("tsp.distances.requests.get", fake_get)

    matrix = fetch_distance_matrix(locations, base_url="https://example.test/table/v1/foot")

    assert matrix == [[0.0, 111195.0], [111195.0, 0.0]]
    assert captured["url"].startswith("https://example.test/table/v1/foot/")


def test_fetch_distance_matrix_raises_on_osrm_error(monkeypatch):
    locations = [Location("A", 0.0, 0.0), Location("B", 1.0, 0.0)]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"code": "InvalidQuery", "message": "bad input"}

    monkeypatch.setattr("tsp.distances.requests.get", lambda url, timeout: FakeResponse())

    with pytest.raises(RuntimeError, match="InvalidQuery"):
        fetch_distance_matrix(locations)


def test_save_distance_matrix_writes_csv_and_meta(tmp_path):
    locations = [Location("A", 0.0, 0.0), Location("B", 1.0, 0.0)]
    matrix = [[0.0, 5.0], [5.0, 0.0]]
    csv_path = tmp_path / "distance_matrix.csv"
    meta_path = tmp_path / "distance_matrix_meta.json"

    save_distance_matrix(matrix, locations, str(csv_path), str(meta_path), "https://example.test")

    first_line = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert first_line == ",A,B"

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["n_locations"] == 2
    assert meta["source_url"] == "https://example.test"
