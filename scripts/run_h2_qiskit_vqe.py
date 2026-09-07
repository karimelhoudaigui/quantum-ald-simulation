#!/usr/bin/env python
"""Run a noiseless Qiskit statevector VQE for H2."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import H2, run_fci, run_hartree_fock
from quantum_ald.hamiltonian_mapping import build_many_body_hamiltonian
from quantum_ald.qubit_mapping_validation import build_local_jordan_wigner_matrix
from quantum_ald.vqe_solver import (
    FallbackVQESolver,
    QiskitVQESolver,
    dense_matrix_to_sparse_pauli,
)

FCI_TOLERANCE_HARTREE = 1e-3
HF_TOLERANCE_HARTREE = 1e-6


def _save_convergence(history: dict[str, list[float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(history.get("iterations", []), history.get("energies", []), "o-", markersize=3)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Electronic energy (Ha)")
    ax.set_title("H2 Qiskit VQE convergence")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def prepare_h2_qubit_problem() -> dict[str, Any]:
    """Build H2 references and the four-qubit Jordan-Wigner Hamiltonian."""
    molecule = H2()
    mf, hf_total = run_hartree_fock(molecule)
    _fci_solver, fci_total = run_fci(molecule, mf)
    nuclear_repulsion = float(mf.mol.energy_nuc())

    active_space = {"num_electrons": 2, "num_spatial_orbitals": mf.mo_coeff.shape[1]}
    n_qubits = 2 * active_space["num_spatial_orbitals"]
    jw_matrix = build_local_jordan_wigner_matrix(mf, active_space["num_spatial_orbitals"])
    sparse_pauli = dense_matrix_to_sparse_pauli(jw_matrix)

    many_body_hamiltonian, _basis = build_many_body_hamiltonian(mf, active_space)
    fallback = FallbackVQESolver(max_iter=200)
    fallback_electronic, _fallback_params = fallback.solve(many_body_hamiltonian)
    fallback_total = fallback_electronic + nuclear_repulsion

    return {
        "molecule": molecule,
        "mf": mf,
        "hf_total": float(hf_total),
        "fci_total": float(fci_total),
        "nuclear_repulsion": nuclear_repulsion,
        "active_space": active_space,
        "n_qubits": n_qubits,
        "jw_matrix": jw_matrix,
        "sparse_pauli": sparse_pauli,
        "many_body_hamiltonian": many_body_hamiltonian,
        "fallback_total": float(fallback_total),
    }


def run_workflow(max_iter: int = 200, output_root: Path | None = None) -> dict[str, Any]:
    output_root = output_root or PROJECT_ROOT / "results"
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    problem = prepare_h2_qubit_problem()
    molecule = problem["molecule"]
    hf_total = problem["hf_total"]
    fci_total = problem["fci_total"]
    nuclear_repulsion = problem["nuclear_repulsion"]
    n_qubits = problem["n_qubits"]
    sparse_pauli = problem["sparse_pauli"]

    solver = QiskitVQESolver(num_qubits=n_qubits, max_iter=max_iter, ansatz_type="h2_pair")
    qiskit_electronic, parameters = solver.solve(sparse_pauli)
    qiskit_total = qiskit_electronic + nuclear_repulsion
    qiskit_gap = qiskit_total - fci_total
    qiskit_minus_hf = qiskit_total - hf_total

    below_hf = qiskit_total <= hf_total + HF_TOLERANCE_HARTREE
    near_fci = abs(qiskit_gap) < FCI_TOLERANCE_HARTREE
    if near_fci:
        status = "FCI_CLOSE"
    elif below_hf:
        status = "REFERENCE_ONLY"
    else:
        status = "CHECK"

    results = {
        "molecule": molecule.name,
        "basis": molecule.mol.basis,
        "n_qubits": n_qubits,
        "ansatz": "H2Pair(HF + double excitation)",
        "optimizer": "Nelder-Mead multi-start",
        "nuclear_repulsion_hartree": nuclear_repulsion,
        "hf_total_hartree": float(hf_total),
        "fci_total_hartree": float(fci_total),
        "fallback_vqe_total_hartree": problem["fallback_total"],
        "qiskit_vqe_electronic_hartree": float(qiskit_electronic),
        "qiskit_vqe_total_hartree": float(qiskit_total),
        "qiskit_vqe_minus_hf_hartree": float(qiskit_minus_hf),
        "qiskit_vqe_minus_fci_hartree": float(qiskit_gap),
        "fci_tolerance_hartree": FCI_TOLERANCE_HARTREE,
        "below_hf": below_hf,
        "near_fci": near_fci,
        "iterations": len(solver.get_convergence_history()["energies"]),
        "status": status,
        "optimal_parameters": [float(x) for x in parameters],
    }

    results_path = tables_dir / "h2_qiskit_vqe_results.json"
    figure_path = figures_dir / "h2_qiskit_vqe_convergence.png"
    results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    _save_convergence(solver.get_convergence_history(), figure_path)
    results["results_path"] = str(results_path)
    results["figure_path"] = str(figure_path)
    return results


def main() -> int:
    try:
        results = run_workflow()
    except ImportError as exc:
        print("H2 Qiskit VQE skipped")
        print("---------------------")
        print(exc)
        return 0

    print("H2 Qiskit VQE")
    print("-------------")
    print(f"HF total: {results['hf_total_hartree']:.12f} Ha")
    print(f"FCI total: {results['fci_total_hartree']:.12f} Ha")
    print(f"Fallback VQE total: {results['fallback_vqe_total_hartree']:.12f} Ha")
    print(f"Qiskit VQE total: {results['qiskit_vqe_total_hartree']:.12f} Ha")
    print(f"Qiskit VQE - HF: {results['qiskit_vqe_minus_hf_hartree']:.6e} Ha")
    print(f"Qiskit VQE - FCI: {results['qiskit_vqe_minus_fci_hartree']:.6e} Ha")
    print(f"Below HF: {results['below_hf']}")
    print(f"Near FCI ({results['fci_tolerance_hartree']:.1e} Ha): {results['near_fci']}")
    print(f"Status: {results['status']}")
    print(f"Results saved to: {Path(results['results_path']).relative_to(PROJECT_ROOT)}")
    print(f"Figure saved to: {Path(results['figure_path']).relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
