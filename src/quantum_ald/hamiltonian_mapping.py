"""Fermion-to-qubit Hamiltonian mapping utilities."""

from __future__ import annotations

import itertools
from math import comb
from typing import Any, List, Tuple

import numpy as np

from ._optional import require_module


def _count_occupied_orbitals(state: int) -> int:
    return bin(int(state)).count("1")


def particle_number_basis(n_spin_orbitals: int, n_electrons: int) -> List[int]:
    """Return occupation bitstrings with exactly ``n_electrons`` electrons."""
    if n_electrons < 0:
        raise ValueError("Number of electrons must be non-negative")
    if n_electrons > n_spin_orbitals:
        raise ValueError("Active space has fewer spin-orbitals than electrons")

    basis = []
    for occ in itertools.combinations(range(n_spin_orbitals), n_electrons):
        bits = 0
        for orbital in occ:
            bits |= 1 << orbital
        basis.append(bits)
    return basis


def restrict_to_particle_number(
    H: np.ndarray, n_spin_orbitals: int, n_electrons: int
) -> Tuple[np.ndarray, List[int]]:
    """Restrict a full Fock-space Hamiltonian to a fixed-particle sector."""
    expected_dim = 2**n_spin_orbitals
    if H.shape != (expected_dim, expected_dim):
        raise ValueError(
            f"Expected a {expected_dim}x{expected_dim} full Fock-space matrix, got {H.shape}"
        )

    basis = particle_number_basis(n_spin_orbitals, n_electrons)
    rows = np.asarray(basis, dtype=int)
    return np.asarray(H)[rows[:, None], rows], basis


def build_many_body_hamiltonian(
    mf: Any, active_space: dict[str, int] | None = None
) -> Tuple[np.ndarray, List[int]]:
    """Build the many-body Hamiltonian matrix in the occupation-number basis.

    This routine constructs the Hamiltonian H for a small active space using
    MO-transformed one- and two-electron integrals and returns a dense matrix
    along with the list of occupation bitstrings (integers) that define the
    basis. The function is intended for small active spaces (e.g. H2 CAS(2,2)).
    """
    # Obtain MO integrals
    hcore_ao = mf.get_hcore()
    mo_coeff = mf.mo_coeff
    # Determine spatial orbitals to include
    n_spatial = mo_coeff.shape[1]
    if active_space is not None:
        n_spatial = min(active_space.get("num_spatial_orbitals", n_spatial), n_spatial)
    C = mo_coeff[:, :n_spatial]

    # Transform one-electron integrals to MO basis (spatial)
    h1_mo = C.T @ hcore_ao @ C

    # Two-electron AO integrals
    eri_ao = mf.mol.intor("int2e")
    # Transform to spatial MO integrals: (p q|r s)
    # naive transformation (sufficient for small basis sizes)
    eri_mo = np.einsum("pi,qj,rk,sl,pqrs->ijkl", C, C, C, C, eri_ao, optimize=True)

    # Build spin-orbital one- and two-electron integrals
    n_spin = 2 * n_spatial
    h1_spin = np.zeros((n_spin, n_spin))
    for p in range(n_spatial):
        for q in range(n_spatial):
            for sp in (0, 1):
                for sq in (0, 1):
                    if sp == sq:
                        P = 2 * p + sp
                        Q = 2 * q + sq
                        h1_spin[P, Q] = h1_mo[p, q]

    # two-electron integrals in spin-orbital basis:
    # <P Q | R S> = <p q | r s> * delta(sp, sr) * delta(sq, ss)
    eri_spin = np.zeros((n_spin, n_spin, n_spin, n_spin))
    for p in range(n_spatial):
        for q in range(n_spatial):
            for r in range(n_spatial):
                for s in range(n_spatial):
                    # For a_p^† a_q^† a_s a_r, the spatial integral from
                    # chemist's notation is (p r | q s), not (p q | r s).
                    val = eri_mo[p, r, q, s]
                    for sp in (0, 1):
                        for sq in (0, 1):
                            for sr in (0, 1):
                                for ss in (0, 1):
                                    P = 2 * p + sp
                                    Q = 2 * q + sq
                                    R = 2 * r + sr
                                    S = 2 * s + ss
                                    if sp == sr and sq == ss:
                                        eri_spin[P, Q, R, S] = val

    # Active space selection: use lowest-energy spin-orbitals
    n_electrons = mf.mol.nelectron
    if active_space is not None:
        n_electrons = active_space.get("num_electrons", int(n_electrons))

    # Choose spin-orbitals 0..(n_active_spin-1)
    n_active_spin = 2 * (active_space.get("num_spatial_orbitals") if active_space else n_spatial)
    n_active_spin = min(n_active_spin, n_spin)

    # Construct the physical fixed-particle-number sector directly.
    basis = particle_number_basis(n_active_spin, int(n_electrons))
    expected_dim = comb(n_active_spin, int(n_electrons))
    if len(basis) != expected_dim:
        raise RuntimeError("Failed to construct the fixed-particle-number basis")

    dim = len(basis)
    H = np.zeros((dim, dim))

    # Helper: fermionic sign for annihilation/creation
    def popcount(x: int) -> int:
        return bin(x).count("1")

    def apply_annihilate(state: int, q: int):
        if (state >> q) & 1 == 0:
            return None
        mask = (1 << q) - 1
        sign = (-1) ** popcount(state & mask)
        return state & ~(1 << q), sign

    def apply_create(state: int, p: int):
        if (state >> p) & 1 == 1:
            return None
        mask = (1 << p) - 1
        sign = (-1) ** popcount(state & mask)
        return state | (1 << p), sign

    for i, bra in enumerate(basis):
        for j, ket in enumerate(basis):
            val = 0.0
            # one-body terms
            for p in range(n_active_spin):
                for q in range(n_active_spin):
                    # apply a_p^† a_q to ket and see if equals bra
                    res = apply_annihilate(ket, q)
                    if res is None:
                        continue
                    state1, s1 = res
                    res2 = apply_create(state1, p)
                    if res2 is None:
                        continue
                    state2, s2 = res2
                    if state2 == bra:
                        val += h1_spin[p, q] * s1 * s2

            # two-body terms:
            # PySCF ERIs are in chemist's notation (pq|rs). The electronic
            # Hamiltonian is 1/2 * (pr|qs) a_p^† a_q^† a_s a_r, so the
            # rightmost annihilation operator a_r acts first on the ket.
            for p in range(n_active_spin):
                for q in range(n_active_spin):
                    for r in range(n_active_spin):
                        for s in range(n_active_spin):
                            res = apply_annihilate(ket, r)
                            if res is None:
                                continue
                            state1, s1 = res
                            res = apply_annihilate(state1, s)
                            if res is None:
                                continue
                            state2, s2 = res
                            res = apply_create(state2, q)
                            if res is None:
                                continue
                            state3, s3 = res
                            res = apply_create(state3, p)
                            if res is None:
                                continue
                            state4, s4 = res
                            if state4 == bra:
                                val += 0.5 * eri_spin[p, q, r, s] * s1 * s2 * s3 * s4

            H[i, j] = val

    return H, basis


