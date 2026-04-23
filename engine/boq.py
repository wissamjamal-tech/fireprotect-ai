import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional
from zipfile import ZIP_DEFLATED, ZipFile

from engine.models import Placement, Room, Stair


def _estimate_pipe_length(placements: List[Placement], stairs: Optional[List[Stair]]) -> float:
    sprinklers = [p for p in placements if p.kind == "sprinkler"]
    anchors = [s.location for s in (stairs or [])]
    if not sprinklers:
        return 0.0
    if not anchors:
        # Fallback conservative estimate from room network (2m/sprinkler)
        return round(len(sprinklers) * 2.0, 2)

    total = 0.0
    for s in sprinklers:
        d = min(math.dist(s.location, a) for a in anchors)
        total += d
    total *= 1.15  # fittings / routing allowance
    return round(total, 2)


def build_boq(placements: List[Placement], rooms: Optional[List[Room]] = None, stairs: Optional[List[Stair]] = None) -> List[Dict]:
    counts = Counter([p.kind for p in placements])

    room_sprinklers = defaultdict(int)
    for p in placements:
        if p.kind == "sprinkler" and p.room_id:
            room_sprinklers[p.room_id] += 1

    rows: List[Dict] = []
    rows.append({"group": "Devices", "item": "sprinkler", "unit": "Nos", "quantity": counts.get("sprinkler", 0)})
    rows.append(
        {
            "group": "Devices",
            "item": "fire_hose_cabinet",
            "unit": "Nos",
            "quantity": counts.get("fire_hose_cabinet", 0),
        }
    )
    rows.append(
        {
            "group": "Piping",
            "item": "pipe_network_estimated",
            "unit": "m",
            "quantity": _estimate_pipe_length(placements, stairs),
        }
    )

    if rooms:
        room_map = {r.id: (r.label or r.room_type or r.id) for r in rooms}
        for room_id in sorted(room_sprinklers):
            rows.append(
                {
                    "group": "Room Summary",
                    "item": f"sprinklers_{room_map.get(room_id, room_id)}",
                    "unit": "Nos",
                    "quantity": room_sprinklers[room_id],
                }
            )

    return rows


def _write_minimal_xlsx(rows: List[Dict], output_path: Path) -> None:
    all_rows = [["Group", "Item", "Unit", "Quantity"]] + [
        [r.get("group", "General"), r["item"], r["unit"], str(r["quantity"])] for r in rows
    ]

    sheet_rows = []
    for ridx, row in enumerate(all_rows, start=1):
        cells = []
        for cidx, val in enumerate(row, start=1):
            col = chr(64 + cidx)
            ref = f"{col}{ridx}"
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{val}</t></is></c>')
        sheet_rows.append(f"<row r=\"{ridx}\">{''.join(cells)}</row>")

    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(sheet_rows)}</sheetData>"
        "</worksheet>"
    )
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="BOQ" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )
    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )
    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        "</Relationships>"
    )

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", root_rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def export_boq_excel(rows: List[Dict], output_path: str) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    try:
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "BOQ"
        ws.append(["Group", "Item", "Unit", "Quantity"])
        for r in rows:
            ws.append([r.get("group", "General"), r["item"], r["unit"], r["quantity"]])
        wb.save(str(p))
    except Exception:
        _write_minimal_xlsx(rows, p)

    return str(p)
