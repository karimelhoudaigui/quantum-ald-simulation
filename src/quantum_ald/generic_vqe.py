"""Generic multiparameter VQE with an explicit energy-evaluation backend."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Protocol

import numpy as np

from ._optional import require_module
from .ansatz import PreparedAnsatz
from .quantum_problem import PreparedQuantumProblem

SUPPORTED_OPTIMIZERS = ("slsqp",)
SUPPORTED_EXECUTION_MODES = ("exact_statevector",)


class EnergyEvaluator(Protocol):
    """Backend boundary required by the generic optimizer."""

    mode: str

    def evaluate(self, circuit: Any, hamiltonian: Any, parameters: np.ndarray) -> float:
        """Return one active-space energy expectation value."""


class StatevectorEstimatorEvaluator:
    """Exact Qiskit StatevectorEstimator energy backend."""

    mode = "exact_statevector"

    def __init__(self, estimator: Any | None = None) -> None:
        if estimator is None:
            primitives = require_module("qiskit.primitives", "quantum")
            estimator = primitives.StatevectorEstimator(default_precision=0.0)
        self.estimator = estimator

    def evaluate(self, circuit: Any, hamiltonian: Any, parameters: np.ndarray) -> float:
        values = self.estimator.run([(circuit, hamiltonian, parameters)]).result()[0].data.evs
        value = complex(np.asarray(values).item())
        if abs(value.imag) > 1e-10:
            raise ValueError(f"exact estimator returned a complex energy: {value}")
        energy = float(value.real)
        if not np.isfinite(energy):
            raise ValueError("exact estimator returned a non-finite energy")
        return energy


@dataclass(frozen=True)
class VQESolverConfig:
    """Serializable configuration for the exact generic VQE solver."""

    optimizer: str = "slsqp"
    maxiter: int = 100
    tolerance: float = 1e-9
    initialization: str = "ansatz_default"
    random_seeds: tuple[int, ...] = ()
    random_scale: float = 0.05
    execution_mode: str = "exact_statevector"

    def __post_init__(self) -> None:
        optimizer = self.optimizer.strip().lower()
        execution_mode = self.execution_mode.strip().lower()
        object.__setattr__(self, "optimizer", optimizer)
        object.__setattr__(self, "execution_mode", execution_mode)
        object.__setattr__(self, "random_seeds", tuple(self.random_seeds))
        if optimizer not in SUPPORTED_OPTIMIZERS:
            supported = ", ".join(SUPPORTED_OPTIMIZERS)
            raise ValueError(f"unsupported optimizer: {optimizer}; supported: {supported}")
        if execution_mode not in SUPPORTED_EXECUTION_MODES:
            supported = ", ".join(SUPPORTED_EXECUTION_MODES)
            raise ValueError(
                f"unsupported execution_mode: {execution_mode}; supported: {supported}"
            )
        if isinstance(self.maxiter, bool) or not isinstance(self.maxiter, int) or self.maxiter < 1:
            raise ValueError("maxiter must be a positive integer")
        if not np.isfinite(self.tolerance) or self.tolerance <= 0.0:
            raise ValueError("tolerance must be positive and finite")
        if self.initialization != "ansatz_default":
            raise ValueError("only initialization='ansatz_default' is supported")
        if len(set(self.random_seeds)) != len(self.random_seeds):
            raise ValueError("random_seeds must not contain duplicates")
        if any(isinstance(seed, bool) or not isinstance(seed, int) for seed in self.random_seeds):
            raise TypeError("random_seeds must contain integers")
        if not np.isfinite(self.random_scale) or self.random_scale <= 0.0:
            raise ValueError("random_scale must be positive and finite")

    def to_dict(self) -> dict[str, Any]:
        return {
            "optimizer": self.optimizer,
            "maxiter": self.maxiter,
            "tolerance": self.tolerance,
            "initialization": self.initialization,
            "random_seeds": list(self.random_seeds),
            "random_scale": self.random_scale,
            "execution_mode": self.execution_mode,
        }


@dataclass(frozen=True)
class VQEConvergencePoint:
    """One exact objective evaluation."""

    evaluation: int
    optimizer_iteration: int
    energy_active: float
    energy_total: float
    parameter_norm: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "evaluation": self.evaluation,
            "optimizer_iteration": self.optimizer_iteration,
            "energy_active": self.energy_active,
            "energy_total": self.energy_total,
            "parameter_norm": self.parameter_norm,
        }


@dataclass(frozen=True)
class VQERunResult:
    """Result and convergence trace for one optimizer initialization."""

    initialization: str
    seed: int | None
    status: str
    converged: bool
    initial_parameters: tuple[float, ...]
    optimal_parameters: tuple[float, ...]
    initial_energy_active: float | None
    initial_energy_total: float | None
    optimal_energy_active: float | None
    optimal_energy_total: float | None
    num_evaluations: int
    optimizer_evaluations: int
    num_iterations: int | None
    termination_message: str
    runtime_seconds: float
    convergence_history: tuple[VQEConvergencePoint, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "initialization": self.initialization,
            "seed": self.seed,
            "status": self.status,
            "converged": self.converged,
            "initial_parameters": list(self.initial_parameters),
            "optimal_parameters": list(self.optimal_parameters),
            "initial_energy_active": self.initial_energy_active,
            "initial_energy_total": self.initial_energy_total,
            "optimal_energy_active": self.optimal_energy_active,
            "optimal_energy_total": self.optimal_energy_total,
            "num_evaluations": self.num_evaluations,
            "optimizer_evaluations": self.optimizer_evaluations,
            "num_iterations": self.num_iterations,
            "termination_message": self.termination_message,
            "runtime_seconds": self.runtime_seconds,
            "convergence_history": [point.to_dict() for point in self.convergence_history],
        }


@dataclass(frozen=True)
class VQEResult:
    """Solver-only VQE result with a selected primary multistart run."""

    status: str
    optimizer: str
    execution_mode: str
    converged: bool
    num_qubits: int
    num_parameters: int
    parameter_names: tuple[str, ...]
    constant_energy: float
    initial_parameters: tuple[float, ...]
    optimal_parameters: tuple[float, ...]
    initial_energy_active: float | None
    initial_energy_total: float | None
    optimal_energy_active: float | None
    optimal_energy_total: float | None
    num_evaluations: int
    num_iterations: int | None
    termination_message: str
    runtime_seconds: float
    primary_run_index: int | None
    runs: tuple[VQERunResult, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_metadata(self) -> dict[str, Any]:
        final_energies = [
            run.optimal_energy_total for run in self.runs if run.optimal_energy_total is not None
        ]
        return {
            "status": self.status,
            "optimizer": self.optimizer,
            "execution_mode": self.execution_mode,
            "converged": self.converged,
            "num_qubits": self.num_qubits,
            "num_parameters": self.num_parameters,
            "parameter_names": list(self.parameter_names),
            "constant_energy": self.constant_energy,
            "initial_parameters": list(self.initial_parameters),
            "optimal_parameters": list(self.optimal_parameters),
            "initial_energy_active": self.initial_energy_active,
            "initial_energy_total": self.initial_energy_total,
            "optimal_energy_active": self.optimal_energy_active,
            "optimal_energy_total": self.optimal_energy_total,
            "num_evaluations": self.num_evaluations,
            "num_iterations": self.num_iterations,
            "termination_message": self.termination_message,
            "runtime_seconds": self.runtime_seconds,
            "primary_run_index": self.primary_run_index,
            "num_starts": len(self.runs),
            "final_energy_mean": (None if not final_energies else float(np.mean(final_energies))),
            "final_energy_std": (None if not final_energies else float(np.std(final_energies))),
            "runs": [run.to_dict() for run in self.runs],
            "metadata": dict(self.metadata),
        }


class GenericVQESolver:
    """Optimize a prepared circuit against a prepared Hamiltonian."""

    def __init__(
        self,
        config: VQESolverConfig | None = None,
        evaluator: EnergyEvaluator | None = None,
    ) -> None:
        self.config = config or VQESolverConfig()
        self.evaluator = evaluator or StatevectorEstimatorEvaluator()
        if self.evaluator.mode != self.config.execution_mode:
            raise ValueError(
                f"evaluator mode {self.evaluator.mode!r} does not match "
                f"execution_mode {self.config.execution_mode!r}"
            )

    @staticmethod
    def _validate_inputs(
        quantum_problem: PreparedQuantumProblem,
        prepared_ansatz: PreparedAnsatz,
    ) -> None:
        if not isinstance(quantum_problem, PreparedQuantumProblem):
            raise TypeError("quantum_problem must be a PreparedQuantumProblem")
        if not isinstance(prepared_ansatz, PreparedAnsatz):
            raise TypeError("prepared_ansatz must be a PreparedAnsatz")
        if prepared_ansatz.num_qubits != quantum_problem.num_qubits:
            raise ValueError("prepared ansatz and quantum problem qubit counts differ")
        if int(quantum_problem.hamiltonian.num_qubits) != prepared_ansatz.num_qubits:
            raise ValueError("prepared Hamiltonian and ansatz qubit counts differ")
        if int(prepared_ansatz.circuit.num_parameters) != prepared_ansatz.num_parameters:
            raise ValueError("prepared ansatz parameter count is inconsistent")
        if len(prepared_ansatz.initial_parameters) != prepared_ansatz.num_parameters:
            raise ValueError("prepared ansatz initial parameter count is inconsistent")

    def _initial_points(
        self,
        prepared_ansatz: PreparedAnsatz,
    ) -> list[tuple[str, int | None, np.ndarray]]:
        baseline = np.asarray(prepared_ansatz.initial_parameters, dtype=float)
        points = [("zeros", None, baseline)]
        for seed in self.config.random_seeds:
            offset = np.random.default_rng(seed).uniform(
                -self.config.random_scale,
                self.config.random_scale,
                prepared_ansatz.num_parameters,
            )
            points.append(("small_random", seed, baseline + offset))
        return points

    def _run_start(
        self,
        quantum_problem: PreparedQuantumProblem,
        prepared_ansatz: PreparedAnsatz,
        initialization: str,
        seed: int | None,
        initial_parameters: np.ndarray,
    ) -> VQERunResult:
        optimize = require_module("scipy.optimize", "chemistry")
        history: list[VQEConvergencePoint] = []
        evaluated_parameters: list[np.ndarray] = []
        optimizer_iteration = 0
        started = perf_counter()

        def evaluate(parameters: np.ndarray, iteration: int) -> float:
            vector = np.asarray(parameters, dtype=float)
            if vector.shape != (prepared_ansatz.num_parameters,):
                raise ValueError("optimizer parameter vector has an invalid shape")
            energy_active = self.evaluator.evaluate(
                prepared_ansatz.circuit,
                quantum_problem.hamiltonian,
                vector,
            )
            energy_total = quantum_problem.total_energy(energy_active)
            history.append(
                VQEConvergencePoint(
                    evaluation=len(history) + 1,
                    optimizer_iteration=iteration,
                    energy_active=energy_active,
                    energy_total=energy_total,
                    parameter_norm=float(np.linalg.norm(vector)),
                )
            )
            evaluated_parameters.append(vector.copy())
            return energy_active

        try:
            initial_energy_active = evaluate(initial_parameters, 0)
            initial_energy_total = quantum_problem.total_energy(initial_energy_active)

            if prepared_ansatz.num_parameters == 0:
                return VQERunResult(
                    initialization=initialization,
                    seed=seed,
                    status="converged",
                    converged=True,
                    initial_parameters=tuple(float(x) for x in initial_parameters),
                    optimal_parameters=tuple(float(x) for x in initial_parameters),
                    initial_energy_active=initial_energy_active,
                    initial_energy_total=initial_energy_total,
                    optimal_energy_active=initial_energy_active,
                    optimal_energy_total=initial_energy_total,
                    num_evaluations=1,
                    optimizer_evaluations=0,
                    num_iterations=0,
                    termination_message="zero-parameter ansatz",
                    runtime_seconds=perf_counter() - started,
                    convergence_history=tuple(history),
                )

            def objective(parameters: np.ndarray) -> float:
                return evaluate(parameters, optimizer_iteration + 1)

            def callback(_parameters: np.ndarray) -> None:
                nonlocal optimizer_iteration
                optimizer_iteration += 1

            result = optimize.minimize(
                objective,
                initial_parameters,
                method="SLSQP",
                callback=callback,
                options={
                    "maxiter": self.config.maxiter,
                    "ftol": self.config.tolerance,
                    "disp": False,
                },
            )
            optimal_parameters = np.asarray(result.x, dtype=float)
            optimal_energy_active = float(result.fun)
            optimal_energy_total = quantum_problem.total_energy(optimal_energy_active)
            converged = bool(result.success)
            return VQERunResult(
                initialization=initialization,
                seed=seed,
                status="converged" if converged else "not_converged",
                converged=converged,
                initial_parameters=tuple(float(x) for x in initial_parameters),
                optimal_parameters=tuple(float(x) for x in optimal_parameters),
                initial_energy_active=initial_energy_active,
                initial_energy_total=initial_energy_total,
                optimal_energy_active=optimal_energy_active,
                optimal_energy_total=optimal_energy_total,
                num_evaluations=len(history),
                optimizer_evaluations=int(result.nfev),
                num_iterations=int(result.nit),
                termination_message=str(result.message),
                runtime_seconds=perf_counter() - started,
                convergence_history=tuple(history),
            )
        except Exception as exc:
            if history:
                best_index = int(np.argmin([point.energy_active for point in history]))
                best_parameters = evaluated_parameters[best_index]
                best_active = history[best_index].energy_active
                best_total = history[best_index].energy_total
                initial_active = history[0].energy_active
                initial_total = history[0].energy_total
            else:
                best_parameters = initial_parameters
                best_active = None
                best_total = None
                initial_active = None
                initial_total = None
            return VQERunResult(
                initialization=initialization,
                seed=seed,
                status="failed",
                converged=False,
                initial_parameters=tuple(float(x) for x in initial_parameters),
                optimal_parameters=tuple(float(x) for x in best_parameters),
                initial_energy_active=initial_active,
                initial_energy_total=initial_total,
                optimal_energy_active=best_active,
                optimal_energy_total=best_total,
                num_evaluations=len(history),
                optimizer_evaluations=max(0, len(history) - 1),
                num_iterations=optimizer_iteration,
                termination_message=f"{type(exc).__name__}: {exc}",
                runtime_seconds=perf_counter() - started,
                convergence_history=tuple(history),
            )

    def solve(
        self,
        quantum_problem: PreparedQuantumProblem,
        prepared_ansatz: PreparedAnsatz,
    ) -> VQEResult:
        """Run all configured starts and select the best converged energy."""
        self._validate_inputs(quantum_problem, prepared_ansatz)
        started = perf_counter()
        runs = tuple(
            self._run_start(
                quantum_problem,
                prepared_ansatz,
                initialization,
                seed,
                initial_parameters,
            )
            for initialization, seed, initial_parameters in self._initial_points(prepared_ansatz)
        )
        converged_indices = [
            index
            for index, run in enumerate(runs)
            if run.converged and run.optimal_energy_active is not None
        ]
        finite_indices = [
            index for index, run in enumerate(runs) if run.optimal_energy_active is not None
        ]
        candidates = converged_indices or finite_indices
        primary_index = (
            min(candidates, key=lambda index: float(runs[index].optimal_energy_active))
            if candidates
            else None
        )
        if primary_index is None:
            primary = runs[0]
            status = "failed"
        else:
            primary = runs[primary_index]
            status = "converged" if converged_indices else "not_converged"
        return VQEResult(
            status=status,
            optimizer=self.config.optimizer,
            execution_mode=self.config.execution_mode,
            converged=status == "converged",
            num_qubits=prepared_ansatz.num_qubits,
            num_parameters=prepared_ansatz.num_parameters,
            parameter_names=prepared_ansatz.parameter_names,
            constant_energy=quantum_problem.constant_energy,
            initial_parameters=primary.initial_parameters,
            optimal_parameters=primary.optimal_parameters,
            initial_energy_active=primary.initial_energy_active,
            initial_energy_total=primary.initial_energy_total,
            optimal_energy_active=primary.optimal_energy_active,
            optimal_energy_total=primary.optimal_energy_total,
            num_evaluations=primary.num_evaluations,
            num_iterations=primary.num_iterations,
            termination_message=primary.termination_message,
            runtime_seconds=perf_counter() - started,
            primary_run_index=primary_index,
            runs=runs,
            metadata={
                "solver": type(self).__name__,
                "evaluator": type(self.evaluator).__name__,
                "primary_selection": "lowest converged total energy",
                "exact_diagonalization_fallback": False,
                "solver_config": self.config.to_dict(),
            },
        )


def run_vqe(
    quantum_problem: PreparedQuantumProblem,
    prepared_ansatz: PreparedAnsatz,
    config: VQESolverConfig | None = None,
    evaluator: EnergyEvaluator | None = None,
) -> VQEResult:
    """Convenience entry point for the generic VQE solver."""
    return GenericVQESolver(config=config, evaluator=evaluator).solve(
        quantum_problem,
        prepared_ansatz,
    )
