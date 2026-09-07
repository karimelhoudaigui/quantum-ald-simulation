#!/usr/bin/env python
"""Write the staged ALD-inspired proxy model catalog."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp") / "quantum_ald_matplotlib"))
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import list_ald_proxy_models

OUTPUT_PATH = PROJECT_ROOT / "results" / "ald_proxy_models.json"


def build_catalog(check_load: bool = False) -> dict[str, Any]:
    models = []
    for model in list_ald_proxy_models():
        entry = model.to_dict()
        entry["geometry_exists"] = model.geometry_path.exists()
        if check_load:
            try:
                molecule = model.load()
                entry["load_status"] = "PASS"
                entry["num_atoms"] = molecule.num_atoms
                entry["num_electrons"] = molecule.num_electrons
            except ImportError as exc:
                entry["load_status"] = "SKIPPED"
                entry["skip_reason"] = str(exc)
        models.append(entry)

    return {
        "purpose": "Controlled ALD-inspired models for staged active-space validation",
        "status": "CATALOG_READY",
        "models": models,
    }


def write_catalog(output_path: Path = OUTPUT_PATH, check_load: bool = False) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    catalog = build_catalog(check_load=check_load)
    output_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-path", type=Path, default=OUTPUT_PATH)
    parser.add_argument(
        "--check-load",
        action="store_true",
        help="Try loading each model with PySCF; missing optional deps are reported as skipped.",
    )
    args = parser.parse_args(argv)

    catalog = write_catalog(output_path=args.output_path, check_load=args.check_load)
    print("ALD proxy models")
    print("----------------")
    print(f"Models: {len(catalog['models'])}")
    print(f"Status: {catalog['status']}")
    print(f"Catalog saved to: {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
