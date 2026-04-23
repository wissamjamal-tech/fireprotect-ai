from pathlib import Path
from typing import Dict, List, Tuple

Point = Tuple[float, float]


def _extract_code_pairs(lines: List[str]) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    i = 0
    while i + 1 < len(lines):
        code = lines[i].strip()
        value = lines[i + 1].rstrip("\n")
        pairs.append((code, value))
        i += 2
    return pairs


def _safe_float(v: str, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def _parse_ascii_dxf(path: Path) -> Dict[str, List]:
    raw_lines = path.read_text(errors="ignore").splitlines()
    pairs = _extract_code_pairs(raw_lines)

    lines: List[Tuple[Point, Point]] = []
    polylines: List[List[Point]] = []
    texts: List[Dict] = []

    i = 0
    n = len(pairs)
    while i < n:
        code, value = pairs[i]
        if code == "0" and value in {"LINE", "LWPOLYLINE", "TEXT", "MTEXT"}:
            entity = value
            i += 1
            entity_pairs: List[Tuple[str, str]] = []
            while i < n:
                c, v = pairs[i]
                if c == "0":
                    break
                entity_pairs.append((c, v))
                i += 1

            if entity == "LINE":
                x1 = y1 = x2 = y2 = 0.0
                for c, v in entity_pairs:
                    if c == "10":
                        x1 = _safe_float(v)
                    elif c == "20":
                        y1 = _safe_float(v)
                    elif c == "11":
                        x2 = _safe_float(v)
                    elif c == "21":
                        y2 = _safe_float(v)
                lines.append(((x1, y1), (x2, y2)))

            elif entity == "LWPOLYLINE":
                pts: List[Point] = []
                closed = False
                current_x = None
                for c, v in entity_pairs:
                    if c == "70":
                        # Bit 1 means closed polyline.
                        closed = int(_safe_float(v, 0)) & 1 == 1
                    elif c == "10":
                        current_x = _safe_float(v)
                    elif c == "20" and current_x is not None:
                        pts.append((current_x, _safe_float(v)))
                        current_x = None

                if len(pts) >= 3:
                    if closed and pts[0] != pts[-1]:
                        pts.append(pts[0])
                    elif pts[0] != pts[-1]:
                        # Treat as room candidate when it is nearly closed by data authoring.
                        pts.append(pts[0])
                    polylines.append(pts)

            elif entity in {"TEXT", "MTEXT"}:
                txt = ""
                x = y = 0.0
                for c, v in entity_pairs:
                    if c in {"1", "3"}:
                        txt = f"{txt} {v}".strip()
                    elif c == "10":
                        x = _safe_float(v)
                    elif c == "20":
                        y = _safe_float(v)
                if txt:
                    texts.append({"text": txt, "location": (x, y)})
            continue
        i += 1

    return {"lines": lines, "polylines": polylines, "texts": texts}


def parse_dxf(path: str) -> Dict[str, List]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"DXF/DWG file not found: {path}")

    if p.suffix.lower() not in {".dxf", ".dwg"}:
        raise ValueError("Only DXF/DWG input is supported in V1")

    if p.suffix.lower() == ".dwg":
        raise NotImplementedError(
            "Direct DWG parsing is not supported in this MVP. Convert DWG to DXF first."
        )

    try:
        import ezdxf

        doc = ezdxf.readfile(str(p))
        msp = doc.modelspace()

        lines: List[Tuple[Point, Point]] = []
        polylines: List[List[Point]] = []
        texts: List[Dict] = []

        for entity in msp:
            dxftype = entity.dxftype()
            if dxftype == "LINE":
                start = (float(entity.dxf.start.x), float(entity.dxf.start.y))
                end = (float(entity.dxf.end.x), float(entity.dxf.end.y))
                lines.append((start, end))
            elif dxftype in {"LWPOLYLINE", "POLYLINE"}:
                try:
                    pts = [(float(pt[0]), float(pt[1])) for pt in entity.get_points()]
                except Exception:
                    pts = [(float(v.dxf.location.x), float(v.dxf.location.y)) for v in entity.vertices]
                if len(pts) >= 3:
                    if pts[0] != pts[-1]:
                        pts.append(pts[0])
                    polylines.append(pts)
            elif dxftype in {"TEXT", "MTEXT"}:
                if dxftype == "TEXT":
                    text = entity.dxf.text
                    insert = entity.dxf.insert
                    loc = (float(insert.x), float(insert.y))
                else:
                    text = entity.text
                    insert = entity.dxf.insert
                    loc = (float(insert.x), float(insert.y))
                texts.append({"text": text.strip(), "location": loc})

        return {"lines": lines, "polylines": polylines, "texts": texts}
    except Exception:
        # Fallback parser keeps MVP runnable when ezdxf is unavailable.
        return _parse_ascii_dxf(p)
