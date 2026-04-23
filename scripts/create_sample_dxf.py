"""Generate a synthetic residential DXF for local testing.

Uses ezdxf when available; otherwise writes a minimal ASCII DXF directly.
"""

from pathlib import Path


def _write_ascii_dxf(path: Path) -> None:
    # Minimal DXF entities sufficient for parser fallback.
    content = """0
SECTION
2
ENTITIES
0
LWPOLYLINE
90
5
70
1
10
0
20
0
10
6
20
0
10
6
20
4
10
0
20
4
10
0
20
0
0
TEXT
1
Living
10
2.5
20
2.0
0
LWPOLYLINE
90
5
70
1
10
6
20
0
10
9
20
0
10
9
20
3
10
6
20
3
10
6
20
0
0
TEXT
1
Stair
10
7
20
1.5
0
LWPOLYLINE
90
5
70
1
10
0
20
4
10
4
20
4
10
4
20
8
10
0
20
8
10
0
20
4
0
TEXT
1
Bedroom
10
1.5
20
6
0
ENDSEC
0
ENDMARK
"""
    # DXF file should end with EOF marker.
    path.write_text(content.replace("ENDMARK", "EOF"))


def main(output_path: str = "data/samples/sample_residential.dxf"):
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    try:
        import ezdxf

        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        msp.add_lwpolyline([(0, 0), (6, 0), (6, 4), (0, 4), (0, 0)], close=True)
        msp.add_text("Living", dxfattribs={"height": 0.25, "insert": (2.5, 2)})

        msp.add_lwpolyline([(6, 0), (9, 0), (9, 3), (6, 3), (6, 0)], close=True)
        msp.add_text("Stair", dxfattribs={"height": 0.25, "insert": (7, 1.5)})

        msp.add_lwpolyline([(0, 4), (4, 4), (4, 8), (0, 8), (0, 4)], close=True)
        msp.add_text("Bedroom", dxfattribs={"height": 0.25, "insert": (1.5, 6)})

        doc.saveas(str(p))
    except Exception:
        _write_ascii_dxf(p)

    print(f"Sample DXF created at: {p}")


if __name__ == "__main__":
    main()
