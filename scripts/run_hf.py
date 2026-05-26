#!/usr/bin/env python
"""Run Hartree-Fock calculations on all available XYZ geometries."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import load_molecule, run_hartree_fock


def main() -> None:
    data_dir = PROJECT_ROOT / "data" / "geometries"
    output_path = PROJECT_ROOT / "results" / "tables" / "hf_energies.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    for xyz_file in sorted(data_dir.glob("*.xyz")):
        molecule = load_molecule(xyz_file)
        _mf, energy = run_hartree_fock(molecule)
        rows.append(
            {
                "molecule": molecule.name,
                "hf_energy": energy,
                "num_atoms": molecule.num_atoms,
                "num_electrons": molecule.num_electrons,
            }
        )
        print(f"{molecule.name}: {energy:.8f} Ha")

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["molecule", "hf_energy", "num_atoms", "num_electrons"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Results saved to {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
