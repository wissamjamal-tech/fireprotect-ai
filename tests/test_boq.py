from engine.boq import build_boq
from engine.models import Placement, Room, Stair


def test_boq_has_pipe_and_room_summary():
    rooms = [Room(id="R1", polygon=[], area=10, centroid=(0, 0), label="Kitchen", room_type="kitchen")]
    stairs = [Stair(id="S1", location=(0, 0), source_room_id="R1")]
    placements = [
        Placement(kind="sprinkler", location=(1, 1), room_id="R1"),
        Placement(kind="sprinkler", location=(2, 1), room_id="R1"),
        Placement(kind="fire_hose_cabinet", location=(0, 0), room_id="R1"),
    ]
    rows = build_boq(placements, rooms=rooms, stairs=stairs)
    items = {r["item"] for r in rows}
    assert "pipe_network_estimated" in items
    assert any(i.startswith("sprinklers_") for i in items)
