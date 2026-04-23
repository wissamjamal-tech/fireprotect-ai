import tempfile
from pathlib import Path
from typing import List, Tuple

import streamlit as st

from engine.image_analysis import detect_rooms_from_floorplan_image
from engine.orchestrator import run_pipeline

Point = Tuple[float, float]


def _layout_bounds(polygons: List[List[Point]], points: List[Point]) -> Tuple[float, float, float, float]:
    all_points: List[Point] = []
    for poly in polygons:
        all_points.extend(poly)
    all_points.extend(points)
    if not all_points:
        return (0.0, 0.0, 10.0, 10.0)
    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    if abs(maxx - minx) < 1e-9:
        maxx = minx + 1.0
    if abs(maxy - miny) < 1e-9:
        maxy = miny + 1.0
    return minx, miny, maxx, maxy


def _build_layout_svg(rooms, placements, width: int = 760, height: int = 420) -> str:
    room_polys = [r.polygon for r in rooms]
    device_points = [p.location for p in placements]
    minx, miny, maxx, maxy = _layout_bounds(room_polys, device_points)

    pad = 24
    draw_w = max(1, width - 2 * pad)
    draw_h = max(1, height - 2 * pad)

    def to_screen(pt: Point) -> Tuple[float, float]:
        x = pad + ((pt[0] - minx) / (maxx - minx)) * draw_w
        y = pad + ((maxy - pt[1]) / (maxy - miny)) * draw_h
        return x, y

    svg: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>',
    ]

    for room in rooms:
        points = " ".join(f"{sx:.1f},{sy:.1f}" for sx, sy in (to_screen(p) for p in room.polygon))
        svg.append(f'<polygon points="{points}" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1.2"/>')

    for pl in placements:
        x, y = to_screen(pl.location)
        if pl.kind == "sprinkler":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.0" fill="#2563eb" />')
        elif pl.kind == "fire_hose_cabinet":
            svg.append(f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" fill="#dc2626" />')

    svg.append("</svg>")
    return "\n".join(svg)


st.set_page_config(page_title="Preliminary Fire Protection Design Assistant", layout="centered")
st.title("Preliminary Fire Protection Design Assistant")
st.caption("VERSION: image-analysis-v2")
st.caption("Generate preliminary sprinkler layout, BOQ, and engineering outputs from DXF/DWG drawings.")
st.info(
    "This tool assists engineers in generating preliminary fire protection layouts, BOQs, and hydraulic estimations based on NFPA guidelines. Final designs must be reviewed and approved by a licensed engineer."
)

st.markdown(
    "### How to use\n"
    "1. Upload your DXF/DWG or floor-plan image.\n"
    "2. Click **Generate Design**.\n"
    "3. Review results and warnings.\n"
    "4. Download BOQ, layout DXF, and report (for DXF/DWG runs)."
)

uploaded = st.file_uploader("Step 1: Upload file", type=["dxf", "dwg", "png", "jpg", "jpeg"])
left, right = st.columns([1, 1])
generate = left.button("Generate Design", type="primary", disabled=uploaded is None)
clear = right.button("Clear")

if clear:
    st.session_state.pop("cad_result", None)
    st.session_state.pop("image_result", None)
    st.session_state.pop("uploaded_image_bytes", None)
    st.session_state.pop("uploaded_name", None)
    st.rerun()

if uploaded is not None:
    st.session_state["uploaded_name"] = uploaded.name
    st.success(f"Loaded file: {uploaded.name}")

if generate and uploaded is not None:
    suffix = Path(uploaded.name).suffix.lower()
    file_bytes = uploaded.getbuffer().tobytes()

    if suffix in {".dxf", ".dwg"}:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            temp_path = tmp.name

        try:
            with st.status("Processing design...", expanded=True) as status:
                st.write("Reading CAD file...")
                st.write("Detecting rooms and stairs...")
                st.write("Placing sprinklers and cabinets...")
                st.write("Generating BOQ and report files...")
                result = run_pipeline(temp_path, output_dir="outputs")
                st.session_state["cad_result"] = result
                st.session_state.pop("image_result", None)
                status.update(label="Processing completed", state="complete")
        except Exception as e:
            st.error(f"Failed to process file: {e}")
    else:
        try:
            with st.status("Processing floor-plan image...", expanded=True) as status:
                st.write("Loading image...")
                st.write("Detecting enclosed room-like areas...")
                st.write("Estimating preliminary sprinkler count by detected areas...")
                image_result = detect_rooms_from_floorplan_image(file_bytes)
                st.session_state["image_result"] = image_result
                st.session_state["uploaded_image_bytes"] = file_bytes
                st.session_state.pop("cad_result", None)
                status.update(label="Image analysis completed", state="complete")
        except Exception as e:
            st.error(f"Failed to process image: {e}")

image_result = st.session_state.get("image_result")
if image_result:
    st.subheader("Results")
    st.image(st.session_state.get("uploaded_image_bytes"), caption="Uploaded floor-plan image", use_container_width=True)

    m1, m2 = st.columns(2)
    m1.metric("Detected rooms / areas", image_result["room_count"])
    m2.metric("Estimated sprinklers", image_result["estimated_sprinklers"])

    st.markdown("#### Edge / Layout Preview")
    st.image(image_result["edge_preview_png"], caption="Extracted edge/layout view", use_container_width=True)

    st.markdown("#### Detected Rooms / Areas")
    st.image(image_result["rooms_preview_png"], caption="Detected enclosed regions outlined", use_container_width=True)
    if image_result.get("fallback_used"):
        st.warning(
            "Room detection confidence is low for this image. A fallback sprinkler estimate was used."
        )

cad_result = st.session_state.get("cad_result")
if cad_result:
    st.subheader("Results")
    m1, m2, m3 = st.columns(3)
    m1.metric("Rooms", len(cad_result["rooms"]))
    m2.metric("Sprinklers", sum(1 for p in cad_result["placements"] if p.kind == "sprinkler"))
    m3.metric("Warnings", len(cad_result["compliance"]["warnings"]))

    st.markdown("#### Sprinkler Layout Preview")
    if cad_result["rooms"] and cad_result["placements"]:
        preview_svg = _build_layout_svg(cad_result["rooms"], cad_result["placements"])
        st.image(preview_svg.encode("utf-8"), caption="Preliminary layout preview (blue: sprinklers, red: hose cabinets)")
    else:
        st.info("Preview unavailable because no rooms or placements were generated.")

    st.markdown("#### Warnings & Compliance Notes")
    warnings = cad_result["compliance"].get("warnings", [])
    notes = cad_result["compliance"].get("notes", [])
    if warnings:
        for w in warnings:
            st.warning(w)
    else:
        st.success("No critical compliance warnings were reported.")
    if notes:
        with st.expander("Show compliance notes"):
            for n in notes:
                st.write(f"- {n}")

    st.markdown("#### BOQ Preview")
    st.dataframe(cad_result["boq_rows"], use_container_width=True)

    st.markdown("#### Downloads")
    d1, d2, d3 = st.columns(3)
    with open(cad_result["boq_path"], "rb") as f:
        d1.download_button(
            label="BOQ (Excel)",
            data=f,
            file_name="boq.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with open(cad_result["layout_dxf_path"], "rb") as f:
        d2.download_button(
            label="Sprinkler Layout (DXF)",
            data=f,
            file_name="sprinkler_layout.dxf",
            mime="application/dxf",
        )
    with open(cad_result["report_path"], "rb") as f:
        d3.download_button(
            label="Engineering Report",
            data=f,
            file_name="engineering_report.md",
            mime="text/markdown",
        )
