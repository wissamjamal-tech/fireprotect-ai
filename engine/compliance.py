import math
from collections import defaultdict
from typing import Dict, List

from engine.geometry import point_to_polygon_edge_distance
from engine.models import Placement, Room


def evaluate_nfpa_compliance(rooms: List[Room], placements: List[Placement], rules: Dict) -> Dict:
    cfg = rules.get("sprinkler", {})
    spacing = float(cfg.get("spacing_m", 3.0))
    max_area = float(cfg.get("max_coverage_area_m2", 12.0))
    wall_min = float(cfg.get("wall_clearance_m", 0.4))
    wall_max = float(cfg.get("max_wall_distance_m", 2.3))

    room_map = {r.id: r for r in rooms}
    by_room = defaultdict(list)
    for p in placements:
        if p.kind == "sprinkler" and p.room_id:
            by_room[p.room_id].append(p)

    warnings = []
    notes = []
    for room_id, sprs in by_room.items():
        room = room_map.get(room_id)
        if not room:
            continue

        coverage_area = room.area / max(1, len(sprs))
        if coverage_area > max_area:
            warnings.append(
                f"{room_id}: coverage area per sprinkler {coverage_area:.2f} m2 exceeds {max_area:.2f} m2"
            )

        for i, s in enumerate(sprs):
            dwall = point_to_polygon_edge_distance(s.location, room.polygon)
            if dwall < wall_min:
                warnings.append(f"{room_id}: sprinkler {i+1} too close to wall ({dwall:.2f} m < {wall_min:.2f} m)")
            if dwall > wall_max:
                notes.append(f"{room_id}: sprinkler {i+1} far from nearest wall ({dwall:.2f} m)")

        for i in range(len(sprs)):
            for j in range(i + 1, len(sprs)):
                d = math.dist(sprs[i].location, sprs[j].location)
                if d > spacing * 1.05:
                    warnings.append(f"{room_id}: sprinkler spacing {d:.2f} m exceeds limit {spacing:.2f} m")

    compliant = len(warnings) == 0
    return {
        "compliant": compliant,
        "warnings": sorted(set(warnings)),
        "notes": sorted(set(notes)),
    }
