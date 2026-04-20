diff --git a/README.md b/README.md
index 5abd61dbb34b7d959d41aa13924f753410c0a781..b152c6ab97d0f5e64b7cb0cdb9b1074c8739a211 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,88 @@
-# fireprotect-ai
-AI-powered fire protection design engine for residential buildings (DWG-based)
+# FireProtect AI (Preliminary Design Assistant)
+
+Preliminary **fire protection design assistant** for **residential** DXF drawings.
+
+## Important disclaimer
+This tool assists engineers in generating preliminary fire protection layouts, BOQs, and hydraulic estimations based on NFPA guidelines. Final designs must be reviewed and approved by a licensed engineer.
+This software is intended for early-stage engineering support and does not replace jurisdictional review or stamped design documents.
+
+## Scope
+- Input: DXF/DWG (DWG must be converted to DXF before processing)
+- Residential buildings
+- Fire Fighting only (no Fire Alarm)
+- Outputs: BOQ Excel, sprinkler layout DXF, hydraulic calc sheet, engineering report
+
+## Project Structure
+- `engine/parser.py` DXF parser (`ezdxf` + ASCII fallback)
+- `engine/room_detector.py` room extraction with nested false-positive filtering
+- `engine/classifier.py` text + shape based room classification
+- `engine/geometry_understanding.py` wall/door/connectivity/multi-floor hints
+- `engine/placement.py` sprinkler/hose placement with spacing and wall-clearance constraints
+- `engine/compliance.py` NFPA-style spacing/coverage/wall-distance checks
+- `engine/hydraulics.py` demand, pressure-loss estimate, and pipe sizing
+- `engine/boq.py` grouped BOQ + pipe estimate + room sprinkler counts
+- `engine/output_dxf.py` output sprinkler layout DXF
+- `engine/reporting.py` engineering report + hydraulic calculation sheet export
+- `engine/orchestrator.py` full workflow
+
+## Run Modes
+### A) Full mode (recommended)
+```bash
+python -m venv .venv
+source .venv/bin/activate
+pip install -r requirements.txt
+```
+
+### B) Dependency-light mode
+Works without `ezdxf` and `openpyxl` via internal fallbacks:
+- ASCII DXF parser fallback
+- ASCII DXF writer fallback
+- Minimal XLSX writer fallback
+
+## Quick start
+```bash
+python scripts/create_sample_dxf.py
+python main.py data/samples/sample_residential.dxf --output outputs
+```
+
+Generated outputs:
+- `outputs/boq.xlsx`
+- `outputs/sprinkler_layout.dxf`
+- `outputs/hydraulic_sheet.csv`
+- `outputs/engineering_report.md`
+
+## Streamlit UI
+```bash
+streamlit run app.py
+```
+
+Entry point: `app.py`
+
+The Streamlit app supports two preliminary workflows:
+- **DXF/DWG workflow**: full pipeline (layout, BOQ, report, downloads).
+- **Image workflow (PNG/JPG)**: OpenCV-based enclosed room/area detection with edge preview, detected room outlines, room count, and preliminary sprinkler estimate.
+
+## Deploy to Streamlit Community Cloud
+If you want a public web link, deploy this repository on Streamlit Community Cloud:
+
+1. Push this project to a GitHub repository.
+2. Sign in to Streamlit Community Cloud: `https://share.streamlit.io/`.
+3. Click **Create app**.
+4. Select:
+   - **Repository**: your GitHub repo
+   - **Branch**: your target branch (for example `main`)
+   - **Main file path**: `app.py`
+5. Click **Deploy**.
+6. Wait for build/install to complete.
+7. Open the generated public app URL (format is usually `https://<app-name>.streamlit.app`).
+
+### Notes for deployment
+- `requirements.txt` already includes the required app dependencies (`streamlit`, `ezdxf`, `openpyxl`).
+- If dependency installation fails, redeploy once after clearing cache from the app settings.
+- In the app, upload DXF/DWG and click **Generate Design**.
+- Output files are generated under the runtime `outputs/` folder and exposed via download buttons.
+
+## Test
+```bash
+pytest -q
+```
