"""Quantum noise models for ALD-oriented VQE simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ._optional import require_module


@dataclass(frozen=True)
class SyntheticNoiseProfile:
    """Synthetic hardware-like gate and asymmetric readout error rates."""

    name: str
    p_1q: float
    p_2q: float
    p_readout_01: float
    p_readout_10: float

    def __post_init__(self) -> None:
        for value in (self.p_1q, self.p_2q, self.p_readout_01, self.p_readout_10):
            if not 0.0 <= value <= 1.0:
                raise ValueError("noise probabilities must lie in [0, 1]")


SYNTHETIC_NOISE_PROFILES = {
    "ZERO": SyntheticNoiseProfile("ZERO", 0.0, 0.0, 0.0, 0.0),
    "LOW": SyntheticNoiseProfile("LOW", 0.0005, 0.005, 0.01, 0.015),
    "MEDIUM": SyntheticNoiseProfile("MEDIUM", 0.0015, 0.015, 0.025, 0.035),
    "HIGH": SyntheticNoiseProfile("HIGH", 0.005, 0.05, 0.05, 0.07),
}


def build_synthetic_noise_model(
    profile: SyntheticNoiseProfile,
    include_gate_errors: bool = True,
    include_readout_error: bool = True,
) -> Any:
    """Build an Aer noise model for transpiled sx/x/cx gates and readout."""
    noise = require_module("qiskit_aer.noise", "quantum")
    model = noise.NoiseModel()
    if include_gate_errors and profile.p_1q > 0:
        model.add_all_qubit_quantum_error(noise.depolarizing_error(profile.p_1q, 1), ["sx", "x"])
    if include_gate_errors and profile.p_2q > 0:
        model.add_all_qubit_quantum_error(noise.depolarizing_error(profile.p_2q, 2), ["cx"])
    if include_readout_error and (profile.p_readout_01 > 0 or profile.p_readout_10 > 0):
        readout = noise.ReadoutError(
            [
                [1.0 - profile.p_readout_01, profile.p_readout_01],
                [profile.p_readout_10, 1.0 - profile.p_readout_10],
            ]
        )
        model.add_all_qubit_readout_error(readout)
    return model


def build_noisy_aer_backend(
    profile: SyntheticNoiseProfile,
    include_gate_errors: bool = True,
    include_readout_error: bool = True,
) -> Any:
    """Return an Aer simulator executing the transpiled hardware-like basis."""
    aer = require_module("qiskit_aer", "quantum")
    model = build_synthetic_noise_model(profile, include_gate_errors, include_readout_error)
    return aer.AerSimulator(noise_model=model, basis_gates=["rz", "sx", "x", "cx"])


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
