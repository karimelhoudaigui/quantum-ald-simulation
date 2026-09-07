#!/usr/bin/env python
"""Validate the H2 Jordan-Wigner qubit Hamiltonian against PySCF FCI."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald.qubit_mapping_validation import validate_jordan_wigner_h2


def main() -> int:
    try:
        result = validate_jordan_wigner_h2()
    except ImportError as exc:
        print("H2 Jordan-Wigner validation skipped")
        print("------------------------------------")
        print(exc)
        return 0

    print("H2 Jordan-Wigner validation")
    print("---------------------------")
    print(f"Spin orbitals: {result['n_spin_orbitals']}")
    print(f"Qubits: {result['n_qubits']}")
    print(f"Electrons: {result['n_electrons']}")
    print(f"Mapping backend: {result['mapping_backend']}")
    print(f"Fixed-particle sector dimension: {result['fixed_particle_sector_dimension']}")
    print(f"FCI electronic: {result['fci_electronic_hartree']:.12f} Ha")
    print(f"FCI total: {result['fci_total_hartree']:.12f} Ha")
    print(
        "JW qubit ground electronic: "
        f"{result['jw_qubit_ground_electronic_hartree']:.12f} Ha"
    )
    print(f"JW qubit ground total: {result['jw_qubit_ground_total_hartree']:.12f} Ha")
    print(f"JW total - FCI total: {result['jw_total_minus_fci_total_hartree']:.6e} Ha")
    print(f"Status: {result['status']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
