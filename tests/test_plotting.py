from pathlib import Path

from quantum_ald import plot_energy_profile


def test_plot_energy_profile(tmp_path: Path) -> None:
    output = tmp_path / "energy_profile.png"
    plot_energy_profile({"HF": {"R": 0.0, "TS": 0.5, "P": -0.2}}, output)
    assert output.exists()
