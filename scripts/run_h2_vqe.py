#!/usr/bin/env python
"""Run a small end-to-end H2 workflow: HF -> FCI -> (optional) VQE.

The script is resilient: if optional quantum dependencies are missing it will
still run HF and FCI (via PySCF) and report results. If Qiskit/OpenFermion are
available it will attempt a VQE run and save convergence plots.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import (
    H2,
    VQESolver,
    build_many_body_hamiltonian,
    define_active_space,
    map_to_qubit_hamiltonian,
    plot_vqe_convergence,
    run_fci,
    run_hartree_fock,
)
from quantum_ald.vqe_solver import FallbackVQESolver


def main() -> None:
    out_dir = PROJECT_ROOT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    tables = out_dir / "tables"
    figs = out_dir / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figs.mkdir(parents=True, exist_ok=True)

    mol = H2()
    print(f"Loaded molecule: {mol}")

    # Hartree-Fock
    try:
        mf, hf_energy = run_hartree_fock(mol)
    except Exception as exc:  # pragma: no cover - environment dependent
        print("Hartree-Fock failed:", exc)
        raise

    # FCI reference (small molecules only)
    nuclear_repulsion = float(mf.mol.energy_nuc())
    fci_energy = None
    fci_electronic = None
    try:
        _fci_solver, fci_energy = run_fci(mol, mf)
        fci_electronic = fci_energy - nuclear_repulsion
    except Exception:
        fci_energy = None

    # Attempt VQE if quantum stack is available
    vqe_energy = None
    vqe_history = None
    try:
        active_space = define_active_space(2, 2)
        # Try quantum backend first
        try:
            qubit_hamiltonian = map_to_qubit_hamiltonian(mf, active_space)
            solver = VQESolver(num_qubits=4, num_electrons=2, ansatz_type="twolocal", max_iter=100)
            vqe_electronic, params = solver.solve(qubit_hamiltonian)
            vqe_energy = vqe_electronic + nuclear_repulsion
            vqe_history = solver.get_convergence_history()
        except Exception:
            # Fallback: build many-body Hamiltonian and run pure-Python variational solver
            H, basis = build_many_body_hamiltonian(mf, active_space)
            fallback = FallbackVQESolver(max_iter=200)
            vqe_electronic, params = fallback.solve(H)
            vqe_energy = vqe_electronic + nuclear_repulsion
            vqe_history = fallback.get_convergence_history()
    except Exception as exc:  # optional dependencies may be missing
        print("VQE skipped (optional deps missing or runtime error):", exc)

    results = {
        "molecule": mol.name,
        "nuclear_repulsion_hartree": nuclear_repulsion,
        "hf_total_energy": hf_energy,
        "fci_electronic_energy": fci_electronic,
        "fci_total_energy": fci_energy,
        "vqe_total_energy": vqe_energy,
    }

    out_file = tables / "h2_vqe_results.json"
    with out_file.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)

    print("Results summary")
    print("--------------")
    print(f"Nuclear repulsion: {nuclear_repulsion:.8f} Ha")
    print(f"HF total energy: {hf_energy:.8f} Ha")
    if fci_energy is not None:
        print(f"FCI electronic energy: {fci_electronic:.8f} Ha")
        print(f"FCI total energy: {fci_energy:.8f} Ha")
    if vqe_energy is not None:
        print(f"VQE total energy: {vqe_energy:.8f} Ha")
        if fci_energy is not None:
            print(f"VQE total error vs FCI total: {abs(vqe_energy - fci_energy):.6e} Ha")
    print(f"Results saved to {out_file.relative_to(PROJECT_ROOT)}")

    if vqe_history:
        plot_path = figs / "h2_vqe_convergence.png"
        try:
            plot_vqe_convergence(vqe_history, plot_path)
            print(f"VQE convergence plot saved to {plot_path.relative_to(PROJECT_ROOT)}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
