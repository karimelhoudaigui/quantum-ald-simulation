"""Canonical electronic-integral data and spin-orbital conventions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np


SPIN_ORBITAL_ORDER = "interleaved_alpha_beta"
SPIN_LABELS = ("alpha", "beta")


def spin_orbital_index(spatial_orbital: int, spin: int) -> int:
    """Return the interleaved spin-orbital index ``2 * spatial + spin``."""
    if spatial_orbital < 0:
        raise ValueError("spatial_orbital must be non-negative")
    if spin not in (0, 1):
        raise ValueError("spin must be 0 (alpha) or 1 (beta)")
    return 2 * spatial_orbital + spin


def spatial_index(spin_orbital: int) -> int:
    if spin_orbital < 0:
        raise ValueError("spin_orbital must be non-negative")
    return spin_orbital // 2


def spin_index(spin_orbital: int) -> int:
    if spin_orbital < 0:
        raise ValueError("spin_orbital must be non-negative")
    return spin_orbital % 2


def spin_orbital_label(spin_orbital: int) -> tuple[str, int]:
    """Return ``(spin, spatial index)`` for the canonical ordering."""
    return SPIN_LABELS[spin_index(spin_orbital)], spatial_index(spin_orbital)


@dataclass(frozen=True)
class ElectronicHamiltonianData:
    """Spatial-MO integrals and metadata for an electronic Hamiltonian.

    ``eri_mo`` uses PySCF chemist notation ``(p q | r s)``. The data contains
    no constant Hamiltonian term: ``nuclear_repulsion`` must be added once to
    an electronic eigenvalue when a molecular total energy is required.
    """

    h1_mo: np.ndarray
    eri_mo: np.ndarray
    n_electrons: int
    n_spatial_orbitals: int
    n_spin_orbitals: int
    nuclear_repulsion: float
    spin_orbital_order: str = SPIN_ORBITAL_ORDER
    orbital_indices: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        n = self.n_spatial_orbitals
        if np.shape(self.h1_mo) != (n, n):
            raise ValueError(f"h1_mo must have shape {(n, n)}")
        if np.shape(self.eri_mo) != (n, n, n, n):
            raise ValueError(f"eri_mo must have shape {(n, n, n, n)}")
        if self.n_spin_orbitals != 2 * n:
            raise ValueError("n_spin_orbitals must equal 2 * n_spatial_orbitals")
        if self.spin_orbital_order != SPIN_ORBITAL_ORDER:
            raise ValueError(f"unsupported spin-orbital order: {self.spin_orbital_order}")
        if self.orbital_indices and len(self.orbital_indices) != n:
            raise ValueError("orbital_indices must match n_spatial_orbitals")


@dataclass(frozen=True)
class SpinOrbitalHamiltonianData:
    """Spin-orbital tensors for ``H = h[P,Q] a†P aQ + 1/2 g[P,Q,R,S] a†P a†Q aS aR``."""

    h1: np.ndarray
    eri: np.ndarray
    n_spin_orbitals: int
    spin_orbital_order: str = SPIN_ORBITAL_ORDER


def extract_electronic_hamiltonian_data(
    mf: Any,
    orbital_indices: Sequence[int] | None = None,
    n_electrons: int | None = None,
) -> ElectronicHamiltonianData:
    """Extract spatial-MO integrals once from a converged PySCF RHF object."""
    mo_coeff = np.asarray(mf.mo_coeff)
    indices = tuple(range(mo_coeff.shape[1])) if orbital_indices is None else tuple(orbital_indices)
    if not indices:
        raise ValueError("at least one spatial orbital is required")
    if min(indices) < 0 or max(indices) >= mo_coeff.shape[1]:
        raise ValueError("orbital index is outside the MO coefficient matrix")

    coefficients = mo_coeff[:, indices]
    h1_mo = coefficients.T.conj() @ np.asarray(mf.get_hcore()) @ coefficients
    eri_ao = np.asarray(mf.mol.intor("int2e"))
    eri_mo = np.einsum(
        "pi,qj,rk,sl,pqrs->ijkl",
        coefficients.conj(),
        coefficients,
        coefficients.conj(),
        coefficients,
        eri_ao,
        optimize=True,
    )
    n_spatial = len(indices)
    electrons = int(mf.mol.nelectron if n_electrons is None else n_electrons)
    return ElectronicHamiltonianData(
        h1_mo=np.asarray(h1_mo),
        eri_mo=np.asarray(eri_mo),
        n_electrons=electrons,
        n_spatial_orbitals=n_spatial,
        n_spin_orbitals=2 * n_spatial,
        nuclear_repulsion=float(mf.mol.energy_nuc()),
        orbital_indices=indices,
    )


def build_spin_orbital_integrals(
    h1_mo: np.ndarray,
    eri_mo: np.ndarray,
) -> SpinOrbitalHamiltonianData:
    """Expand spatial integrals into the canonical spin-orbital tensors.

    Input ERIs use chemist notation ``(p q | r s)``. The returned tensor is
    indexed for ``1/2 * g[P,Q,R,S] a†P a†Q aS aR`` and therefore stores
    ``g[P,Q,R,S] = (p r | q s)`` when spins P/R and Q/S match.
    """
    h1_mo = np.asarray(h1_mo)
    eri_mo = np.asarray(eri_mo)
    if h1_mo.ndim != 2 or h1_mo.shape[0] != h1_mo.shape[1]:
        raise ValueError("h1_mo must be a square matrix")
    n_spatial = int(h1_mo.shape[0])
    if eri_mo.shape != (n_spatial, n_spatial, n_spatial, n_spatial):
        raise ValueError("eri_mo shape is inconsistent with h1_mo")

    n_spin = 2 * n_spatial
    h1_spin = np.zeros((n_spin, n_spin), dtype=np.result_type(h1_mo, float))
    eri_spin = np.zeros(
        (n_spin, n_spin, n_spin, n_spin),
        dtype=np.result_type(eri_mo, float),
    )
    for p in range(n_spatial):
        for q in range(n_spatial):
            for spin in (0, 1):
                P = spin_orbital_index(p, spin)
                Q = spin_orbital_index(q, spin)
                h1_spin[P, Q] = h1_mo[p, q]

    for p in range(n_spatial):
        for q in range(n_spatial):
            for r in range(n_spatial):
                for s in range(n_spatial):
                    value = eri_mo[p, r, q, s]
                    for spin_p in (0, 1):
                        for spin_q in (0, 1):
                            P = spin_orbital_index(p, spin_p)
                            Q = spin_orbital_index(q, spin_q)
                            R = spin_orbital_index(r, spin_p)
                            S = spin_orbital_index(s, spin_q)
                            eri_spin[P, Q, R, S] = value

    return SpinOrbitalHamiltonianData(h1=h1_spin, eri=eri_spin, n_spin_orbitals=n_spin)


def expand_to_spin_orbitals(data: ElectronicHamiltonianData) -> SpinOrbitalHamiltonianData:
    """Expand canonical spatial-MO data using the project's spin convention."""
    return build_spin_orbital_integrals(data.h1_mo, data.eri_mo)
