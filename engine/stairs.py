from typing import List

from engine.models import Room, Stair


def detect_stairs(rooms: List[Room]) -> List[Stair]:
    stairs = []
    for room in rooms:
        if room.room_type == "stair" or (room.label and "stair" in room.label.lower()):
            stairs.append(Stair(id=f"S-{room.id}", location=room.centroid, source_room_id=room.id))
    return stairs
