from engine.hydraulics import run_hydraulic_calculation
from engine.models import Placement, Room, Stair


def test_hydraulic_calc_returns_pipe_sizes_and_pressure_flags():
    rooms = [Room(id="R1", polygon=[], area=20, centroid=(0, 0), room_type="living")]
    placements = [Placement(kind="sprinkler", location=(1, 1), room_id="R1")]
    stairs = [Stair(id="S1", location=(0, 0), source_room_id="R1")]
    rules = {"hydraulics": {"density_lpm_m2": 4.1, "min_pressure_bar": 1.0, "min_residual_pressure_bar": 0.3}}

    out = run_hydraulic_calculation(rooms, placements, stairs, rules)
    assert out["total_flow_lpm"] > 0
    assert out["rooms"][0]["pipe_diameter_mm"] >= 25
    assert "pressure_ok" in out["rooms"][0]
