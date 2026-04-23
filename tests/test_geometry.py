from engine.geometry import point_in_polygon, polygon_area


def test_polygon_area_rectangle():
    poly = [(0, 0), (4, 0), (4, 3), (0, 3), (0, 0)]
    assert polygon_area(poly) == 12.0


def test_point_in_polygon():
    poly = [(0, 0), (4, 0), (4, 3), (0, 3), (0, 0)]
    assert point_in_polygon((2, 2), poly)
    assert not point_in_polygon((5, 5), poly)
