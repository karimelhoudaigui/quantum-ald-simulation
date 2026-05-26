from quantum_ald import CAS_2_2, CAS_4_4, define_active_space


def test_cas_2_2() -> None:
    cas = CAS_2_2()
    assert cas["num_electrons"] == 2
    assert cas["num_spatial_orbitals"] == 2
    assert cas["num_qubits_spinorbitals"] == 4


def test_cas_4_4() -> None:
    cas = CAS_4_4()
    assert cas["num_electrons"] == 4
    assert cas["num_spatial_orbitals"] == 4
    assert cas["num_qubits_spinorbitals"] == 8


def test_define_active_space() -> None:
    cas = define_active_space(6, 6)
    assert cas["num_electrons"] == 6
    assert cas["num_spatial_orbitals"] == 6
