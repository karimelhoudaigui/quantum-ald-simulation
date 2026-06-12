#!/usr/bin/env python
"""Prepare a conservative LiH validation report without forcing dense scaling."""

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

from quantum_ald import load_molecule, run_casci, run_fci, run_hartree_fock
from quantum_ald.hamiltonian_mapping import (
    build_many_body_hamiltonian,
    build_many_body_hamiltonian_from_integrals,
)

GEOMETRY_PATH = PROJECT_ROOT / "data" / "geometries" / "lih.xyz"
SUMMARY_PATH = PROJECT_ROOT / "results" / "lih_validation_summary.json"
FCI_DIMENSION_LIMIT = 1000
LOCAL_DIAGONALIZATION_LIMIT = 100
REDUCED_ACTIVE_SPACE = {"num_electrons": 2, "num_spatial_orbitals": 2}
CASCI_TOLERANCE = 1e-4


def _sector_dimension(n_spin_orbitals: int, n_electrons: int) -> int:
    if n_electrons > n_spin_orbitals:
        return 0
    return comb(n_spin_orbitals, n_electrons)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def run_validation(
    output_path: Path = SUMMARY_PATH,
    fci_dimension_limit: int = FCI_DIMENSION_LIMIT,
    local_diagonalization_limit: int = LOCAL_DIAGONALIZATION_LIMIT,
) -> dict[str, Any]:
    molecule = load_molecule(GEOMETRY_PATH)
    mf, hf_total = run_hartree_fock(molecule)
    nuclear_repulsion = float(mf.mol.energy_nuc())

    n_electrons = molecule.num_electrons
    n_spatial_orbitals = int(mf.mo_coeff.shape[1])
    n_spin_orbitals = 2 * n_spatial_orbitals
    full_sector_dimension = _sector_dimension(n_spin_orbitals, n_electrons)

    fci_total = None
    fci_status = "skipped"
    if full_sector_dimension <= fci_dimension_limit:
        try:
            _fci_solver, fci_total = run_fci(molecule, mf)
            fci_status = "ok"
        except Exception as exc:  # pragma: no cover - environment/runtime dependent
            fci_status = f"failed: {exc}"
    else:
        fci_status = (
            f"skipped: fixed-particle sector dimension {full_sector_dimension} "
            f"exceeds limit {fci_dimension_limit}"
        )

    local_full = {
        "status": "skipped",
        "reason": (
            f"fixed-particle sector dimension {full_sector_dimension} exceeds "
            f"dense limit {local_diagonalization_limit}"
        ),
    }
    if full_sector_dimension <= local_diagonalization_limit:
        hamiltonian, basis = build_many_body_hamiltonian(
            mf,
            {"num_electrons": n_electrons, "num_spatial_orbitals": n_spatial_orbitals},
        )
        local_electronic = float(np.min(np.linalg.eigvalsh(hamiltonian)))
        local_full = {
            "status": "ok",
            "basis_size": len(basis),
            "electronic_energy_hartree": local_electronic,
            "total_energy_hartree": local_electronic + nuclear_repulsion,
        }

    ncas = REDUCED_ACTIVE_SPACE["num_spatial_orbitals"]
    nelecas = REDUCED_ACTIVE_SPACE["num_electrons"]
    casci_solver, casci_total = run_casci(molecule, mf, n_electrons=nelecas, n_orbitals=ncas)

    h1eff, ecore = casci_solver.get_h1eff()
    ao2mo = __import__("pyscf.ao2mo", fromlist=["restore"])
    h2eff = ao2mo.restore(1, casci_solver.get_h2eff(), ncas)
    cas_hamiltonian, cas_basis = build_many_body_hamiltonian_from_integrals(
        h1eff,
        h2eff,
        n_electrons=nelecas,
    )
    cas_active_electronic = float(np.min(np.linalg.eigvalsh(cas_hamiltonian)))
    local_casci_total = cas_active_electronic + float(ecore)
    local_casci_error = local_casci_total - casci_total
    if abs(local_casci_error) >= CASCI_TOLERANCE:
        raise RuntimeError(
            "LiH local CASCI active-space diagonalization differs from PySCF CASCI "
            f"by {local_casci_error:.6e} Ha"
        )

    summary = {
        "molecule": molecule.name,
        "geometry": str(GEOMETRY_PATH.relative_to(PROJECT_ROOT)),
        "basis": molecule.mol.basis,
        "n_electrons": n_electrons,
        "n_spatial_orbitals": n_spatial_orbitals,
        "n_spin_orbitals": n_spin_orbitals,
        "full_fixed_particle_sector_dimension": full_sector_dimension,
        "nuclear_repulsion_hartree": nuclear_repulsion,
        "hf_total_hartree": float(hf_total),
        "fci_status": fci_status,
        "fci_total_hartree": None if fci_total is None else float(fci_total),
        "local_full_space": local_full,
        "casci_active_space": {
            "active_space": REDUCED_ACTIVE_SPACE,
            "basis_size": len(cas_basis),
            "core_energy_shift_hartree": float(ecore),
            "pyscf_casci_total_hartree": float(casci_total),
            "local_active_electronic_hartree": cas_active_electronic,
            "local_casci_total_hartree": local_casci_total,
            "local_minus_pyscf_casci_hartree": local_casci_error,
            "note": (
                "CASCI(2,2) with the PySCF effective one-electron Hamiltonian "
                "and core energy shift. This validates the reduced active-space "
                "model against PySCF CASCI, not against full-space FCI."
            ),
        },
        "validated_reduced_active_space": abs(local_casci_error) < CASCI_TOLERANCE,
        "validated_total_energy": fci_total is not None,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def print_summary(summary: dict[str, Any], output_path: Path = SUMMARY_PATH) -> None:
    print("LiH validation preparation")
    print("--------------------------")
    print(f"Geometry: {summary['geometry']}")
    print(f"Basis: {summary['basis']}")
    print(f"Electrons: {summary['n_electrons']}")
    print(f"Spatial orbitals: {summary['n_spatial_orbitals']}")
    print(f"Spin orbitals: {summary['n_spin_orbitals']}")
    print(f"Fixed-particle sector dimension: {summary['full_fixed_particle_sector_dimension']}")
    print(f"Nuclear repulsion: {summary['nuclear_repulsion_hartree']:.12f} Ha")
    print(f"HF total: {summary['hf_total_hartree']:.12f} Ha")
    print(f"FCI status: {summary['fci_status']}")
    if summary["fci_total_hartree"] is not None:
        print(f"FCI total: {summary['fci_total_hartree']:.12f} Ha")
    print(f"Full local diagonalization: {summary['local_full_space']['status']}")
    if summary["local_full_space"]["status"] != "ok":
        print(f"Reason: {summary['local_full_space']['reason']}")
    casci = summary["casci_active_space"]
    print(f"CASCI active space: {casci['active_space']}")
    print(f"CASCI basis size: {casci['basis_size']}")
    print(f"CASCI core energy shift: {casci['core_energy_shift_hartree']:.12f} Ha")
    print(f"PySCF CASCI total: {casci['pyscf_casci_total_hartree']:.12f} Ha")
    print(f"Local CASCI total: {casci['local_casci_total_hartree']:.12f} Ha")
    print(f"Local - PySCF CASCI: {casci['local_minus_pyscf_casci_hartree']:.6e} Ha")
    print(f"Note: {casci['note']}")
    print(f"Summary saved to: {_display_path(output_path)}")


def main(output_path: Path = SUMMARY_PATH) -> None:
    summary = run_validation(output_path=output_path)
    print_summary(summary, output_path=output_path)


if __name__ == "__main__":
    main()
