import pytest

pytest.importorskip("pyscf")

from quantum_ald import H2, LiH, molecule_from_string


def test_h2() -> None:
    molecule = H2()
    assert molecule.num_atoms == 2
    assert molecule.num_electrons == 2


def test_lih() -> None:
    molecule = LiH()
    assert molecule.num_atoms == 2
    assert molecule.num_electrons == 4


def test_molecule_from_string() -> None:
    molecule = molecule_from_string("H 0 0 0\nH 0 0 1.0", name="test_h2")
    assert molecule.name == "test_h2"
    assert molecule.num_electrons == 2
