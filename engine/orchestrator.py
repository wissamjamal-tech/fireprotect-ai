from pathlib import Path
from typing import Dict

from engine.boq import build_boq, export_boq_excel
from engine.classifier import classify_rooms
from engine.compliance import evaluate_nfpa_compliance
from engine.geometry_understanding import (
    detect_doors,
    detect_floor_and_riser_hints,
    detect_walls,
    infer_room_connectivity,
)
from engine.hydraulics import run_hydraulic_calculation
from engine.output_dxf import export_sprinkler_layout_dxf
from engine.parser import parse_dxf
from engine.placement import place_hose_cabinets, place_sprinklers
from engine.reporting import export_engineering_report, export_hydraulic_sheet_csv
from engine.room_detector import detect_rooms_from_polylines
from engine.rules import load_rules
from engine.stairs import detect_stairs


def run_pipeline(input_file: str, output_dir: str = "outputs") -> Dict:
    parsed = parse_dxf(input_file)
    rules = load_rules()

    rooms = detect_rooms_from_polylines(parsed["polylines"])
    rooms = classify_rooms(
        rooms,
        parsed["texts"],
        rules.get("room_classification", {}).get("keywords", {}),
    )
    stairs = detect_stairs(rooms)

    walls = detect_walls(parsed.get("lines", []), min_wall_length=float(rules.get("geometry", {}).get("min_wall_length_m", 0.8)))
    doors = detect_doors(
        parsed.get("lines", []),
        min_door_width=float(rules.get("geometry", {}).get("door_min_width_m", 0.65)),
        max_door_width=float(rules.get("geometry", {}).get("door_max_width_m", 1.4)),
    )
    connectivity = infer_room_connectivity(rooms, doors)
    floor_info = detect_floor_and_riser_hints(parsed.get("texts", []))

    hose = place_hose_cabinets(stairs, rules)
    sprinklers = place_sprinklers(rooms, rules)
    placements = hose + sprinklers

    compliance = evaluate_nfpa_compliance(rooms, placements, rules)
    hydraulic = run_hydraulic_calculation(rooms, placements, stairs, rules)

    boq_rows = build_boq(placements, rooms=rooms, stairs=stairs)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    boq_path = out_dir / "boq.xlsx"
    export_boq_excel(boq_rows, str(boq_path))

    layout_path = out_dir / "sprinkler_layout.dxf"
    export_sprinkler_layout_dxf(placements, str(layout_path))

    hydraulic_sheet_path = out_dir / "hydraulic_sheet.csv"
    export_hydraulic_sheet_csv(hydraulic, str(hydraulic_sheet_path))

    report_path = out_dir / "engineering_report.md"
    export_engineering_report(str(report_path), compliance, hydraulic, connectivity, floor_info)

    return {
        "rooms": rooms,
        "stairs": stairs,
        "walls": walls,
        "doors": doors,
        "connectivity": connectivity,
        "floor_info": floor_info,
        "placements": placements,
        "compliance": compliance,
        "hydraulic": hydraulic,
        "boq_rows": boq_rows,
        "boq_path": str(boq_path),
        "layout_dxf_path": str(layout_path),
        "hydraulic_sheet_path": str(hydraulic_sheet_path),
        "report_path": str(report_path),
    }
