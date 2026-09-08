from math import atan, e, pi

from tsp.visualize import lonlat_to_px, plot_convergence, plot_route, plot_route_map


class _FakeStaticMap:
    zoom = 14
    x_center = 8000.0
    y_center = 8000.0
    tile_size = 256
    width = 100
    height = 100


def test_lonlat_to_px_maps_center_to_canvas_middle():
    static_map = _FakeStaticMap()
    scale = 2**static_map.zoom
    center_lon = static_map.x_center / scale * 360.0 - 180.0
    center_lat = (2 * atan(e ** (pi * (1 - 2 * static_map.y_center / scale))) - pi / 2) * 180 / pi

    x, y = lonlat_to_px(static_map, center_lon, center_lat)

    assert x == static_map.width // 2
    assert y == static_map.height // 2


def test_plot_convergence_creates_a_nonempty_file(tmp_path):
    output_path = tmp_path / "convergence.png"
    plot_convergence([10.0, 8.0, 6.0], [10.0, 9.0, 7.0], str(output_path), ga_evals_per_generation=10)
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_route_creates_a_nonempty_file(tmp_path, square_problem):
    output_path = tmp_path / "route.png"
    plot_route(square_problem, [0, 1, 2, 3], "Test Route", str(output_path))
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_route_with_geometry_creates_a_nonempty_file(tmp_path, square_problem):
    output_path = tmp_path / "route_geometry.png"
    route_coords = [(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1), (0.0, 0.0)]
    plot_route(
        square_problem,
        [0, 1, 2, 3],
        "Test Route",
        str(output_path),
        route_coords=route_coords,
    )
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_route_map_creates_a_nonempty_file(tmp_path, square_problem, monkeypatch):
    from PIL import Image

    class FakeStaticMap(_FakeStaticMap):
        def __init__(self, *args, **kwargs):
            pass

        def add_line(self, line):
            pass

        def add_marker(self, marker):
            pass

        def render(self):
            return Image.new("RGB", (self.width, self.height), "#ffffff")

    monkeypatch.setattr("tsp.visualize.StaticMap", FakeStaticMap)

    output_path = tmp_path / "route_map.png"
    plot_route_map(
        square_problem,
        [0, 1, 2, 3],
        "Test Route",
        str(output_path),
        route_coords=[(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.0)],
        width=100,
        height=100,
    )
    assert output_path.exists()
    assert output_path.stat().st_size > 0
