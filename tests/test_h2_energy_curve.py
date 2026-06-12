import importlib.util
import json
from pathlib import Path

import pytest


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def test_h2_energy_curve_smoke(tmp_path: Path) -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("matplotlib")
    project = Path(__file__).resolve().parents[1]
    script = load_script(project / "scripts" / "run_h2_energy_curve.py")

    rows, paths = script.run_curve(distances=[0.7, 0.735], output_root=tmp_path)

    assert len(rows) == 2
    assert paths["csv"].exists()
    assert paths["json"].exists()
    assert paths["figure"].exists()

    saved_rows = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert len(saved_rows) == 2
    for row in saved_rows:
        assert row["sector_dimension"] == 6
        assert abs(row["diag_minus_fci_hartree"]) < 1e-4
