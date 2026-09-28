"""Gate-based four-qubit H2 pair ansatz."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from ._optional import require_module


def prepare_hartree_fock_state(circuit: Any, occupied_orbitals: Iterable[int]) -> None:
    """Prepare an occupation-basis determinant with explicit X gates."""
    for orbital in occupied_orbitals:
        if orbital < 0 or orbital >= circuit.num_qubits:
            raise ValueError("occupied orbital is outside the qubit register")
        circuit.x(orbital)


def apply_h2_pair_excitation(circuit: Any, theta: Any) -> None:
    """Apply the gate decomposition rotating ``|0011>`` into ``|1100>``.

    A reversible basis change maps the two determinants to ``|0111>`` and
    ``|1111>``. A three-controlled ``RY(2*theta)`` then performs the desired
    two-level rotation before the basis change is uncomputed.
    """
    if circuit.num_qubits != 4:
        raise ValueError("the H2 pair excitation requires exactly four qubits")
    library = require_module("qiskit.circuit.library", "quantum")

    for target in (0, 1, 2):
        circuit.cx(3, target)
    circuit.x(2)
    circuit.append(library.RYGate(2 * theta).control(3), [0, 1, 2, 3])
    circuit.x(2)
    for target in (2, 1, 0):
        circuit.cx(3, target)


def build_h2_pair_ansatz() -> tuple[Any, Any]:
    """Return a reusable parameterized circuit and its ``theta`` parameter."""
    qiskit_circuit = require_module("qiskit.circuit", "quantum")
    circuit = qiskit_circuit.QuantumCircuit(4, name="H2Pair")
    theta = qiskit_circuit.Parameter("theta")
    prepare_hartree_fock_state(circuit, occupied_orbitals=(0, 1))
    apply_h2_pair_excitation(circuit, theta)
    return circuit, theta
