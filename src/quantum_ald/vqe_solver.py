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
