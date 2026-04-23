from pathlib import Path

from engine.orchestrator import run_pipeline
from scripts.create_sample_dxf import main as create_sample


def test_end_to_end_pipeline(tmp_path: Path):
    dxf_path = tmp_path / "sample.dxf"
    create_sample(str(dxf_path))

    out = run_pipeline(str(dxf_path), output_dir=str(tmp_path / "out"))
    assert len(out["rooms"]) >= 3
    assert len(out["stairs"]) >= 1
    assert any(row["item"] == "sprinkler" for row in out["boq_rows"])
    assert Path(out["boq_path"]).exists()
    assert Path(out["layout_dxf_path"]).exists()
    assert Path(out["hydraulic_sheet_path"]).exists()
    assert Path(out["report_path"]).exists()
