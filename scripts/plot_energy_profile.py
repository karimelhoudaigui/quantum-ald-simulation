#!/usr/bin/env python
"""Generate a demonstration ALD reaction energy profile."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import plot_energy_profile


def main() -> None:
    energies = {
        "HF": {"R": 0.0, "TS": 0.50, "P": -0.20},
        "VQE": {"R": 0.0, "TS": 0.48, "P": -0.18},
    }
    output = PROJECT_ROOT / "results" / "figures" / "energy_profile.png"
    plot_energy_profile(energies, output)
    print(f"Figure saved to {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
