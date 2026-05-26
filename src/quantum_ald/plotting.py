"""Visualization utilities for ALD quantum simulation outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_energy_profile(energies: dict[str, dict[str, float]], filename: str | Path) -> None:
    """Plot a reaction energy profile for several methods."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    states = ["R", "TS", "P"]
    x_pos = np.arange(len(states))
    width = 0.8 / max(len(energies), 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    for idx, (method, data) in enumerate(energies.items()):
        values = [data.get(state, 0.0) for state in states]
        ax.bar(x_pos + idx * width, values, width, label=method)

    ax.set_xlabel("Reaction state")
    ax.set_ylabel("Relative energy (Ha)")
    ax.set_title("Reaction Energy Profile")
    ax.set_xticks(x_pos + width * (len(energies) - 1) / 2)
    ax.set_xticklabels(states)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_vqe_convergence(history: dict[str, list[float]], filename: str | Path) -> None:
    """Plot VQE optimization history."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    iterations = history.get("iterations", [])
    energies = history.get("energies", [])
    if not iterations or not energies:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(iterations, energies, "o-", linewidth=2, markersize=4)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Energy (Ha)")
    ax.set_title("VQE Convergence")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_comparison(methods_data: dict[str, tuple[list[float], list[float]]], filename: str | Path) -> None:
    """Plot several method curves on the same axes."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    for method, (x_values, y_values) in methods_data.items():
        ax.plot(x_values, y_values, "o-", label=method, linewidth=2, markersize=6)
    ax.set_xlabel("Coordinate")
    ax.set_ylabel("Energy (Ha)")
    ax.set_title("Method Comparison")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
