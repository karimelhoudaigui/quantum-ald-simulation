"""Pure-NumPy Jordan-Wigner reference for tests and validation reports.

This module intentionally does not import OpenFermion or Qiskit. It is not a
production mapping backend; it independently implements the defining algebra.
Matrix indices follow the project convention: qubit ``p`` is bit ``p`` of the
computational-basis integer, so qubit zero is the rightmost Kronecker factor.
"""

from __future__ import annotations

import itertools

import numpy as np

from ..electronic_structure import SpinOrbitalHamiltonianData


I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI_MATRICES = {"I": I2, "X": X, "Y": Y, "Z": Z}


def _kron_for_qubits(operators: dict[int, np.ndarray], n_qubits: int) -> np.ndarray:
    matrix = np.asarray([[1.0]], dtype=complex)
    for qubit in reversed(range(n_qubits)):
        matrix = np.kron(matrix, operators.get(qubit, I2))
    return matrix


def reference_jw_annihilation(orbital: int, n_qubits: int) -> np.ndarray:
    """Return ``a_p = (X_p + iY_p)/2 product_(j<p) Z_j``."""
    if orbital < 0 or orbital >= n_qubits:
        raise ValueError("orbital index is outside the qubit register")
    operators = {index: Z for index in range(orbital)}
    operators[orbital] = (X + 1j * Y) / 2.0
    return _kron_for_qubits(operators, n_qubits)


def reference_jw_creation(orbital: int, n_qubits: int) -> np.ndarray:
    """Return ``a†_p = (X_p - iY_p)/2 product_(j<p) Z_j``."""
    return reference_jw_annihilation(orbital, n_qubits).conj().T


def reference_jw_hamiltonian(data: SpinOrbitalHamiltonianData) -> np.ndarray:
    """Build the full-Fock-space electronic Hamiltonian from JW matrices."""
    n_qubits = data.n_spin_orbitals
    dim = 2**n_qubits
    annihilation = [reference_jw_annihilation(p, n_qubits) for p in range(n_qubits)]
    creation = [operator.conj().T for operator in annihilation]
    hamiltonian = np.zeros((dim, dim), dtype=complex)

    for p in range(n_qubits):
        for q in range(n_qubits):
            if abs(data.h1[p, q]) > 0.0:
                hamiltonian += data.h1[p, q] * creation[p] @ annihilation[q]

    for p in range(n_qubits):
        for q in range(n_qubits):
            for r in range(n_qubits):
                for s in range(n_qubits):
                    if abs(data.eri[p, q, r, s]) > 0.0:
                        hamiltonian += (
                            0.5
                            * data.eri[p, q, r, s]
                            * creation[p]
                            @ creation[q]
                            @ annihilation[s]
                            @ annihilation[r]
                        )
    return hamiltonian


def reference_number_operator(n_qubits: int) -> np.ndarray:
    """Construct ``N = sum_p a†_p a_p`` from reference JW operators."""
    dim = 2**n_qubits
    number = np.zeros((dim, dim), dtype=complex)
    for orbital in range(n_qubits):
        annihilation = reference_jw_annihilation(orbital, n_qubits)
        number += annihilation.conj().T @ annihilation
    return number


def number_operator_from_z(n_qubits: int) -> np.ndarray:
    """Construct ``N = sum_p (I - Z_p)/2`` independently."""
    dim = 2**n_qubits
    number = np.zeros((dim, dim), dtype=complex)
    identity = np.eye(dim, dtype=complex)
    for orbital in range(n_qubits):
        number += (identity - _kron_for_qubits({orbital: Z}, n_qubits)) / 2.0
    return number


def pauli_matrix(label: str) -> np.ndarray:
    """Return a matrix for a Qiskit-style big-endian Pauli label."""
    matrix = np.asarray([[1.0]], dtype=complex)
    for character in label:
        matrix = np.kron(matrix, PAULI_MATRICES[character])
    return matrix


def decompose_pauli(matrix: np.ndarray, tolerance: float = 1e-12) -> dict[str, complex]:
    """Decompose a small matrix in the orthogonal Pauli basis."""
    matrix = np.asarray(matrix, dtype=complex)
    dim = matrix.shape[0]
    n_qubits = int(round(np.log2(dim)))
    if matrix.shape != (2**n_qubits, 2**n_qubits):
        raise ValueError("matrix dimension must be a power-of-two square")

    terms: dict[str, complex] = {}
    for characters in itertools.product("IXYZ", repeat=n_qubits):
        label = "".join(characters)
        pauli = pauli_matrix(label)
        coefficient = complex(np.trace(pauli.conj().T @ matrix) / dim)
        if abs(coefficient) > tolerance:
            terms[label] = coefficient
    return terms
