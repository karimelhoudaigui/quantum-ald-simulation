"""Variational Quantum Eigensolver wrapper."""

from __future__ import annotations

from typing import Any

import numpy as np

from ._optional import require_module


class VQESolver:
    """Small VQE interface around Qiskit primitives."""

    def __init__(
        self,
        num_qubits: int,
        num_electrons: int | None = None,
        ansatz_type: str = "twolocal",
        optimizer: str = "cobyla",
        max_iter: int = 300,
    ):
        self.num_qubits = num_qubits
        self.num_electrons = num_electrons or 0
        self.ansatz_type = ansatz_type
        self.max_iter = max_iter
        self.history: dict[str, list[float]] = {"iterations": [], "energies": []}
        self.optimizer = self._build_optimizer(optimizer)
        self.ansatz = self._build_ansatz()
        self.result: Any | None = None

    def _build_optimizer(self, optimizer: str) -> Any:
        optimizers = require_module("qiskit_algorithms.optimizers", "quantum")
        if optimizer == "cobyla":
            return optimizers.COBYLA(maxiter=self.max_iter)
        if optimizer == "l_bfgs_b":
            return optimizers.L_BFGS_B(maxiter=self.max_iter)
        raise ValueError(f"Unknown optimizer: {optimizer}")

    def _build_ansatz(self) -> Any:
        library = require_module("qiskit.circuit.library", "quantum")
        if self.ansatz_type == "twolocal":
            return library.TwoLocal(
                self.num_qubits,
                rotation_blocks="ry",
                entanglement_blocks="cz",
                entanglement="linear",
                reps=2,
            )
        if self.ansatz_type == "uccsd":
            if self.num_electrons == 0:
                raise ValueError("num_electrons is required for UCCSD")
            return library.UCCSD(
                num_spatial_orbitals=self.num_qubits // 2,
                num_particles=self.num_electrons,
                reps=1,
            )
        return library.TwoLocal(self.num_qubits, rotation_blocks="ry", entanglement_blocks="cz", reps=1)

    def solve(self, hamiltonian: Any, estimator: Any | None = None) -> tuple[float, np.ndarray]:
        """Run VQE and return the minimum energy and optimal parameters."""
        algorithms = require_module("qiskit_algorithms", "quantum")
        if estimator is None:
            try:
                primitives = require_module("qiskit.primitives", "quantum")
                estimator = primitives.Estimator()
            except AttributeError:
                primitives = require_module("qiskit_aer.primitives", "quantum")
                estimator = primitives.Estimator()

        def callback(*args: Any) -> None:
            energy = float(args[-1]) if args else np.nan
            self.history["iterations"].append(float(len(self.history["iterations"])))
            self.history["energies"].append(energy)

        vqe = algorithms.VQE(estimator=estimator, ansatz=self.ansatz, optimizer=self.optimizer, callback=callback)
        self.result = vqe.compute_minimum_eigenvalue(hamiltonian)
        return float(np.real(self.result.eigenvalue)), np.asarray(self.result.optimal_point)

    def get_convergence_history(self) -> dict[str, list[float]]:
        return self.history

    def get_circuit(self, parameters: np.ndarray | None = None) -> Any:
        if parameters is None:
            return self.ansatz
        return self.ansatz.assign_parameters(parameters)


