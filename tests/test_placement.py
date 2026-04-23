from engine.models import Room
from engine.placement import place_sprinklers


def test_sprinklers_respect_wall_clearance():
    room = Room(
        id="R1",
        polygon=[(0, 0), (6, 0), (6, 6), (0, 6), (0, 0)],
        area=36,
        centroid=(3, 3),
        room_type="living",
    )
    rules = {
        "sprinkler": {
            "spacing_m": 3.0,
            "max_coverage_area_m2": 12.0,
            "wall_clearance_m": 0.4,
            "coverage_overlap_factor": 0.85,
            "exclude_room_types": [],
        }
    }
    sprinklers = place_sprinklers([room], rules)
    assert len(sprinklers) >= 1
    for s in sprinklers:
        x, y = s.location
        assert 0.39 <= x <= 5.61
        assert 0.39 <= y <= 5.61
