from engine.geometry_understanding import detect_doors, infer_room_connectivity
from engine.models import Room


def test_door_connectivity_between_rooms():
    room1 = Room(id="R1", polygon=[(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)], area=16, centroid=(2, 2))
    room2 = Room(id="R2", polygon=[(4, 0), (8, 0), (8, 4), (4, 4), (4, 0)], area=16, centroid=(6, 2))
    lines = [((3.9, 2), (4.9, 2))]  # ~1m door crossing boundary
    doors = detect_doors(lines)
    links = infer_room_connectivity([room1, room2], doors, edge_tol=0.6)
    assert len(links) >= 1
