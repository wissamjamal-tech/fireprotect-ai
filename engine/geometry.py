import math
from typing import Iterable, List, Tuple

Point = Tuple[float, float]


def polygon_area(points: Iterable[Point]) -> float:
    pts = list(points)
    if len(pts) < 3:
        return 0.0
    area = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        area += (x1 * y2) - (x2 * y1)
    return abs(area) / 2.0


def polygon_centroid(points: List[Point]) -> Point:
    area = polygon_area(points)
    if area == 0:
        return (0.0, 0.0)
    factor = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        cross = (x1 * y2) - (x2 * y1)
        factor += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    factor *= 0.5
    cx /= (6.0 * factor)
    cy /= (6.0 * factor)
    return (cx, cy)


def point_in_polygon(point: Point, polygon: List[Point]) -> bool:
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        intersects = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-9) + x1
        )
        if intersects:
            inside = not inside
    return inside


def room_bounds(polygon: List[Point]) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return (min(xs), min(ys), max(xs), max(ys))


def polygon_perimeter(points: List[Point]) -> float:
    if len(points) < 2:
        return 0.0
    total = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        total += math.dist((x1, y1), (x2, y2))
    return total


def point_to_segment_distance(point: Point, seg_a: Point, seg_b: Point) -> float:
    px, py = point
    x1, y1 = seg_a
    x2, y2 = seg_b
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.dist(point, seg_a)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    proj = (x1 + t * dx, y1 + t * dy)
    return math.dist(point, proj)


def point_to_polygon_edge_distance(point: Point, polygon: List[Point]) -> float:
    if not polygon:
        return 0.0
    dmin = float("inf")
    for i in range(len(polygon)):
        a = polygon[i]
        b = polygon[(i + 1) % len(polygon)]
        dmin = min(dmin, point_to_segment_distance(point, a, b))
    return dmin
