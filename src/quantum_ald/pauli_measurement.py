"""Exact and finite-shot measurements of Pauli Hamiltonians."""

from __future__ import annotations

from typing import Any, Iterator

import numpy as np

from ._optional import require_module


def iter_pauli_terms(hamiltonian: Any) -> Iterator[tuple[str, complex]]:
    """Yield Qiskit big-endian Pauli labels and coefficients."""
    for label, coefficient in hamiltonian.to_list():
        yield str(label), complex(coefficient)


def is_identity_pauli(label: str) -> bool:
    return all(operator == "I" for operator in label)


def build_pauli_measurement_circuit(circuit: Any, label: str) -> Any | None:
    """Append basis rotations and q-to-c measurements for one Pauli string."""
    if len(label) != circuit.num_qubits:
        raise ValueError("Pauli label length must match the circuit qubit count")
    if set(label) - set("IXYZ"):
        raise ValueError("Pauli label may contain only I, X, Y and Z")
    if is_identity_pauli(label):
        return None

    qiskit = require_module("qiskit", "quantum")
    measured = qiskit.QuantumCircuit(circuit.num_qubits, circuit.num_qubits)
    measured.compose(circuit, inplace=True)
    for qubit in range(circuit.num_qubits):
        operator = label[-1 - qubit]
        if operator == "X":
            measured.h(qubit)
        elif operator == "Y":
            measured.sdg(qubit)
            measured.h(qubit)
    measured.measure(range(circuit.num_qubits), range(circuit.num_qubits))
    return measured


def pauli_eigenvalue(bitstring: str, label: str) -> int:
    """Return the measured eigenvalue using Qiskit's c[n-1]...c[0] display."""
    bits = bitstring.replace(" ", "")
    if len(bits) != len(label):
        raise ValueError("bitstring and Pauli label lengths differ")
    eigenvalue = 1
    for qubit in range(len(label)):
        if label[-1 - qubit] != "I" and bits[-1 - qubit] == "1":
            eigenvalue *= -1
    return eigenvalue


def expectation_from_counts(counts: dict[str, int], label: str) -> float:
    shots = sum(counts.values())
    if shots <= 0:
        raise ValueError("counts must contain at least one shot")
    return sum(count * pauli_eigenvalue(bits, label) for bits, count in counts.items()) / shots


def estimate_pauli_expectation(
    circuit: Any,
    label: str,
    shots: int,
    seed: int | None = None,
    backend: Any | None = None,
) -> float:
    """Estimate one Pauli expectation from an actual counts experiment."""
    if shots <= 0:
        raise ValueError("shots must be positive")
    measured = build_pauli_measurement_circuit(circuit, label)
    if measured is None:
        return 1.0
    if backend is None:
        backend = require_module("qiskit_aer", "quantum").AerSimulator()
    qiskit = require_module("qiskit", "quantum")
    compiled = qiskit.transpile(measured, backend)
    result = backend.run(compiled, shots=shots, seed_simulator=seed).result()
    return expectation_from_counts(result.get_counts(), label)


def exact_pauli_energy(circuit: Any, hamiltonian: Any) -> dict[str, Any]:
    """Reconstruct an exact energy term by term from a circuit statevector."""
    quantum_info = require_module("qiskit.quantum_info", "quantum")
    state = quantum_info.Statevector.from_instruction(circuit)
    terms = []
    energy = 0.0 + 0.0j
    for label, coefficient in iter_pauli_terms(hamiltonian):
        expectation = 1.0 if is_identity_pauli(label) else state.expectation_value(
            quantum_info.Pauli(label)
        )
        contribution = coefficient * expectation
        energy += contribution
        terms.append(
            {
                "pauli": label,
                "coefficient": float(np.real(coefficient)),
                "expectation": float(np.real(expectation)),
                "contribution": float(np.real(contribution)),
            }
        )
    return {"energy": float(np.real(energy)), "terms": terms}


def evaluate_pauli_energy(
    circuit: Any,
    hamiltonian: Any,
    mode: str = "exact",
    shots: int | None = None,
    seed: int | None = None,
    backend: Any | None = None,
) -> dict[str, Any]:
    """Evaluate a Pauli Hamiltonian exactly or through finite-shot circuits."""
    if mode == "exact":
        return exact_pauli_energy(circuit, hamiltonian)
    if mode == "shots":
        if shots is None:
            raise ValueError("shots are required in shots mode")
        return estimate_energy_from_paulis(circuit, hamiltonian, shots, seed, backend)
    raise ValueError("mode must be 'exact' or 'shots'")


def estimate_energy_from_paulis(
    circuit: Any,
    hamiltonian: Any,
    shots: int,
    seed: int | None = None,
    backend: Any | None = None,
) -> dict[str, Any]:
    """Estimate energy from independent noiseless Aer measurements."""
    if shots <= 0:
        raise ValueError("shots must be positive")
    terms = list(iter_pauli_terms(hamiltonian))
    sampled = [(label, coeff) for label, coeff in terms if not is_identity_pauli(label)]
    if backend is None and sampled:
        backend = require_module("qiskit_aer", "quantum").AerSimulator()
    qiskit = require_module("qiskit", "quantum")
    circuits = [build_pauli_measurement_circuit(circuit, label) for label, _ in sampled]
    result = None
    if circuits:
        compiled = qiskit.transpile(circuits, backend)
        result = backend.run(compiled, shots=shots, seed_simulator=seed).result()

    diagnostics = []
    energy = 0.0
    variance = 0.0
    sampled_index = 0
    for label, coefficient in terms:
        coeff = float(np.real(coefficient))
        if is_identity_pauli(label):
            expectation = 1.0
            was_sampled = False
        else:
            expectation = expectation_from_counts(result.get_counts(sampled_index), label)
            variance += coeff**2 * max(0.0, 1.0 - expectation**2) / shots
            sampled_index += 1
            was_sampled = True
        contribution = coeff * expectation
        energy += contribution
        diagnostics.append(
            {
                "pauli": label,
                "coefficient": coeff,
                "expectation": expectation,
                "contribution": contribution,
                "sampled": was_sampled,
            }
        )

    return {
        "energy": energy,
        "standard_error": float(np.sqrt(variance)),
        "num_pauli_terms": len(terms),
        "num_measurement_circuits": len(sampled),
        "shots_per_term": shots,
        "total_shots": len(sampled) * shots,
        "seed": seed,
        "terms": diagnostics,
    }
