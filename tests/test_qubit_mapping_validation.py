from math import comb

import numpy as np
import pytest


def test_jordan_wigner_preserves_h2_fixed_particle_spectrum() -> None:
    pytest.importorskip("pyscf")
    openfermion = pytest.importorskip("openfermion")

    from quantum_ald import H2, map_to_qubit_hamiltonian, run_fci, run_hartree_fock
    from quantum_ald.hamiltonian_mapping import build_many_body_hamiltonian

    molecule = H2()
    mf, _hf_total = run_hartree_fock(molecule)
    _fci_solver, fci_total = run_fci(molecule, mf)
    nuclear_repulsion = float(mf.mol.energy_nuc())
    fci_electronic = fci_total - nuclear_repulsion

    active_space = {"num_electrons": 2, "num_spatial_orbitals": 2}
    local_hamiltonian, basis = build_many_body_hamiltonian(mf, active_space)
    qubit_hamiltonian = map_to_qubit_hamiltonian(
        mf,
        active_space,
        mapping="jordan-wigner",
    )
    sparse_qubit = openfermion.utils.get_sparse_operator(  # type: ignore[attr-defined]
        qubit_hamiltonian,
        n_qubits=2 * active_space["num_spatial_orbitals"],
    )

    rows = np.asarray(basis, dtype=int)
    fixed_particle_block = sparse_qubit[rows[:, None], rows].toarray()

    assert np.allclose(fixed_particle_block, fixed_particle_block.conj().T, atol=1e-10)

    local_eigenvalues = np.linalg.eigvalsh(local_hamiltonian)
    qubit_eigenvalues = np.linalg.eigvalsh(fixed_particle_block)
    local_ground = float(np.min(local_eigenvalues))
    qubit_ground = float(np.min(qubit_eigenvalues))

    n_spin_orbitals = 2 * active_space["num_spatial_orbitals"]
    sector_dimension = comb(n_spin_orbitals, active_space["num_electrons"])

    # Diagnostic values for this validation:
    # n_spin_orbitals = 4
    # n_electrons = 2
    # fixed-particle sector dimension = C(4,2) = 6
    # PySCF FCI electronic energy is compared to the fixed-sector JW block.
    assert n_spin_orbitals == 4
    assert sector_dimension == 6
    assert len(basis) == sector_dimension
    assert abs(local_ground - fci_electronic) < 1e-4
    assert abs(qubit_ground - local_ground) < 1e-6
