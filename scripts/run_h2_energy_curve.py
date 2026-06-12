#!/usr/bin/env python
"""Compute a small H2 potential-energy curve with the validated local pipeline."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import molecule_from_string, run_fci, run_hartree_fock
from quantum_ald.hamiltonian_mapping import build_many_body_hamiltonian
from quantum_ald.vqe_solver import FallbackVQESolver

DEFAULT_DISTANCES = [0.3, 0.5, 0.7, 0.735, 1.0, 1.5, 2.0, 2.5]
DIAG_TOLERANCE = 1e-4


def _h2_at_distance(distance: float):
    return molecule_from_string(
        f"H 0 0 0\nH 0 0 {distance:.12f}",
        basis="sto-3g",
        name=f"H2_R_{distance:.3f}",
    )


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def compute_curve_point(distance: float, run_vqe: bool = True) -> dict[str, Any]:
    molecule = _h2_at_distance(distance)
    mf, hf_total = run_hartree_fock(molecule)
    _fci_solver, fci_total = run_fci(molecule, mf)
    nuclear_repulsion = float(mf.mol.energy_nuc())

    active_space = {"num_electrons": 2, "num_spatial_orbitals": mf.mo_coeff.shape[1]}
    hamiltonian, basis = build_many_body_hamiltonian(mf, active_space)
    diag_electronic = float(np.min(np.linalg.eigvalsh(hamiltonian)))
    diag_total = diag_electronic + nuclear_repulsion
    diag_error = diag_total - fci_total
    if abs(diag_error) >= DIAG_TOLERANCE:
        raise RuntimeError(
            f"H2 local diagonalization failed at R={distance:.3f} A: "
            f"diag-FCI={diag_error:.6e} Ha"
        )

    vqe_total = None
    vqe_error = None
    vqe_status = "not_run"
    if run_vqe:
        try:
            solver = FallbackVQESolver(max_iter=200)
            vqe_electronic, _params = solver.solve(hamiltonian)
            vqe_total = float(vqe_electronic + nuclear_repulsion)
            vqe_error = vqe_total - fci_total
            vqe_status = "ok"
        except Exception as exc:  # pragma: no cover - defensive runtime path
            vqe_status = f"failed: {exc}"
            print(f"Warning: fallback VQE failed at R={distance:.3f} A: {exc}")

    return {
        "distance_angstrom": float(distance),
        "nuclear_repulsion_hartree": nuclear_repulsion,
        "sector_dimension": len(basis),
        "hf_total_hartree": float(hf_total),
        "fci_total_hartree": float(fci_total),
        "local_diag_total_hartree": float(diag_total),
        "fallback_vqe_total_hartree": vqe_total,
        "diag_minus_fci_hartree": float(diag_error),
        "vqe_minus_fci_hartree": None if vqe_error is None else float(vqe_error),
        "vqe_status": vqe_status,
    }


def _write_outputs(rows: list[dict[str, Any]], output_root: Path) -> dict[str, Path]:
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    csv_path = tables_dir / "h2_energy_curve.csv"
    json_path = tables_dir / "h2_energy_curve.json"
    figure_path = figures_dir / "h2_energy_curve.png"

    fieldnames = list(rows[0].keys())
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    distances = [row["distance_angstrom"] for row in rows]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(distances, [row["hf_total_hartree"] for row in rows], "o-", label="HF total")
    ax.plot(distances, [row["fci_total_hartree"] for row in rows], "o-", label="FCI total")
    ax.plot(
        distances,
        [row["local_diag_total_hartree"] for row in rows],
        "s--",
        label="Local diagonalization total",
    )
    if any(row["fallback_vqe_total_hartree"] is not None for row in rows):
        ax.plot(
            distances,
            [row["fallback_vqe_total_hartree"] for row in rows],
            "x:",
            label="Fallback VQE total",
        )
    ax.set_xlabel("H-H distance (Angstrom)")
    ax.set_ylabel("Total energy (Ha)")
    ax.set_title("H2 potential-energy curve")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return {"csv": csv_path, "json": json_path, "figure": figure_path}


def run_curve(
    distances: Iterable[float] = DEFAULT_DISTANCES,
    output_root: Path | None = None,
    run_vqe: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    rows = [compute_curve_point(float(distance), run_vqe=run_vqe) for distance in distances]
    paths = _write_outputs(rows, output_root or PROJECT_ROOT / "results")
    return rows, paths


def print_summary(rows: list[dict[str, Any]], paths: dict[str, Path]) -> None:
    print("H2 energy curve")
    print("---------------")
    for row in rows:
        vqe_total = row["fallback_vqe_total_hartree"]
        vqe_error = row["vqe_minus_fci_hartree"]
        base = (
            f"R={row['distance_angstrom']:.3f} A | "
            f"HF={row['hf_total_hartree']:.12f} Ha | "
            f"FCI={row['fci_total_hartree']:.12f} Ha | "
            f"diag={row['local_diag_total_hartree']:.12f} Ha | "
            f"diag-FCI={row['diag_minus_fci_hartree']:.3e} Ha"
        )
        if vqe_total is not None and vqe_error is not None:
            print(f"{base} | VQE={vqe_total:.12f} Ha | VQE-FCI={vqe_error:.3e} Ha")
        else:
            print(f"{base} | VQE={row['vqe_status']}")
    print(f"CSV saved to: {_display_path(paths['csv'])}")
    print(f"JSON saved to: {_display_path(paths['json'])}")
    print(f"Figure saved to: {_display_path(paths['figure'])}")


def main() -> None:
    rows, paths = run_curve()
    print_summary(rows, paths)


if __name__ == "__main__":
    main()