class FallbackVQESolver:
    """Simple pure-Python variational solver for very small systems.

    This solver works directly with a dense many-body Hamiltonian matrix and
    performs a classical variational optimization over a real parameter vector
    that defines the trial state. For reliability it attempts an optimization
    and falls back to exact diagonalization if needed.
    """

    def __init__(self, max_iter: int = 100, optimizer: str = "BFGS"):
        self.max_iter = max_iter
        self.history: dict[str, list[float]] = {"iterations": [], "energies": []}
        self.optimizer = optimizer
        self.result = None

    def _energy(self, x: np.ndarray, H: np.ndarray) -> float:
        if x.ndim != 1:
            x = np.ravel(x)
        norm = np.linalg.norm(x)
        if norm == 0:
            return float(np.inf)
        psi = x / norm
        e = float(np.real(psi.conj() @ (H @ psi)))
        return e

    def solve(self, H: np.ndarray) -> tuple[float, np.ndarray]:
        n = H.shape[0]
        # initial random vector biased to HF-like occupation (first basis state)
        x0 = np.zeros(n)
        x0[0] = 1.0

        from scipy import optimize

        def fun(x):
            e = self._energy(x, H)
            self.history["iterations"].append(len(self.history["iterations"]))
            self.history["energies"].append(e)
            return e

        try:
            res = optimize.minimize(fun, x0, method=self.optimizer, options={"maxiter": self.max_iter})
            if res.success:
                energy = self._energy(res.x, H)
                self.result = res
                params = res.x / np.linalg.norm(res.x)
                return float(energy), params
        except Exception:
            pass

        # Fallback: exact diagonalization
        evals, evecs = np.linalg.eigh(H)
        idx = int(np.argmin(evals))
        energy = float(evals[idx])
        params = np.asarray(evecs[:, idx], dtype=float)
        params = params / np.linalg.norm(params)
        self.result = {"eigenvalue": energy, "eigenvector": params}
        # record fallback in history
        self.history["iterations"].append(0)
        self.history["energies"].append(energy)
        return energy, params

    def get_convergence_history(self) -> dict[str, list[float]]:
        return self.history


def openfermion_qubit_operator_to_sparse_pauli(qubit_operator: Any, num_qubits: int) -> Any:
    """Convert an OpenFermion QubitOperator to Qiskit's SparsePauliOp."""
    quantum_info = require_module("qiskit.quantum_info", "quantum")

    labels: list[str] = []
    coeffs: list[complex] = []
    for term, coeff in qubit_operator.terms.items():
        pauli = ["I"] * num_qubits
        for index, operator in term:
            # Qiskit labels are big-endian; OpenFermion qubit 0 is the
            # rightmost character in the Pauli label.
            pauli[num_qubits - 1 - index] = operator
        labels.append("".join(pauli))
        coeffs.append(complex(coeff))

    if not labels:
        labels = ["I" * num_qubits]
        coeffs = [0.0]

    return quantum_info.SparsePauliOp(labels, coeffs=np.asarray(coeffs, dtype=complex))


def dense_matrix_to_sparse_pauli(matrix: np.ndarray, tolerance: float = 1e-12) -> Any:
    """Decompose a small dense qubit Hamiltonian into Qiskit SparsePauliOp terms."""
    quantum_info = require_module("qiskit.quantum_info", "quantum")
    matrix = np.asarray(matrix, dtype=complex)
    dim = matrix.shape[0]
    num_qubits = int(round(np.log2(dim)))
    if matrix.shape != (2**num_qubits, 2**num_qubits):
        raise ValueError("Matrix dimension must be a power-of-two square")

    single = {
        "I": np.array([[1, 0], [0, 1]], dtype=complex),
        "X": np.array([[0, 1], [1, 0]], dtype=complex),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    }

    labels: list[str] = []
    coeffs: list[complex] = []

    import itertools

    for label_tuple in itertools.product("IXYZ", repeat=num_qubits):
        label = "".join(label_tuple)
        pauli = single[label[0]]
        for item in label[1:]:
            pauli = np.kron(pauli, single[item])
        coeff = np.trace(pauli.conj().T @ matrix) / dim
        if abs(coeff) > tolerance:
            labels.append(label)
            coeffs.append(complex(coeff))

    if not labels:
        labels = ["I" * num_qubits]
        coeffs = [0.0]

    return quantum_info.SparsePauliOp(labels, coeffs=np.asarray(coeffs, dtype=complex))


