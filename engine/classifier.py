from math import dist
from typing import Dict, List

from engine.geometry import point_in_polygon, room_bounds
from engine.models import Room


def _infer_from_label(text: str, keyword_rules: Dict[str, List[str]]) -> str:
    t = text.lower().strip()
    for room_type, kws in keyword_rules.items():
        if any(kw in t for kw in kws):
            return room_type
    return "unknown"


def _shape_heuristic(room: Room) -> str:
    minx, miny, maxx, maxy = room_bounds(room.polygon)
    w = maxx - minx
    h = maxy - miny
    if w <= 0 or h <= 0:
        return "unknown"
    aspect = max(w, h) / max(0.1, min(w, h))

    if room.area <= 7.0:
        return "bathroom"
    if aspect >= 3.5 and room.area >= 6.0:
        return "corridor"
    if 6.0 <= room.area <= 25.0 and aspect < 2.5:
        return "kitchen"
    return "unknown"


def classify_rooms(rooms: List[Room], texts: List[Dict], keyword_rules: Dict[str, List[str]]) -> List[Room]:
    for room in rooms:
        room.room_type = "unknown"

    unassigned_texts = []
    for text_obj in texts:
        raw = text_obj.get("text", "")
        loc = text_obj.get("location", (0, 0))
        matched = False

        for room in rooms:
            if point_in_polygon(loc, room.polygon):
                room.label = raw
                inferred = _infer_from_label(raw, keyword_rules)
                if inferred != "unknown":
                    room.room_type = inferred
                matched = True
                break

        if not matched:
            unassigned_texts.append(text_obj)

    for room in rooms:
        if not room.label:
            nearest = None
            best_d = float("inf")
            for text_obj in unassigned_texts:
                loc = text_obj.get("location", (0, 0))
                d = dist(room.centroid, loc)
                if d < best_d:
                    best_d = d
                    nearest = text_obj
            if nearest and best_d <= 3.0:
                room.label = nearest.get("text", "")
                inferred = _infer_from_label(room.label, keyword_rules)
                if inferred != "unknown":
                    room.room_type = inferred

        if room.room_type == "unknown":
            heuristic_type = _shape_heuristic(room)
            if heuristic_type != "unknown":
                room.room_type = heuristic_type
            elif room.area < 4.0:
                room.room_type = "utility"

    return rooms
