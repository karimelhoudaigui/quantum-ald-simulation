#!/usr/bin/env python
"""Run a compact VQE demonstration on H2."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import H2, VQESolver, define_active_space, map_to_qubit_hamiltonian, run_hartree_fock


def main() -> None:
    molecule = H2()
    mf, hf_energy = run_hartree_fock(molecule)
    active_space = define_active_space(2, 2)
    qubit_hamiltonian = map_to_qubit_hamiltonian(mf, active_space)

    solver = VQESolver(num_qubits=4, num_electrons=2, ansatz_type="twolocal", max_iter=100)
    energy, _params = solver.solve(qubit_hamiltonian)

    print("Quantum ALD VQE Demonstration")
    print("=============================")
    print(f"Molecule: {molecule.name}")
    print(f"HF energy: {hf_energy:.8f} Ha")
    print(f"VQE energy: {energy:.8f} Ha")


if __name__ == "__main__":
    main()