class QiskitVQESolver:
    """Noiseless Qiskit statevector VQE for small Pauli Hamiltonians.

    This class intentionally avoids depending on fast-moving Qiskit Algorithms
    VQE APIs. It uses Qiskit for the ansatz, Pauli Hamiltonian representation
    and statevector simulation, with SciPy providing the classical optimizer.
    """

    def __init__(
        self,
        num_qubits: int,
        max_iter: int = 200,
        reps: int = 2,
        seed: int = 7,
        ansatz_type: str = "twolocal",
        occupied_orbitals: tuple[int, ...] | None = None,
        excitation_orbitals: tuple[int, ...] | None = None,
    ):
        self.num_qubits = num_qubits
        self.max_iter = max_iter
        self.reps = reps
        self.seed = seed
        self.ansatz_type = ansatz_type
        self.occupied_orbitals = occupied_orbitals or (0, 1)
        self.excitation_orbitals = excitation_orbitals or (2, 3)
        self.history: dict[str, list[float]] = {"iterations": [], "energies": []}
        self.result: Any | None = None
        self.ansatz = self._build_ansatz()

    def _build_ansatz(self) -> Any:
        if self.ansatz_type == "h2_pair":
            return None
        if self.ansatz_type != "twolocal":
            raise ValueError(f"Unknown ansatz_type: {self.ansatz_type}")
        library = require_module("qiskit.circuit.library", "quantum")
        return library.TwoLocal(
            self.num_qubits,
            rotation_blocks="ry",
            entanglement_blocks="cz",
            entanglement="linear",
            reps=self.reps,
        )

    def _basis_state(self, orbitals: tuple[int, ...]) -> int:
        state = 0
        for orbital in orbitals:
            if orbital < 0 or orbital >= self.num_qubits:
                raise ValueError("orbital index is outside the qubit register")
            state |= 1 << orbital
        return state

    def _h2_pair_statevector(self, parameters: np.ndarray) -> Any:
        if self.num_qubits != 4:
            raise ValueError("h2_pair ansatz is defined for the four-qubit H2 minimal basis")

        statevector_cls = require_module("qiskit.quantum_info", "quantum").Statevector
        theta = float(np.ravel(parameters)[0])
        vector = np.zeros(2**self.num_qubits, dtype=complex)
        vector[self._basis_state(self.occupied_orbitals)] = np.cos(theta)
        vector[self._basis_state(self.excitation_orbitals)] = np.sin(theta)
        return statevector_cls(vector)

    def _energy(self, parameters: np.ndarray, hamiltonian: Any) -> float:
        if self.ansatz_type == "h2_pair":
            state = self._h2_pair_statevector(parameters)
        else:
            statevector_cls = require_module("qiskit.quantum_info", "quantum").Statevector
            circuit = self.ansatz.assign_parameters(parameters, inplace=False)
            state = statevector_cls.from_instruction(circuit)
        energy = state.expectation_value(hamiltonian)
        return float(np.real(energy))

    def _initial_points(self) -> list[np.ndarray]:
        if self.ansatz_type == "h2_pair":
            grid = np.linspace(-np.pi, np.pi, 17)
            return [np.asarray([theta], dtype=float) for theta in grid]

        rng = np.random.default_rng(self.seed)
        return [rng.uniform(-0.05, 0.05, self.ansatz.num_parameters)]

    def solve(self, hamiltonian: Any) -> tuple[float, np.ndarray]:
        """Run noiseless statevector VQE and return energy and parameters."""
        optimize = require_module("scipy.optimize", "chemistry")

        def objective(parameters: np.ndarray) -> float:
            energy = self._energy(parameters, hamiltonian)
            self.history["iterations"].append(float(len(self.history["iterations"])))
            self.history["energies"].append(energy)
            return energy

        method = "Nelder-Mead" if self.ansatz_type == "h2_pair" else "COBYLA"
        best_result = None
        best_energy = float("inf")

        for initial_point in self._initial_points():
            result = optimize.minimize(
                objective,
                initial_point,
                method=method,
                options={"maxiter": self.max_iter},
            )
            energy = self._energy(np.asarray(result.x), hamiltonian)
            if energy < best_energy:
                best_energy = float(energy)
                best_result = result

        self.result = best_result
        return best_energy, np.asarray(best_result.x)

    def get_convergence_history(self) -> dict[str, list[float]]:
        return self.history
