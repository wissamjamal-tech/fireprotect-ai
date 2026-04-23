from engine.compliance import evaluate_nfpa_compliance
from engine.models import Placement, Room


def test_compliance_detects_spacing_issues():
    room = Room(
        id="R1",
        polygon=[(0, 0), (8, 0), (8, 4), (0, 4), (0, 0)],
        area=32,
        centroid=(4, 2),
        room_type="living",
    )
    placements = [
        Placement(kind="sprinkler", location=(1, 2), room_id="R1"),
        Placement(kind="sprinkler", location=(7, 2), room_id="R1"),
    ]
    rules = {"sprinkler": {"spacing_m": 3.0, "max_coverage_area_m2": 12.0, "wall_clearance_m": 0.1, "max_wall_distance_m": 2.3}}

    out = evaluate_nfpa_compliance([room], placements, rules)
    assert not out["compliant"]
    assert any("spacing" in w for w in out["warnings"])
