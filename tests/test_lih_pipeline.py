import importlib.util
import json
from pathlib import Path

import pytest


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def test_lih_pipeline_smoke(tmp_path: Path) -> None:
    pytest.importorskip("pyscf")
    project = Path(__file__).resolve().parents[1]
    script = load_script(project / "scripts" / "validate_lih_pipeline.py")
    output_path = tmp_path / "lih_validation_summary.json"

    summary = script.run_validation(
        output_path=output_path,
        fci_dimension_limit=0,
        local_diagonalization_limit=0,
    )

    assert output_path.exists()
    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["molecule"] == "lih"
    assert saved["n_electrons"] == 4
    assert saved["n_spin_orbitals"] >= 4
    assert saved["full_fixed_particle_sector_dimension"] > 0
    assert saved["fci_status"].startswith("skipped")
    assert saved["local_full_space"]["status"] == "skipped"
    assert saved["casci_active_space"]["basis_size"] == 6
    assert "core_energy_shift_hartree" in saved["casci_active_space"]
    assert abs(saved["casci_active_space"]["local_minus_pyscf_casci_hartree"]) < 1e-4
    assert summary["validated_reduced_active_space"] is True
