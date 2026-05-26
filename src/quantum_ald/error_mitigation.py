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
    """Minimal Clifford-data-regression-style linear correction placeholder."""

    def __init__(self, num_samples: int = 100):
        self.num_samples = num_samples

    def execute(self, noisy_result: float, ideal_result: float) -> float:
        if noisy_result == 0:
            return float(ideal_result)
        return float(noisy_result * (ideal_result / noisy_result))
