import pytest

pytest.importorskip("pyscf")
pytest.importorskip("scipy")

from quantum_ald import H2, run_hartree_fock, run_fci
from quantum_ald.hamiltonian_mapping import build_many_body_hamiltonian
from quantum_ald.vqe_solver import FallbackVQESolver


def test_fallback_vqe_h2() -> None:
    mol = H2()
    mf, hf_e = run_hartree_fock(mol)
    _fci_solver, fci_total = run_fci(mol, mf)
    nuclear_repulsion = float(mf.mol.energy_nuc())

    active_space = {"num_electrons": 2, "num_spatial_orbitals": 2}
    H, basis = build_many_body_hamiltonian(mf, active_space)
    solver = FallbackVQESolver(max_iter=50)
    vqe_electronic, params = solver.solve(H)
    vqe_total = vqe_electronic + nuclear_repulsion

    # Energy should be at least as low as HF and close to FCI (within 1e-5)
    assert len(basis) == 6
    assert vqe_total <= hf_e + 1e-6
    assert abs(vqe_total - fci_total) < 1e-4
