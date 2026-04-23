from pathlib import Path
from typing import List

from engine.models import Placement


def _write_ascii_overlay(path: Path, placements: List[Placement]) -> None:
    lines = ["0", "SECTION", "2", "ENTITIES"]
    for p in placements:
        if p.kind != "sprinkler":
            continue
        x, y = p.location
        lines.extend(["0", "POINT", "10", str(x), "20", str(y)])
        lines.extend(["0", "TEXT", "1", "SPR", "10", str(x + 0.1), "20", str(y + 0.1)])
    lines.extend(["0", "ENDSEC", "0", "EOF"])
    path.write_text("\n".join(lines) + "\n")


def export_sprinkler_layout_dxf(placements: List[Placement], output_path: str) -> str:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    try:
        import ezdxf

        doc = ezdxf.new("R2010")
        msp = doc.modelspace()
        for pl in placements:
            if pl.kind != "sprinkler":
                continue
            x, y = pl.location
            msp.add_circle((x, y), radius=0.15, dxfattribs={"layer": "SPRINKLERS"})
            msp.add_text("SPR", dxfattribs={"height": 0.15, "insert": (x + 0.1, y + 0.1)})
        doc.saveas(str(p))
    except Exception:
        _write_ascii_overlay(p, placements)

    return str(p)
