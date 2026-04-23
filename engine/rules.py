import json
from pathlib import Path
from typing import Dict


def load_rules(path: str = "rules/nfpa_simplified.json") -> Dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Rules file missing: {path}")
    return json.loads(p.read_text())
