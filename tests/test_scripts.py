import importlib.util
import json
import runpy
from pathlib import Path

import pytest


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def test_scripts_importable() -> None:
    # Load scripts by path to avoid relying on sys.path modifications
    project = Path(__file__).resolve().parents[1]
    validate = load_script(project / "scripts" / "validate_install.py")
    run_h2 = load_script(project / "scripts" / "run_h2_vqe.py")
    validate_h2 = load_script(project / "scripts" / "validate_h2_pipeline.py")
    assert hasattr(validate, "main")
    assert hasattr(run_h2, "main")
    assert hasattr(validate_h2, "main")


def test_run_h2_vqe_smoke() -> None:
    # This test performs a quick HF + FCI on H2; skip if pyscf missing
    pytest.importorskip("pyscf")
    project = Path(__file__).resolve().parents[1]
    run_h2 = load_script(project / "scripts" / "run_h2_vqe.py")
    # Run the main pipeline; it should complete for H2 in minimal basis
    run_h2.main()


def test_validate_h2_pipeline_smoke(tmp_path: Path) -> None:
    pytest.importorskip("pyscf")
    project = Path(__file__).resolve().parents[1]
    validate_h2 = load_script(project / "scripts" / "validate_h2_pipeline.py")
    output_path = tmp_path / "h2_validation_summary.json"

    validate_h2.main(output_path=output_path)

    assert output_path.exists()
    summary = json.loads(output_path.read_text(encoding="utf-8"))
    assert summary["n_spin_orbitals"] == 4
    assert summary["n_electrons"] == 2
    assert summary["fixed_particle_sector_dimension"] == 6
    assert summary["basis_size"] == 6
    assert summary["nuclear_repulsion_hartree"] > 0.0
    assert "fci_electronic" in summary["energies_hartree"]
    assert "fci_total" in summary["energies_hartree"]
    assert "diag_manybody_electronic" in summary["energies_hartree"]
    assert "diag_manybody_total" in summary["energies_hartree"]
    assert abs(summary["gaps_hartree"]["diag_manybody_total_minus_fci_total"]) < 1e-4
