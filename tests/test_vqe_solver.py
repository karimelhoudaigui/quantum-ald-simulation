import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_algorithms")

from quantum_ald import VQESolver


def test_vqe_initialization() -> None:
    solver = VQESolver(num_qubits=4, ansatz_type="twolocal")
    assert solver.num_qubits == 4
    assert solver.ansatz is not None


def test_ansatz_building() -> None:
    solver = VQESolver(num_qubits=4, ansatz_type="twolocal")
    circuit = solver.get_circuit()
    assert circuit.num_qubits == 4
