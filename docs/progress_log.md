# FireProtect AI - Progress Log

## 2026-04-20
- Initialized MVP folder structure.
- Implemented DXF parser, geometry helpers, room classifier, stair detection, NFPA-style rules loader, placement engine, BOQ writer, orchestration pipeline.
- Added CLI (`main.py`) and Streamlit app (`app.py`).
- Added tests for geometry, classification, and end-to-end pipeline with synthetic DXF.
- Added dependency-fallback behavior so non-DXF-independent tests still run in restricted environments.
- Executed test suite: 3 passed, 1 skipped (pipeline test requires ezdxf).
- Improved parser with internal ASCII DXF fallback (no ezdxf required for basic entities).
- Improved BOQ export with internal minimal XLSX fallback (no openpyxl required).
- Improved classification with nearest-text fallback heuristic.
- Improved sprinkler placement by validating points inside room polygons.
- Updated tests to run without ezdxf availability and added parser fallback test.
- Updated README with full mode + dependency-light mode run instructions.
- Improved room detection to filter nested outer-envelope false positives.
- Improved room classification heuristics for bathroom/corridor/kitchen when text is weak.
- Improved sprinkler placement with wall clearance and greedy coverage strategy.
- Improved BOQ with grouped items, pipe length estimation, and per-room sprinkler counts.
- Added sprinkler layout DXF output generation with ezdxf + ASCII fallback.
- Added tests for nested room detection, sprinkler wall-clearance behavior, and BOQ enhancements.
- Added engineering modules: compliance checking, hydraulic calculation, geometry understanding, and reporting.
- Added wall/door detection, room connectivity inference, and multi-floor/riser hint extraction.
- Added hydraulic sheet CSV and engineering report markdown outputs.
- Integrated NFPA-style warnings into CLI/UI workflow.
- Repositioned product messaging as a preliminary design assistant and added explicit licensed-engineer disclaimer in README, Streamlit UI, CLI, and engineering report output.
- Redesigned Streamlit UX for real users with step-by-step flow: upload, generate action, processing status, preview, warnings/notes section, and focused downloads for BOQ, DXF layout, and engineering report.
- Prepared deployment guidance for Streamlit Community Cloud in README and added `runtime.txt` for explicit Python runtime targeting.
- Added image-based room detection workflow in Streamlit using OpenCV contour/region analysis with edge preview, detected room outlines, room-count metric, room-based sprinkler estimate, and fallback estimation when detection confidence is low.
- Added visible Streamlit UI version label `VERSION: image-analysis-v2` to help confirm cloud deployment updates.
