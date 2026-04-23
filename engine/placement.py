import math
from typing import Dict, List, Tuple

from engine.geometry import point_in_polygon, point_to_polygon_edge_distance, room_bounds
from engine.models import Placement, Room, Stair

Point = Tuple[float, float]


def place_hose_cabinets(stairs: List[Stair], rules: Dict) -> List[Placement]:
    placements: List[Placement] = []
    for stair in stairs:
        placements.append(
            Placement(
                kind="fire_hose_cabinet",
                location=stair.location,
                room_id=stair.source_room_id,
                metadata={"rule": "near_stair"},
            )
        )
    return placements


def _candidate_points(room: Room, spacing: float, wall_clearance: float) -> List[Point]:
    minx, miny, maxx, maxy = room_bounds(room.polygon)
    x = minx + wall_clearance
    points = []
    while x <= maxx - wall_clearance + 1e-9:
        y = miny + wall_clearance
        while y <= maxy - wall_clearance + 1e-9:
            p = (x, y)
            if point_in_polygon(p, room.polygon) and point_to_polygon_edge_distance(p, room.polygon) >= wall_clearance:
                points.append(p)
            y += spacing
        x += spacing
    if not points and point_in_polygon(room.centroid, room.polygon):
        points = [room.centroid]
    return points


def _sample_coverage_points(room: Room, sample_step: float, wall_clearance: float) -> List[Point]:
    minx, miny, maxx, maxy = room_bounds(room.polygon)
    samples = []
    x = minx + wall_clearance / 2.0
    while x <= maxx - wall_clearance / 2.0 + 1e-9:
        y = miny + wall_clearance / 2.0
        while y <= maxy - wall_clearance / 2.0 + 1e-9:
            p = (x, y)
            if point_in_polygon(p, room.polygon):
                samples.append(p)
            y += sample_step
        x += sample_step
    return samples or [room.centroid]


def place_sprinklers(rooms: List[Room], rules: Dict) -> List[Placement]:
    cfg = rules.get("sprinkler", {})
    spacing = float(cfg.get("spacing_m", 3.0))
    max_cov = float(cfg.get("max_coverage_area_m2", 12.0))
    wall_clearance = float(cfg.get("wall_clearance_m", 0.4))
    overlap_factor = float(cfg.get("coverage_overlap_factor", 0.85))
    excluded = set(cfg.get("exclude_room_types", []))

    cover_radius = math.sqrt(max_cov / math.pi) * overlap_factor
    sample_step = max(0.5, spacing / 2.0)

    placements: List[Placement] = []
    for room in rooms:
        if room.room_type in excluded:
            continue

        candidates = _candidate_points(room, spacing, wall_clearance)
        samples = _sample_coverage_points(room, sample_step, wall_clearance)
        uncovered = set(range(len(samples)))

        chosen: List[Point] = []
        while uncovered:
            best = None
            best_cover = set()
            for c in candidates:
                covered = {i for i in uncovered if math.dist(c, samples[i]) <= cover_radius}
                if len(covered) > len(best_cover):
                    best = c
                    best_cover = covered
            if not best:
                # no candidate can cover remaining points; place at centroid as fallback
                best = room.centroid
                best_cover = {i for i in uncovered if math.dist(best, samples[i]) <= cover_radius}
                if not best_cover:
                    best_cover = {next(iter(uncovered))}
            chosen.append(best)
            uncovered -= best_cover
            if len(chosen) > 200:  # safety bound
                break

        for x, y in chosen:
            placements.append(
                Placement(
                    kind="sprinkler",
                    location=(x, y),
                    room_id=room.id,
                    metadata={"room_type": room.room_type, "wall_clearance_m": wall_clearance},
                )
            )

    return placements
