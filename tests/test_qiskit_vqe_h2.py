import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def test_h2_qiskit_vqe_smoke(tmp_path: Path) -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("qiskit")

    project = Path(__file__).resolve().parents[1]
    script = load_script(project / "scripts" / "run_h2_qiskit_vqe.py")

    result = script.run_workflow(max_iter=25, output_root=tmp_path)

    assert (tmp_path / "tables" / "h2_qiskit_vqe_results.json").exists()
    assert (tmp_path / "figures" / "h2_qiskit_vqe_convergence.png").exists()
    assert math.isfinite(result["qiskit_vqe_total_hartree"])
    assert math.isfinite(result["qiskit_vqe_minus_hf_hartree"])
    assert math.isfinite(result["qiskit_vqe_minus_fci_hartree"])
    assert isinstance(result["below_hf"], bool)
    assert isinstance(result["near_fci"], bool)
    assert result["status"] in {"FCI_CLOSE", "REFERENCE_ONLY", "CHECK"}
    assert result["iterations"] > 0


def test_h2_pair_ansatz_optimizes_pair_subspace() -> None:
    pytest.importorskip("qiskit")

    from quantum_ald import QiskitVQESolver, dense_matrix_to_sparse_pauli

    matrix = 2.0 * np.eye(16)
    matrix[3, 3] = -1.0
    matrix[12, 12] = -0.8
    matrix[3, 12] = matrix[12, 3] = -0.15
    expected = float(np.min(np.linalg.eigvalsh(matrix[np.ix_([3, 12], [3, 12])])))

    solver = QiskitVQESolver(num_qubits=4, max_iter=80, ansatz_type="h2_pair")
    energy, parameters = solver.solve(dense_matrix_to_sparse_pauli(matrix))

    assert math.isfinite(energy)
    assert parameters.shape == (1,)
    assert abs(energy - expected) < 1e-6
