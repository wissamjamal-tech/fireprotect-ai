from pathlib import Path
from typing import Dict, List


def export_hydraulic_sheet_csv(hydraulic: Dict, output_path: str) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = ["room_id,sprinklers,area_m2,flow_lpm,pipe_diameter_mm,pressure_loss_bar,residual_pressure_bar,pressure_ok"]
    for r in hydraulic.get("rooms", []):
        lines.append(
            f"{r['room_id']},{r['sprinklers']},{r['area_m2']},{r['flow_lpm']},{r['pipe_diameter_mm']},{r['pressure_loss_bar']},{r['residual_pressure_bar']},{r['pressure_ok']}"
        )
    p.write_text("\n".join(lines) + "\n")
    return str(p)


def export_engineering_report(
    output_path: str,
    compliance: Dict,
    hydraulic: Dict,
    connectivity: List[Dict],
    floor_info: Dict,
) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    warnings = compliance.get("warnings", [])
    notes = compliance.get("notes", [])

    md = []
    md.append("# FireProtect AI Engineering Report")
    md.append("")
    md.append("## Disclaimer")
    md.append(
        "This tool assists engineers in generating preliminary fire protection layouts, BOQs, and hydraulic estimations based on NFPA guidelines. Final designs must be reviewed and approved by a licensed engineer."
    )
    md.append("")
    md.append("## Compliance Summary")
    md.append(f"- Overall compliant: **{compliance.get('compliant', False)}**")
    md.append(f"- Warning count: **{len(warnings)}**")
    md.append(f"- Note count: **{len(notes)}**")
    md.append("")

    md.append("## NFPA-style Compliance Notes")
    if warnings:
        for w in warnings:
            md.append(f"- ⚠️ {w}")
    else:
        md.append("- No critical spacing/coverage/wall-distance warnings.")
    if notes:
        md.append("- Informational:")
        for n in notes:
            md.append(f"  - {n}")

    md.append("")
    md.append("## Hydraulic Calculation Summary")
    md.append(f"- Total flow: **{hydraulic.get('total_flow_lpm', 0)} lpm**")
    md.append(f"- Estimated minimum pump pressure: **{hydraulic.get('pump_min_pressure_bar', 0)} bar**")
    for rr in hydraulic.get("rooms", []):
        md.append(
            f"- {rr['room_id']}: flow={rr['flow_lpm']} lpm, pipe={rr['pipe_diameter_mm']} mm, pressure_ok={rr['pressure_ok']}"
        )

    md.append("")
    md.append("## Connectivity & Multi-floor Hints")
    md.append(f"- Door-based room links detected: **{len(connectivity)}**")
    md.append(f"- Floor labels detected: **{len(floor_info.get('floors', []))}**")
    md.append(f"- Riser labels detected: **{len(floor_info.get('risers', []))}**")
    md.append(f"- Multi-floor link inferred: **{floor_info.get('has_multifloor_link', False)}**")

    p.write_text("\n".join(md) + "\n")
    return str(p)
