import math
from collections import defaultdict
from typing import Dict, List

from engine.models import Placement, Room, Stair


PIPE_OPTIONS_MM = [25, 32, 40, 50, 65, 80, 100]


def _select_pipe_diameter(flow_lpm: float, max_velocity_m_s: float = 3.0) -> int:
    q_m3_s = flow_lpm / 1000.0 / 60.0
    for d_mm in PIPE_OPTIONS_MM:
        d = d_mm / 1000.0
        area = math.pi * (d ** 2) / 4.0
        velocity = q_m3_s / max(area, 1e-9)
        if velocity <= max_velocity_m_s:
            return d_mm
    return PIPE_OPTIONS_MM[-1]


def _estimate_branch_pressure_loss(length_m: float, flow_lpm: float, diameter_mm: int, c_hw: float = 120.0) -> float:
    # Hazen-Williams approximate head loss (m) converted to bar.
    if flow_lpm <= 0 or length_m <= 0:
        return 0.0
    q_m3_s = flow_lpm / 1000.0 / 60.0
    d_m = diameter_mm / 1000.0
    hf_m = 10.67 * length_m * (q_m3_s ** 1.852) / ((c_hw ** 1.852) * (d_m ** 4.871))
    return hf_m / 10.197


def run_hydraulic_calculation(
    rooms: List[Room], placements: List[Placement], stairs: List[Stair], rules: Dict
) -> Dict:
    cfg = rules.get("hydraulics", {})
    density_lpm_m2 = float(cfg.get("density_lpm_m2", 4.1))
    min_pressure_bar = float(cfg.get("min_pressure_bar", 1.0))
    safety_factor = float(cfg.get("safety_factor", 1.15))

    room_area = {r.id: r.area for r in rooms}
    room_spr = defaultdict(int)
    for p in placements:
        if p.kind == "sprinkler" and p.room_id:
            room_spr[p.room_id] += 1

    room_results = []
    total_flow = 0.0
    for room_id, spr_count in sorted(room_spr.items()):
        area = room_area.get(room_id, 0.0)
        demand = area * density_lpm_m2
        flow = max(demand, spr_count * float(cfg.get("min_sprinkler_flow_lpm", 57.0)))
        flow *= safety_factor
        diameter = _select_pipe_diameter(flow)

        # Use nearest stair as riser anchor; fallback branch length 8m.
        branch_len = float(cfg.get("default_branch_length_m", 8.0))
        pressure_loss = _estimate_branch_pressure_loss(branch_len, flow, diameter)
        residual_pressure = max(0.0, min_pressure_bar - pressure_loss)

        room_results.append(
            {
                "room_id": room_id,
                "sprinklers": spr_count,
                "area_m2": round(area, 2),
                "flow_lpm": round(flow, 2),
                "pipe_diameter_mm": diameter,
                "pressure_loss_bar": round(pressure_loss, 3),
                "residual_pressure_bar": round(residual_pressure, 3),
                "pressure_ok": residual_pressure >= float(cfg.get("min_residual_pressure_bar", 0.5)),
            }
        )
        total_flow += flow

    summary = {
        "total_flow_lpm": round(total_flow, 2),
        "pump_min_pressure_bar": round(min_pressure_bar + max([r["pressure_loss_bar"] for r in room_results] or [0]), 2),
        "rooms": room_results,
    }
    return summary
