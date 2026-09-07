#!/usr/bin/env python
"""Run H2 VQE with analytic depolarizing noise and mitigation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

SCRIPT_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from quantum_ald import CDR, ZNE, DepolarizingNoiseProfile, QiskitVQESolver
from run_h2_qiskit_vqe import prepare_h2_qubit_problem


def _save_noise_scan(scan: list[dict[str, float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    factors = [row["noise_factor"] for row in scan]
    totals = [row["noisy_total_hartree"] for row in scan]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(factors, totals, "o-", label="Noisy VQE total")
    ax.set_xlabel("Noise scale factor")
    ax.set_ylabel("Total energy (Ha)")
    ax.set_title("H2 noisy VQE noise scaling")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _determinant_energy(matrix: np.ndarray, occupied_orbitals: tuple[int, ...]) -> float:
    state = 0
    for orbital in occupied_orbitals:
        state |= 1 << orbital
    return float(np.real(matrix[state, state]))


def run_workflow(
    max_iter: int = 200,
    error_rate: float = 0.005,
    output_root: Path | None = None,
) -> dict[str, Any]:
    output_root = output_root or PROJECT_ROOT / "results"
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    problem = prepare_h2_qubit_problem()
    jw_matrix = np.asarray(problem["jw_matrix"], dtype=complex)
    sparse_pauli = problem["sparse_pauli"]
    nuclear_repulsion = float(problem["nuclear_repulsion"])
    fci_total = float(problem["fci_total"])
    hf_total = float(problem["hf_total"])
    n_qubits = int(problem["n_qubits"])

    solver = QiskitVQESolver(num_qubits=n_qubits, max_iter=max_iter, ansatz_type="h2_pair")
    ideal_electronic, parameters = solver.solve(sparse_pauli)
    ideal_total = ideal_electronic + nuclear_repulsion

    profile = DepolarizingNoiseProfile(
        error_rate=error_rate,
        one_qubit_gates=2,
        two_qubit_gates=1,
    )
    mixed_electronic = float(np.real(np.trace(jw_matrix)) / jw_matrix.shape[0])

    noisy_electronic = profile.mix_energy(ideal_electronic, mixed_electronic, noise_factor=1.0)
    noisy_total = noisy_electronic + nuclear_repulsion

    noise_factors = [1.0, 1.5, 2.0, 2.5]
    zne = ZNE(noise_factors=noise_factors)
    zne_electronic = zne.execute(
        lambda factor: profile.mix_energy(ideal_electronic, mixed_electronic, noise_factor=factor)
    )
    zne_total = zne_electronic + nuclear_repulsion

    hf_electronic = _determinant_energy(jw_matrix, occupied_orbitals=(0, 1))
    noisy_hf_electronic = profile.mix_energy(hf_electronic, mixed_electronic, noise_factor=1.0)
    cdr = CDR(num_samples=1).fit([noisy_hf_electronic], [hf_electronic])
    cdr_electronic = cdr.correct(noisy_electronic)
    cdr_total = cdr_electronic + nuclear_repulsion

    scan = [
        {
            "noise_factor": float(factor),
            "effective_probability": profile.effective_probability(factor),
            "noisy_electronic_hartree": float(
                profile.mix_energy(ideal_electronic, mixed_electronic, noise_factor=factor)
            ),
            "noisy_total_hartree": float(
                profile.mix_energy(ideal_electronic, mixed_electronic, noise_factor=factor)
                + nuclear_repulsion
            ),
        }
        for factor in noise_factors
    ]

    results = {
        "molecule": problem["molecule"].name,
        "basis": problem["molecule"].mol.basis,
        "n_qubits": n_qubits,
        "ansatz": "H2Pair(HF + double excitation)",
        "noise_model": "analytic_global_depolarizing",
        "error_rate": float(error_rate),
        "gate_counts": {
            "one_qubit": profile.one_qubit_gates,
            "two_qubit": profile.two_qubit_gates,
        },
        "nuclear_repulsion_hartree": nuclear_repulsion,
        "hf_total_hartree": hf_total,
        "fci_total_hartree": fci_total,
        "ideal_vqe_total_hartree": float(ideal_total),
        "noisy_vqe_total_hartree": float(noisy_total),
        "zne_total_hartree": float(zne_total),
        "cdr_total_hartree": float(cdr_total),
        "ideal_minus_fci_hartree": float(ideal_total - fci_total),
        "noisy_minus_fci_hartree": float(noisy_total - fci_total),
        "zne_minus_fci_hartree": float(zne_total - fci_total),
        "cdr_minus_fci_hartree": float(cdr_total - fci_total),
        "mixed_electronic_hartree": mixed_electronic,
        "hf_calibration": {
            "ideal_hf_electronic_hartree": float(hf_electronic),
            "noisy_hf_electronic_hartree": float(noisy_hf_electronic),
            "cdr_slope": cdr.slope,
            "cdr_intercept": cdr.intercept,
        },
        "noise_scan": scan,
        "optimal_parameters": [float(x) for x in parameters],
        "status": "PASS" if abs(zne_total - ideal_total) < abs(noisy_total - ideal_total) else "CHECK",
    }

    results_path = tables_dir / "h2_noisy_vqe_mitigation.json"
    figure_path = figures_dir / "h2_noisy_vqe_noise_scan.png"
    results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    _save_noise_scan(scan, figure_path)
    results["results_path"] = str(results_path)
    results["figure_path"] = str(figure_path)
    return results


def main() -> int:
    try:
        results = run_workflow()
    except ImportError as exc:
        print("H2 noisy VQE skipped")
        print("--------------------")
        print(exc)
        return 0

    print("H2 noisy VQE with mitigation")
    print("----------------------------")
    print(f"Ideal VQE total: {results['ideal_vqe_total_hartree']:.12f} Ha")
    print(f"Noisy VQE total: {results['noisy_vqe_total_hartree']:.12f} Ha")
    print(f"ZNE total: {results['zne_total_hartree']:.12f} Ha")
    print(f"CDR total: {results['cdr_total_hartree']:.12f} Ha")
    print(f"FCI total: {results['fci_total_hartree']:.12f} Ha")
    print(f"Status: {results['status']}")
    print(f"Results saved to: {Path(results['results_path']).relative_to(PROJECT_ROOT)}")
    print(f"Figure saved to: {Path(results['figure_path']).relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