def build_many_body_hamiltonian_from_integrals(
    h1_spatial: np.ndarray,
    eri_spatial: np.ndarray,
    n_electrons: int,
) -> Tuple[np.ndarray, List[int]]:
    """Build a fixed-electron Hamiltonian from spatial-orbital integrals.

    ``eri_spatial`` is expected in PySCF/chemist notation ``(p q | r s)``.
    Constant energy shifts, such as CASCI core energy, should be added by the
    caller after diagonalization.
    """
    h1_spatial = np.asarray(h1_spatial)
    eri_spatial = np.asarray(eri_spatial)
    n_spatial = int(h1_spatial.shape[0])
    n_spin = 2 * n_spatial

    h1_spin = np.zeros((n_spin, n_spin))
    for p in range(n_spatial):
        for q in range(n_spatial):
            for spin in (0, 1):
                h1_spin[2 * p + spin, 2 * q + spin] = h1_spatial[p, q]

    eri_spin = np.zeros((n_spin, n_spin, n_spin, n_spin))
    for p in range(n_spatial):
        for q in range(n_spatial):
            for r in range(n_spatial):
                for s in range(n_spatial):
                    val = eri_spatial[p, r, q, s]
                    for spin_p in (0, 1):
                        for spin_q in (0, 1):
                            P = 2 * p + spin_p
                            Q = 2 * q + spin_q
                            R = 2 * r + spin_p
                            S = 2 * s + spin_q
                            eri_spin[P, Q, R, S] = val

    basis = particle_number_basis(n_spin, int(n_electrons))
    H = np.zeros((len(basis), len(basis)))

    def apply_annihilate(state: int, q: int):
        if (state >> q) & 1 == 0:
            return None
        mask = (1 << q) - 1
        sign = (-1) ** _count_occupied_orbitals(state & mask)
        return state & ~(1 << q), sign

    def apply_create(state: int, p: int):
        if (state >> p) & 1 == 1:
            return None
        mask = (1 << p) - 1
        sign = (-1) ** _count_occupied_orbitals(state & mask)
        return state | (1 << p), sign

    for i, bra in enumerate(basis):
        for j, ket in enumerate(basis):
            val = 0.0
            for p in range(n_spin):
                for q in range(n_spin):
                    res = apply_annihilate(ket, q)
                    if res is None:
                        continue
                    state1, sign1 = res
                    res = apply_create(state1, p)
                    if res is None:
                        continue
                    state2, sign2 = res
                    if state2 == bra:
                        val += h1_spin[p, q] * sign1 * sign2

            for p in range(n_spin):
                for q in range(n_spin):
                    for r in range(n_spin):
                        for s in range(n_spin):
                            res = apply_annihilate(ket, r)
                            if res is None:
                                continue
                            state1, sign1 = res
                            res = apply_annihilate(state1, s)
                            if res is None:
                                continue
                            state2, sign2 = res
                            res = apply_create(state2, q)
                            if res is None:
                                continue
                            state3, sign3 = res
                            res = apply_create(state3, p)
                            if res is None:
                                continue
                            state4, sign4 = res
                            if state4 == bra:
                                val += (
                                    0.5
                                    * eri_spin[p, q, r, s]
                                    * sign1
                                    * sign2
                                    * sign3
                                    * sign4
                                )
            H[i, j] = val

    return H, basis


