"""Active-space definitions for quantum chemistry reductions."""

from __future__ import annotations

from typing import Any

import numpy as np

from ._optional import require_module


def define_active_space(n_electrons: int, n_orbitals: int) -> dict[str, int]:
    """Define a complete active space CAS(n_electrons, n_orbitals)."""
    if n_electrons <= 0 or n_orbitals <= 0:
        raise ValueError("active electrons and orbitals must be positive")
    if n_electrons > 2 * n_orbitals:
        raise ValueError("too many electrons for the requested spatial orbitals")
    return {
        "num_electrons": n_electrons,
        "num_spatial_orbitals": n_orbitals,
        "num_qubits_spinorbitals": 2 * n_orbitals,
    }


def simple_active_space(mf: Any, orbital_indices: list[int]) -> tuple[np.ndarray, int]:
    """Select active orbitals manually from a mean-field object."""
    mo_coeff = mf.mo_coeff[:, orbital_indices]
    occupied = set(range(mf.mol.nelectron // 2))
    n_electrons = 2 * sum(index in occupied for index in orbital_indices)
    return np.asarray(mo_coeff), int(n_electrons)


def avas_selection(mf: Any, atomlist: list[str], minao: str = "minao") -> dict[str, Any]:
    """Run PySCF AVAS active-space selection."""
    avas = require_module("pyscf.mcscf.avas", "chemistry")
    ncas, nelecas, mo_coeff = avas.avas(mf, atomlist, minao=minao)
    return {"n_electrons": nelecas, "n_orbitals": ncas, "mo_coeff": mo_coeff}


def CAS_2_2() -> dict[str, int]:
    return define_active_space(2, 2)


def CAS_4_4() -> dict[str, int]:
    return define_active_space(4, 4)


def CAS_6_6() -> dict[str, int]:
    return define_active_space(6, 6)


def CAS_8_8() -> dict[str, int]:
    return define_active_space(8, 8)
