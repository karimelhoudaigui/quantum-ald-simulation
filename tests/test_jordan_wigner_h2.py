import pytest


def test_validate_jordan_wigner_h2_matches_fci() -> None:
    pytest.importorskip("pyscf")

    from quantum_ald.qubit_mapping_validation import validate_jordan_wigner_h2

    result = validate_jordan_wigner_h2()

    assert result["n_spin_orbitals"] == 4
    assert result["n_qubits"] == 4
    assert result["n_electrons"] == 2
    assert result["fixed_particle_sector_dimension"] == 6
    assert result["mapping_backend"] in {
        "local_dense_jordan_wigner",
        "openfermion_jordan_wigner",
    }
    assert abs(result["jw_total_minus_fci_total_hartree"]) < 1e-4
    assert result["status"] == "PASS"
