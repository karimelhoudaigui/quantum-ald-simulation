import pytest

import numpy as np

from quantum_ald import H2, run_hartree_fock, run_fci
from quantum_ald.hamiltonian_mapping import (
    _count_occupied_orbitals,
    build_many_body_hamiltonian,
    get_fermion_hamiltonian,
    restrict_to_particle_number,
)


def diag_eigenvalues(H: np.ndarray) -> np.ndarray:
    evals = np.linalg.eigvalsh(H)
    return np.sort(np.real(evals))


def test_manybody_diagonalization_matches_fci():
    """Compare local fixed-N diagonalization with PySCF FCI total energy."""
    pytest.importorskip("pyscf")
    mol = H2()
    mf, hf_e = run_hartree_fock(mol)
    _fci_solver, fci_total = run_fci(mol, mf)
    nuclear_repulsion = float(mf.mol.energy_nuc())
    fci_electronic = fci_total - nuclear_repulsion

    active_space = {"num_electrons": 2, "num_spatial_orbitals": 2}
    H, basis = build_many_body_hamiltonian(mf, active_space)

    evals = diag_eigenvalues(H)
    local_electronic = float(evals[0])
    local_total = local_electronic + nuclear_repulsion

    assert len(basis) == 6
    assert 2 * active_space["num_spatial_orbitals"] == 4
    assert active_space["num_electrons"] == 2
    assert hf_e > fci_total
    assert abs(local_electronic - fci_electronic) < 1e-4
    assert abs(local_total - fci_total) < 1e-4


def test_restrict_to_particle_number_dimension():
    H_full = np.eye(16)
    H_sector, basis = restrict_to_particle_number(H_full, n_spin_orbitals=4, n_electrons=2)

    assert H_sector.shape == (6, 6)
    assert len(basis) == 6
    assert all(_count_occupied_orbitals(state) == 2 for state in basis)


def test_openfermion_consistency_if_available():
    """Optional test: compare eigenvalues of our many-body matrix with the
    block of the OpenFermion sparse operator restricted to the same particle
    number. Skipped if OpenFermion is not installed.
    """
    pytest.importorskip("pyscf")
    pytest.importorskip("openfermion")
    import openfermion as of
    from scipy.sparse import csc_matrix

    mol = H2()
    mf, _ = run_hartree_fock(mol)
    active_space = {"num_electrons": 2, "num_spatial_orbitals": 2}

    H_local, basis = build_many_body_hamiltonian(mf, active_space)
    ferm_op = get_fermion_hamiltonian(mf, active_space)
    sparse = of.utils.get_sparse_operator(  # type: ignore[attr-defined]
        ferm_op,
        n_qubits=2 * active_space["num_spatial_orbitals"],
    )

    sparse = csc_matrix(sparse)
    rows = np.array(basis, dtype=int)
    sub = sparse[rows[:, None], rows].toarray()

    evals_of = diag_eigenvalues(sub)
    evals_local = diag_eigenvalues(H_local)

    assert np.allclose(evals_of, evals_local, atol=1e-6)


def test_jordan_wigner_spectrum_if_available():
    """Optional: check that mapping to qubits via our map_to_qubit_hamiltonian
    followed by OpenFermion sparse operator preserves the spectrum.
    """
    try:
        pytest.importorskip("pyscf")
        pytest.importorskip("openfermion")
    except Exception:
        pytest.skip("OpenFermion not available")

    from quantum_ald import map_to_qubit_hamiltonian
    import openfermion as of

    mol = H2()
    mf, _ = run_hartree_fock(mol)
    active_space = {"num_electrons": 2, "num_spatial_orbitals": 2}

    q_op = map_to_qubit_hamiltonian(mf, active_space, mapping="jordan-wigner")

    sparse_q = of.utils.get_sparse_operator(  # type: ignore[attr-defined]
        q_op,
        n_qubits=2 * active_space["num_spatial_orbitals"],
    )

    H_local, basis = build_many_body_hamiltonian(mf, active_space)
    rows = np.array(basis, dtype=int)
    sub = sparse_q[rows[:, None], rows].toarray()
    evals_q = diag_eigenvalues(sub)
    evals_local = diag_eigenvalues(H_local)

    assert np.allclose(evals_q, evals_local, atol=1e-6)
