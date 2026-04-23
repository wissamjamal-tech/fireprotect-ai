from pathlib import Path

from engine.parser import parse_dxf


def test_ascii_dxf_fallback_parser(tmp_path: Path):
    dxf = tmp_path / "fallback.dxf"
    dxf.write_text(
        "\n".join(
            [
                "0", "SECTION", "2", "ENTITIES",
                "0", "LWPOLYLINE", "90", "5", "70", "1",
                "10", "0", "20", "0", "10", "2", "20", "0", "10", "2", "20", "2", "10", "0", "20", "2", "10", "0", "20", "0",
                "0", "TEXT", "1", "Kitchen", "10", "1", "20", "1",
                "0", "ENDSEC", "0", "EOF",
            ]
        )
    )

    parsed = parse_dxf(str(dxf))
    assert len(parsed["polylines"]) == 1
    assert parsed["texts"][0]["text"].lower() == "kitchen"
