"""Fermion-to-qubit Hamiltonian mapping utilities."""

from __future__ import annotations

import itertools
from typing import Any, List, Tuple

import numpy as np

from ._optional import require_module
from .active_space import PreparedElectronicProblem
from .electronic_structure import (
    ElectronicHamiltonianData,
    build_spin_orbital_integrals,
    expand_to_spin_orbitals,
    extract_electronic_hamiltonian_data,
)


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
    n_spatial = mf.mo_coeff.shape[1]
    if active_space is not None:
        n_spatial = min(active_space.get("num_spatial_orbitals", n_spatial), n_spatial)
    n_electrons = int(
        mf.mol.nelectron
        if active_space is None
        else active_space.get("num_electrons", mf.mol.nelectron)
    )
    data = extract_electronic_hamiltonian_data(
        mf,
        orbital_indices=range(n_spatial),
        n_electrons=n_electrons,
    )
    return build_many_body_hamiltonian_from_data(data)


def build_many_body_hamiltonian_from_data(
    data: ElectronicHamiltonianData,
) -> Tuple[np.ndarray, List[int]]:
    """Build a fixed-particle electronic Hamiltonian from canonical data."""
    return build_many_body_hamiltonian_from_integrals(data.h1_mo, data.eri_mo, data.n_electrons)


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
    spin_data = build_spin_orbital_integrals(h1_spatial, eri_spatial)
    h1_spin = spin_data.h1
    eri_spin = spin_data.eri
    n_spin = spin_data.n_spin_orbitals

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
    n_spatial = mf.mo_coeff.shape[1]
    if active_space is not None:
        n_spatial = min(active_space.get("num_spatial_orbitals", n_spatial), n_spatial)
    n_electrons = int(
        mf.mol.nelectron
        if active_space is None
        else active_space.get("num_electrons", mf.mol.nelectron)
    )
    data = extract_electronic_hamiltonian_data(
        mf,
        orbital_indices=range(n_spatial),
        n_electrons=n_electrons,
    )
    return get_fermion_hamiltonian_from_data(data)


def get_fermion_hamiltonian_from_data(data: ElectronicHamiltonianData) -> Any:
    """Construct the electronic FermionOperator from canonical MO data."""
    openfermion = require_module("openfermion", "chemistry")
    spin_data = expand_to_spin_orbitals(data)
    n_spin = spin_data.n_spin_orbitals

    hamiltonian = openfermion.FermionOperator()
    for P in range(n_spin):
        for Q in range(n_spin):
            coefficient = spin_data.h1[P, Q]
            if abs(coefficient) >= 1e-15:
                hamiltonian += openfermion.FermionOperator(((P, 1), (Q, 0)), coefficient)

    for P in range(n_spin):
        for Q in range(n_spin):
            for R in range(n_spin):
                for S in range(n_spin):
                    coefficient = 0.5 * spin_data.eri[P, Q, R, S]
                    if abs(coefficient) < 1e-15:
                        continue
                    hamiltonian += openfermion.FermionOperator(
                        ((P, 1), (Q, 1), (S, 0), (R, 0)),
                        coefficient,
                    )

    return hamiltonian


def get_fermion_hamiltonian_from_problem(problem: PreparedElectronicProblem) -> Any:
    """Build only the operator-valued part of a prepared active problem."""
    data = ElectronicHamiltonianData(
        h1_mo=problem.h1,
        eri_mo=problem.h2,
        n_electrons=problem.n_active_electrons,
        n_spatial_orbitals=problem.n_active_orbitals,
        n_spin_orbitals=problem.n_spin_orbitals,
        nuclear_repulsion=problem.nuclear_repulsion,
        orbital_indices=problem.active_orbital_indices,
    )
    return get_fermion_hamiltonian_from_data(data)


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


def map_fermion_hamiltonian(
    fermion_hamiltonian: Any,
    mapping: str = "jordan-wigner",
) -> Any:
    """Apply one of the mapping implementations already supported by the project."""
    if mapping == "jordan-wigner":
        return map_to_qubit_hamiltonian_jw(fermion_hamiltonian)
    if mapping == "bravyi-kitaev":
        return map_to_qubit_hamiltonian_bk(fermion_hamiltonian)
    raise ValueError(f"Unknown mapping: {mapping}")


def map_to_qubit_hamiltonian(
    mf: Any, active_space: dict[str, int], mapping: str = "jordan-wigner"
) -> Any:
    """Build and map a fermionic Hamiltonian to a qubit Hamiltonian."""
    fermion_hamiltonian = get_fermion_hamiltonian(mf, active_space)
    return map_fermion_hamiltonian(fermion_hamiltonian, mapping=mapping)


def map_prepared_problem_to_qubit(
    problem: PreparedElectronicProblem,
    mapping: str = "jordan-wigner",
) -> Any:
    """Map a prepared active problem while keeping its constant separate."""
    fermion_hamiltonian = get_fermion_hamiltonian_from_problem(problem)
    return map_fermion_hamiltonian(fermion_hamiltonian, mapping=mapping)


def get_qubit_operator_terms(qubit_hamiltonian: Any) -> tuple[np.ndarray, np.ndarray]:
    """Return Pauli terms and coefficients from an OpenFermion QubitOperator."""
    terms: list[str] = []
    coeffs: list[complex] = []
    for pauli_term, coeff in qubit_hamiltonian.terms.items():
        terms.append(str(pauli_term))
        coeffs.append(coeff)
    return np.asarray(terms), np.asarray(coeffs)
