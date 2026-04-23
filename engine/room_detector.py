from typing import Dict, List

from engine.geometry import point_in_polygon, polygon_area, polygon_centroid, room_bounds
from engine.models import Room


MIN_ROOM_AREA = 1.2
MAX_ROOM_AREA = 1000.0


def _contains_polygon(outer: List[tuple], inner: List[tuple]) -> bool:
    return all(point_in_polygon(p, outer) for p in inner[:-1])


def detect_rooms_from_polylines(polylines: List[list]) -> List[Room]:
    candidates: List[Room] = []
    for idx, poly in enumerate(polylines, start=1):
        area = polygon_area(poly)
        if area <= MIN_ROOM_AREA or area >= MAX_ROOM_AREA:
            continue
        centroid = polygon_centroid(poly)
        minx, miny, maxx, maxy = room_bounds(poly)
        width = maxx - minx
        height = maxy - miny
        if width <= 0.2 or height <= 0.2:
            continue
        candidates.append(
            Room(
                id=f"R{idx}",
                polygon=poly,
                area=area,
                centroid=centroid,
            )
        )

    # Detect nested polygons: keep all children; suppress very large containers
    parents: Dict[str, List[str]] = {r.id: [] for r in candidates}
    for outer in candidates:
        for inner in candidates:
            if outer.id == inner.id:
                continue
            if outer.area <= inner.area:
                continue
            if _contains_polygon(outer.polygon, inner.polygon):
                parents[outer.id].append(inner.id)

    filtered: List[Room] = []
    for room in candidates:
        children = parents.get(room.id, [])
        # Ignore likely building envelope false positives.
        if len(children) >= 2 and room.area > sum(
            c.area for c in candidates if c.id in children
        ) * 0.9:
            continue
        filtered.append(room)

    return filtered
