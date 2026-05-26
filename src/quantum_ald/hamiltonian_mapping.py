"""Fermion-to-qubit Hamiltonian mapping utilities."""

from __future__ import annotations

from typing import Any

import numpy as np

from ._optional import require_module


def get_fermion_hamiltonian(mf: Any, active_space: dict[str, int] | None = None) -> Any:
    """Construct an approximate fermionic Hamiltonian from PySCF integrals.

    This routine provides a compact educational bridge to OpenFermion. For
    production quantum chemistry, spin-orbital integral conventions and active
    space projections should be validated carefully.
    """
    del active_space
    openfermion = require_module("openfermion", "chemistry")
    h1e = mf.get_hcore()
    eri = mf.mol.intor("int2e")
    interaction = openfermion.InteractionOperator(0.0, h1e, eri)
    return openfermion.get_fermion_operator(interaction)


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
