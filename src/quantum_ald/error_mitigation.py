"""Error mitigation techniques for hybrid quantum simulations."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np


class ZNE:
    """Zero-noise extrapolation with polynomial fitting."""

    def __init__(self, noise_factors: Sequence[float] = (1.0, 1.5, 2.0)):
        self.noise_factors = list(noise_factors)
        self.results: dict[float, float] = {}

    def execute(self, evaluate_fn: Callable[[float], float], noise_factors: Sequence[float] | None = None) -> float:
        factors = list(noise_factors or self.noise_factors)
        energies = [float(evaluate_fn(factor)) for factor in factors]
        self.results = dict(zip(factors, energies))
        slope, intercept = np.polyfit(np.asarray(factors), np.asarray(energies), deg=1)
        del slope
        return float(intercept)


class CDR:
    """Small linear calibration model inspired by Clifford data regression."""

    def __init__(self, num_samples: int = 100):
        self.num_samples = num_samples
        self.slope = 1.0
        self.intercept = 0.0

    def fit(self, noisy_values: Sequence[float], ideal_values: Sequence[float]) -> "CDR":
        """Fit a linear map from noisy to ideal expectation values."""
        noisy = np.asarray(list(noisy_values), dtype=float)
        ideal = np.asarray(list(ideal_values), dtype=float)
        if noisy.shape != ideal.shape:
            raise ValueError("noisy_values and ideal_values must have the same shape")
        if noisy.size == 0:
            raise ValueError("at least one calibration pair is required")

        if noisy.size == 1:
            self.slope = 1.0
            self.intercept = float(ideal[0] - noisy[0])
            return self

        self.slope, self.intercept = [float(x) for x in np.polyfit(noisy, ideal, deg=1)]
        return self

    def correct(self, noisy_result: float) -> float:
        """Apply the fitted linear correction."""
        return float(self.slope * noisy_result + self.intercept)

    def execute(self, noisy_result: float, ideal_result: float) -> float:
        """Backward-compatible one-point calibration helper."""
        self.fit([noisy_result], [ideal_result])
        return self.correct(noisy_result)
