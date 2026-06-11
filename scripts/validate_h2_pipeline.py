#!/usr/bin/env python
"""Validate the local H2 reference pipeline end to end."""

from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path
from typing import Any

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quantum_ald import load_molecule, run_fci, run_hartree_fock
from quantum_ald.hamiltonian_mapping import build_many_body_hamiltonian
from quantum_ald.vqe_solver import FallbackVQESolver

GEOMETRY_PATH = PROJECT_ROOT / "data" / "geometries" / "h2.xyz"
SUMMARY_PATH = PROJECT_ROOT / "results" / "h2_validation_summary.json"
FCI_TOLERANCE = 1e-4


def _energy_gap(energy: float, reference: float) -> float:
    return float(energy - reference)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def run_validation() -> dict[str, Any]:
    molecule = load_molecule(GEOMETRY_PATH)
    mf, hf_energy = run_hartree_fock(molecule)
    _fci_solver, fci_total = run_fci(molecule, mf)
    nuclear_repulsion = float(mf.mol.energy_nuc())
    fci_electronic = float(fci_total - nuclear_repulsion)

    active_space = {
        "num_electrons": molecule.num_electrons,
        "num_spatial_orbitals": mf.mo_coeff.shape[1],
    }
    hamiltonian, basis = build_many_body_hamiltonian(mf, active_space)
    n_spin_orbitals = 2 * active_space["num_spatial_orbitals"]
    sector_dimension = comb(n_spin_orbitals, active_space["num_electrons"])

    eigenvalues = np.linalg.eigvalsh(hamiltonian)
    diag_electronic = float(np.min(np.real(eigenvalues)))
    diag_total = diag_electronic + nuclear_repulsion

    solver = FallbackVQESolver(max_iter=200)
    vqe_electronic, _params = solver.solve(hamiltonian)
    vqe_total = float(vqe_electronic + nuclear_repulsion)

    gaps = {
        "hf_total_minus_fci_total": _energy_gap(hf_energy, fci_total),
        "diag_manybody_electronic_minus_fci_electronic": _energy_gap(
            diag_electronic, fci_electronic
        ),
        "diag_manybody_total_minus_fci_total": _energy_gap(diag_total, fci_total),
        "vqe_total_minus_fci_total": _energy_gap(vqe_total, fci_total),
    }

    return {
        "molecule": molecule.name,
        "geometry": str(GEOMETRY_PATH.relative_to(PROJECT_ROOT)),
        "basis": molecule.mol.basis,
        "active_space": active_space,
        "n_spin_orbitals": n_spin_orbitals,
        "n_electrons": active_space["num_electrons"],
        "basis_size": len(basis),
        "fixed_particle_sector_dimension": sector_dimension,
        "nuclear_repulsion_hartree": nuclear_repulsion,
        "energies_hartree": {
            "hf_total": float(hf_energy),
            "fci_electronic": fci_electronic,
            "fci_total": float(fci_total),
            "diag_manybody_electronic": diag_electronic,
            "diag_manybody_total": diag_total,
            "vqe_fallback_electronic": float(vqe_electronic),
            "vqe_fallback_total": vqe_total,
        },
        "gaps_hartree": gaps,
        "tolerance_hartree": FCI_TOLERANCE,
        "diag_matches_fci": abs(gaps["diag_manybody_total_minus_fci_total"]) < FCI_TOLERANCE,
    }


def save_summary(summary: dict[str, Any], output_path: Path = SUMMARY_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def print_summary(summary: dict[str, Any], output_path: Path = SUMMARY_PATH) -> None:
    energies = summary["energies_hartree"]
    gaps = summary["gaps_hartree"]

    print("H2 validation summary")
    print("---------------------")
    print(f"Geometry: {summary['geometry']}")
    print(f"Basis: {summary['basis']}")
    print(f"Active space: {summary['active_space']}")
    print(f"Spin orbitals: {summary['n_spin_orbitals']}")
    print(f"Electrons: {summary['n_electrons']}")
    print(f"Fixed-particle sector dimension: {summary['fixed_particle_sector_dimension']}")
    print(f"Many-body basis size: {summary['basis_size']}")
    print(f"Nuclear repulsion: {summary['nuclear_repulsion_hartree']:.12f} Ha")
    print()
    print(f"HF total:                       {energies['hf_total']:.12f} Ha")
    print(f"FCI electronic:                 {energies['fci_electronic']:.12f} Ha")
    print(f"FCI total:                      {energies['fci_total']:.12f} Ha")
    print(f"Local diagonalization electronic:{energies['diag_manybody_electronic']:.12f} Ha")
    print(f"Local diagonalization total:    {energies['diag_manybody_total']:.12f} Ha")
    print(f"Fallback VQE electronic:        {energies['vqe_fallback_electronic']:.12f} Ha")
    print(f"Fallback VQE total:             {energies['vqe_fallback_total']:.12f} Ha")
    print()
    print(f"HF total - FCI total:                       {gaps['hf_total_minus_fci_total']:.6e} Ha")
    print(
        "diag_manybody electronic - FCI electronic: "
        f"{gaps['diag_manybody_electronic_minus_fci_electronic']:.6e} Ha"
    )
    print(
        "diag_manybody total - FCI total:           "
        f"{gaps['diag_manybody_total_minus_fci_total']:.6e} Ha"
    )
    print(
        "VQE total - FCI total:                      "
        f"{gaps['vqe_total_minus_fci_total']:.6e} Ha"
    )
    print(f"Summary saved to: {_display_path(output_path)}")


def main(output_path: Path = SUMMARY_PATH) -> None:
    summary = run_validation()
    save_summary(summary, output_path)
    print_summary(summary, output_path)

    diag_gap = abs(summary["gaps_hartree"]["diag_manybody_total_minus_fci_total"])
    if diag_gap >= FCI_TOLERANCE:
        raise SystemExit(
            f"Local many-body diagonalization differs from FCI by {diag_gap:.6e} Ha "
            f"(tolerance: {FCI_TOLERANCE:.1e} Ha)"
        )


if __name__ == "__main__":
    main()
