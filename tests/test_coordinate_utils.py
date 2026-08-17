"""
Tests for `parse_point`.
 
Assumes the function lives in a module called `coordinate_utils.py`
(adjust the import below to match wherever you saved the function).
"""
 
import math
import pytest
 
from coordinate_utils import parse_point
 
 
# ---------------------------------------------------------------------
# POINT geometry
# ---------------------------------------------------------------------
 
def test_point_basic():
    lat, lon = parse_point("POINT (-122.3321 47.6062)")
    assert lat == pytest.approx(47.6062)
    assert lon == pytest.approx(-122.3321)
 
 
def test_point_positive_coords():
    lat, lon = parse_point("POINT (122.3321 47.6062)")
    assert lat == pytest.approx(47.6062)
    assert lon == pytest.approx(122.3321)
 
 
def test_point_integer_like_coords():
    # No decimal portion at all
    lat, lon = parse_point("POINT (100 50)")
    assert lat == pytest.approx(50.0)
    assert lon == pytest.approx(100.0)
 
 
def test_point_zero_coords():
    lat, lon = parse_point("POINT (0.0 0.0)")
    assert lat == pytest.approx(0.0)
    assert lon == pytest.approx(0.0)
 
 
def test_point_return_types_are_float():
    lat, lon = parse_point("POINT (-122.33 47.60)")
    assert isinstance(lat, float)
    assert isinstance(lon, float)
 
 
# ---------------------------------------------------------------------
# POLYGON geometry -> centroid (simple average of vertices)
# ---------------------------------------------------------------------
 
def test_polygon_centroid_square():
    # A unit square with corners at (0,0), (2,0), (2,2), (0,2)
    wkt = "POLYGON ((0 0, 2 0, 2 2, 0 2, 0 0))"
    lat, lon = parse_point(wkt)
    # lons = [0,2,2,0,0] -> mean 0.8 ; lats = [0,0,2,2,0] -> mean 0.8
    assert lat == pytest.approx(0.8)
    assert lon == pytest.approx(0.8)
 
 
def test_polygon_centroid_matches_manual_average():
    wkt = "POLYGON ((-122.1 47.1, -122.3 47.3, -122.5 47.5))"
    lat, lon = parse_point(wkt)
    expected_lat = (47.1 + 47.3 + 47.5) / 3
    expected_lon = (-122.1 + -122.3 + -122.5) / 3
    assert lat == pytest.approx(expected_lat)
    assert lon == pytest.approx(expected_lon)
 
 
def test_polygon_single_vertex_pair():
    # Degenerate polygon with just one coordinate pair listed
    wkt = "POLYGON ((1.0 2.0))"
    lat, lon = parse_point(wkt)
    assert lat == pytest.approx(2.0)
    assert lon == pytest.approx(1.0)
 
 
def test_polygon_return_types_are_float():
    wkt = "POLYGON ((0 0, 2 0, 2 2, 0 2, 0 0))"
    lat, lon = parse_point(wkt)
    assert isinstance(lat, float)
    assert isinstance(lon, float)
 
 
# ---------------------------------------------------------------------
# Invalid / unsupported input -> (None, None)
# ---------------------------------------------------------------------
 
@pytest.mark.parametrize(
    "wkt",
    [
        "",
        "not a wkt string",
        "LINESTRING (0 0, 1 1)",
        "MULTIPOINT ((0 0), (1 1))",
        "POINT(1 2)",          # missing required space after POINT
        "POLYGON((0 0, 1 1))", # missing required space after POLYGON
        "POINT (1 2",          # malformed, missing closing paren
    ],
)
def test_unsupported_or_malformed_wkt_returns_none(wkt):
    lat, lon = parse_point(wkt)
    assert lat is None
    assert lon is None
 
 
def test_none_input_returns_none():
    # wkt = str(wkt) inside the function turns None into "None"
    lat, lon = parse_point(None)
    assert lat is None
    assert lon is None
 
 
def test_non_string_numeric_input_returns_none():
    lat, lon = parse_point(12345)
    assert lat is None
    assert lon is None
 
 
# ---------------------------------------------------------------------
# NaN handling (values that stringify to something regex-unfriendly)
# ---------------------------------------------------------------------
 
def test_nan_input_returns_none():
    lat, lon = parse_point(float("nan"))
    assert lat is None
    assert lon is None
