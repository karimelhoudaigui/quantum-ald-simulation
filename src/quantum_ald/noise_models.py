"""Quantum noise models for ALD-oriented VQE simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
