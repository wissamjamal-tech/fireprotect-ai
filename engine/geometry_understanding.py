import math
from typing import Dict, List, Tuple

from engine.geometry import point_to_polygon_edge_distance
from engine.models import Room

Point = Tuple[float, float]
Line = Tuple[Point, Point]


def _line_len(line: Line) -> float:
    return math.dist(line[0], line[1])


def detect_walls(lines: List[Line], min_wall_length: float = 0.8) -> List[Line]:
    return [ln for ln in lines if _line_len(ln) >= min_wall_length]


def detect_doors(lines: List[Line], min_door_width: float = 0.65, max_door_width: float = 1.4) -> List[Dict]:
    doors = []
    for ln in lines:
        l = _line_len(ln)
        if min_door_width <= l <= max_door_width:
            mx = (ln[0][0] + ln[1][0]) / 2.0
            my = (ln[0][1] + ln[1][1]) / 2.0
            doors.append({"line": ln, "midpoint": (mx, my), "width": l})
    return doors


def infer_room_connectivity(rooms: List[Room], doors: List[Dict], edge_tol: float = 0.25) -> List[Dict]:
    links = []
    for d in doors:
        near_rooms = []
        for r in rooms:
            if point_to_polygon_edge_distance(d["midpoint"], r.polygon) <= edge_tol:
                near_rooms.append(r.id)
        near_rooms = sorted(set(near_rooms))
        if len(near_rooms) >= 2:
            links.append({"door": d, "rooms": near_rooms[:2]})
    return links


def detect_floor_and_riser_hints(texts: List[Dict]) -> Dict:
    floors = []
    risers = []
    for t in texts:
        text = t.get("text", "").lower()
        if "floor" in text:
            floors.append(t)
        if "riser" in text:
            risers.append(t)
    # multi-floor links are inferred from riser labels when present
    return {"floors": floors, "risers": risers, "has_multifloor_link": bool(risers)}
