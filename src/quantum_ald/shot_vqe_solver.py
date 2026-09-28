"""Finite-shot VQE optimization driven exclusively by Pauli counts."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from ._optional import require_module
from .pauli_measurement import estimate_energy_from_paulis


def evaluate_shot_vqe_objective(
    theta: float,
    ansatz: Any,
    parameter: Any,
    hamiltonian: Any,
    nuclear_repulsion: float,
    shots_per_term: int,
    seed: int,
    backend: Any | None = None,
) -> dict[str, Any]:
    """Evaluate one VQE point using only finite-shot Pauli counts."""
    bound_circuit = ansatz.assign_parameters({parameter: float(theta)}, inplace=False)
    measurement = estimate_energy_from_paulis(
        bound_circuit,
        hamiltonian,
        shots=shots_per_term,
        seed=seed,
        backend=backend,
    )
    return {
        "energy_electronic": measurement["energy"],
        "energy_total": measurement["energy"] + nuclear_repulsion,
        "standard_error_estimate": measurement["standard_error"],
        "num_measurement_circuits": measurement["num_measurement_circuits"],
        "total_shots": measurement["total_shots"],
    }


class ShotBasedVQESolver:
    """One-dimensional periodic grid/refinement VQE for stochastic energies."""

    def __init__(
        self,
        ansatz: Any,
        parameter: Any,
        hamiltonian: Any,
        nuclear_repulsion: float,
        shots_per_term: int,
        seed: int,
        coarse_points: int = 9,
        refinement_points: int = 17,
        objective: Callable[..., dict[str, Any]] = evaluate_shot_vqe_objective,
        backend: Any | None = None,
    ) -> None:
        if coarse_points < 3 or refinement_points < 3:
            raise ValueError("grid sizes must each contain at least three points")
        self.ansatz = ansatz
        self.parameter = parameter
        self.hamiltonian = hamiltonian
        self.nuclear_repulsion = float(nuclear_repulsion)
        self.shots_per_term = shots_per_term
        self.seed = seed
        self.coarse_points = coarse_points
        self.refinement_points = refinement_points
        self.objective = objective
        self.backend = backend or require_module("qiskit_aer", "quantum").AerSimulator()
        self.trace: list[dict[str, Any]] = []

    @staticmethod
    def _wrap(theta: float) -> float:
        return float((theta + np.pi) % (2 * np.pi) - np.pi)

    def _evaluate(self, theta: float, stage: str) -> dict[str, Any]:
        point = self.objective(
            self._wrap(theta),
            self.ansatz,
            self.parameter,
            self.hamiltonian,
            self.nuclear_repulsion,
            self.shots_per_term,
            self.seed,
            self.backend,
        )
        record = {
            "evaluation_index": len(self.trace),
            "theta": self._wrap(theta),
            "energy_electronic": float(point["energy_electronic"]),
            "energy_total": float(point["energy_total"]),
            "estimated_standard_error": float(point["standard_error_estimate"]),
            "shots_per_term": self.shots_per_term,
            "seed": self.seed,
            "num_measurement_circuits": int(point["num_measurement_circuits"]),
            "total_shots": int(point["total_shots"]),
            "stage": stage,
        }
        self.trace.append(record)
        return record

    def solve(self, theta_initial: float) -> dict[str, Any]:
        """Run initial evaluation, global grid, then local periodic refinement."""
        self.trace = []
        self._evaluate(theta_initial, "initial")
        coarse = np.linspace(-np.pi, np.pi, self.coarse_points, endpoint=False)
        coarse_records = [self._evaluate(float(theta), "coarse") for theta in coarse]
        coarse_best = min(coarse_records, key=lambda row: row["energy_electronic"])
        spacing = 2 * np.pi / self.coarse_points
        offsets = np.linspace(-spacing / 2, spacing / 2, self.refinement_points)
        refinement = [
            self._evaluate(coarse_best["theta"] + float(offset), "refinement")
            for offset in offsets
        ]
        best = min([coarse_best, *refinement], key=lambda row: row["energy_electronic"])
        circuits = sum(row["num_measurement_circuits"] for row in self.trace)
        total_shots = sum(row["total_shots"] for row in self.trace)
        return {
            "strategy": "periodic_grid_refinement",
            "theta_initial": self._wrap(theta_initial),
            "theta_final": best["theta"],
            "final_energy_electronic": best["energy_electronic"],
            "final_energy_total": best["energy_total"],
            "final_standard_error": best["estimated_standard_error"],
            "num_energy_evaluations": len(self.trace),
            "total_measurement_circuits": circuits,
            "total_shots": total_shots,
            "trace": list(self.trace),
        }