def get_fermion_hamiltonian(mf: Any, active_space: dict[str, int] | None = None) -> Any:
    """Construct a FermionOperator from PySCF molecular-orbital integrals.

    The returned Hamiltonian contains the electronic terms only. Add
    ``mf.mol.energy_nuc()`` when comparing with total PySCF energies.
    """
    openfermion = require_module("openfermion", "chemistry")

    hcore_ao = mf.get_hcore()
    mo_coeff = mf.mo_coeff
    n_spatial = mo_coeff.shape[1]
    if active_space is not None:
        n_spatial = min(active_space.get("num_spatial_orbitals", n_spatial), n_spatial)
    C = mo_coeff[:, :n_spatial]

    h1_mo = C.T @ hcore_ao @ C
    eri_ao = mf.mol.intor("int2e")
    eri_mo = np.einsum("pi,qj,rk,sl,pqrs->ijkl", C, C, C, C, eri_ao, optimize=True)

    hamiltonian = openfermion.FermionOperator()
    for p in range(n_spatial):
        for q in range(n_spatial):
            for spin in (0, 1):
                P = 2 * p + spin
                Q = 2 * q + spin
                hamiltonian += openfermion.FermionOperator(((P, 1), (Q, 0)), h1_mo[p, q])

    for p in range(n_spatial):
        for q in range(n_spatial):
            for r in range(n_spatial):
                for s in range(n_spatial):
                    coefficient = 0.5 * eri_mo[p, r, q, s]
                    if abs(coefficient) < 1e-15:
                        continue
                    for spin_p in (0, 1):
                        for spin_q in (0, 1):
                            P = 2 * p + spin_p
                            Q = 2 * q + spin_q
                            R = 2 * r + spin_p
                            S = 2 * s + spin_q
                            hamiltonian += openfermion.FermionOperator(
                                ((P, 1), (Q, 1), (S, 0), (R, 0)),
                                coefficient,
                            )

    return hamiltonian


# Conventions used in this module:
# - Spin-orbital ordering: for a spatial orbital index p, we use spin-orbital
#   indices `2*p` (alpha) and `2*p+1` (beta). This ordering is consistent with
#   many quantum-chemistry codes and with the mapping used when converting a
#   FermionOperator to a qubit operator via Jordan-Wigner (occupied -> qubit=1).
# - Fermionic operator signs: standard creation/annihilation operators with
#   canonical anticommutation relations are assumed. When building the many-body
#   Hamiltonian in `build_many_body_hamiltonian` we explicitly account for
#   fermionic sign arising from moving operators past occupied orbitals.
# - Integral conventions: `h1e` is the one-electron core Hamiltonian in the
#   molecular-orbital (MO) basis (spatial). PySCF ERIs are in chemist's
#   notation (p q | r s). In the spin-orbital Hamiltonian term
#   1/2 (p r | q s) a_p^† a_q^† a_s a_r, the tensor indices are permuted
#   accordingly before operator application.
# - Nuclear repulsion: the FermionOperator built here has no constant nuclear
#   term; if comparing total electronic+nuclear energies, add the nuclear
#   repulsion energy from the PySCF `mf.mol.energy_nuc()` when needed.


def map_to_qubit_hamiltonian_jw(fermion_hamiltonian: Any) -> Any:
    """Map a FermionOperator to qubits with Jordan-Wigner."""
    transforms = require_module("openfermion.transforms", "chemistry")
    return transforms.jordan_wigner(fermion_hamiltonian)


def map_to_qubit_hamiltonian_bk(fermion_hamiltonian: Any) -> Any:
    """Map a FermionOperator to qubits with Bravyi-Kitaev."""
    transforms = require_module("openfermion.transforms", "chemistry")
    return transforms.bravyi_kitaev(fermion_hamiltonian)


def map_to_qubit_hamiltonian(
    mf: Any, active_space: dict[str, int], mapping: str = "jordan-wigner"
) -> Any:
    """Build and map a fermionic Hamiltonian to a qubit Hamiltonian."""
    fermion_hamiltonian = get_fermion_hamiltonian(mf, active_space)
    if mapping == "jordan-wigner":
        return map_to_qubit_hamiltonian_jw(fermion_hamiltonian)
    if mapping == "bravyi-kitaev":
        return map_to_qubit_hamiltonian_bk(fermion_hamiltonian)
    raise ValueError(f"Unknown mapping: {mapping}")


def get_qubit_operator_terms(qubit_hamiltonian: Any) -> tuple[np.ndarray, np.ndarray]:
    """Return Pauli terms and coefficients from an OpenFermion QubitOperator."""
    terms: list[str] = []
    coeffs: list[complex] = []
    for pauli_term, coeff in qubit_hamiltonian.terms.items():
        terms.append(str(pauli_term))
        coeffs.append(coeff)
    return np.asarray(terms), np.asarray(coeffs)
