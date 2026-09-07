"""Quantum noise models for ALD-oriented VQE simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ._optional import require_module


def simple_noise_model(error_rate: float = 0.01) -> Any:
    """Return a depolarizing Qiskit Aer noise model."""
    noise = require_module("qiskit_aer.noise", "quantum")
    model = noise.NoiseModel()
    model.add_all_qubit_quantum_error(noise.depolarizing_error(error_rate, 1), ["u3", "u2", "u1", "sx", "x"])
    model.add_all_qubit_quantum_error(noise.depolarizing_error(2 * error_rate, 2), ["cx"])
    return model


def carbon_nanotube_noise(t1: float = 1.0, t2: float = 0.5, gate_time: float = 0.1) -> Any:
    """Return a simple thermal-relaxation model inspired by nanotube qubits."""
    noise = require_module("qiskit_aer.noise", "quantum")
    model = noise.NoiseModel()
    one_qubit = noise.thermal_relaxation_error(t1, t2, gate_time)
    two_qubit = noise.thermal_relaxation_error(t1, t2, 2 * gate_time).tensor(
        noise.thermal_relaxation_error(t1, t2, 2 * gate_time)
    )
    model.add_all_qubit_quantum_error(one_qubit, ["u3", "u2", "u1", "sx", "x"])
    model.add_all_qubit_quantum_error(two_qubit, ["cx"])
    return model


@dataclass
class NoiseModel:
    """Configuration object for converting project noise assumptions to Qiskit."""

    name: str = "custom"
    params: dict[str, float] = field(default_factory=dict)

    def add_depolarizing(self, error_rate: float) -> None:
        self.params["depolarizing"] = error_rate

    def add_thermal(self, t1: float, t2: float) -> None:
        self.params["t1"] = t1
        self.params["t2"] = t2

    def to_qiskit_noise_model(self) -> Any:
        if "depolarizing" in self.params:
            return simple_noise_model(self.params["depolarizing"])
        if "t1" in self.params and "t2" in self.params:
            return carbon_nanotube_noise(self.params["t1"], self.params["t2"])
        noise = require_module("qiskit_aer.noise", "quantum")
        return noise.NoiseModel()


@dataclass(frozen=True)
class DepolarizingNoiseProfile:
    """Analytic depolarizing profile for lightweight noisy-VQE studies.

    The profile compresses a circuit into approximate one- and two-qubit gate
    counts, then mixes the ideal energy with the maximally mixed-state energy.
    It is intentionally simple and deterministic, so it can be used in
    reproducible validation scripts without requiring a sampler backend.
    """

    error_rate: float = 0.005
    one_qubit_gates: int = 0
    two_qubit_gates: int = 0

    def __post_init__(self) -> None:
        if self.error_rate < 0:
            raise ValueError("error_rate must be non-negative")
        if self.one_qubit_gates < 0 or self.two_qubit_gates < 0:
            raise ValueError("gate counts must be non-negative")

    def effective_probability(self, noise_factor: float = 1.0) -> float:
        """Return the total depolarizing probability at a noise scale factor."""
        if noise_factor < 0:
            raise ValueError("noise_factor must be non-negative")

        p1 = float(np.clip(self.error_rate * noise_factor, 0.0, 1.0))
        p2 = float(np.clip(2.0 * self.error_rate * noise_factor, 0.0, 1.0))
        survival = (1.0 - p1) ** self.one_qubit_gates
        survival *= (1.0 - p2) ** self.two_qubit_gates
        return float(1.0 - survival)

    def mix_energy(
        self,
        ideal_energy: float,
        maximally_mixed_energy: float,
        noise_factor: float = 1.0,
    ) -> float:
        """Apply the analytic depolarizing channel to an expectation value."""
        probability = self.effective_probability(noise_factor)
        return float((1.0 - probability) * ideal_energy + probability * maximally_mixed_energy)
