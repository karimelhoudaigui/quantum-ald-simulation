#!/usr/bin/env python
"""Quick check that the package imports and optional features warn usefully."""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import importlib


def main() -> None:
    pkg = importlib.import_module("quantum_ald")
    print("Imported package quantum_ald, version:", getattr(pkg, "__version__", "unknown"))
    # Try to access light-weight utilities
    try:
        from quantum_ald import H2, load_molecule

        mol = H2()
        print("H2 molecule loaded:", mol)
    except Exception as exc:
        print("Warning: could not construct H2 molecule:", exc)

    print("validate_install completed")


if __name__ == "__main__":
    main()
