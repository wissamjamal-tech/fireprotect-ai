import argparse
from pprint import pprint

from engine.orchestrator import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="FireProtect AI - Preliminary Fire Protection Design Assistant")
    parser.add_argument("input", help="Path to DXF file")
    parser.add_argument("--output", default="outputs", help="Output directory")
    args = parser.parse_args()

    result = run_pipeline(args.input, args.output)
    print("Pipeline completed.")
    print(f"BOQ Excel: {result['boq_path']}")
    print(f"Layout DXF: {result['layout_dxf_path']}")
    print(f"Hydraulic Sheet: {result['hydraulic_sheet_path']}")
    print(f"Engineering Report: {result['report_path']}")
    print(
        "Disclaimer: This tool assists engineers in generating preliminary fire protection layouts, BOQs, and hydraulic estimations based on NFPA guidelines. Final designs must be reviewed and approved by a licensed engineer."
    )
    print("BOQ Summary:")
    pprint(result["boq_rows"])
    print("Compliance Warnings:")
    pprint(result["compliance"]["warnings"])


if __name__ == "__main__":
    main()
