"""Molecular structure loading utilities for ALD quantum-chemistry workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._optional import require_module


@dataclass
class Molecule:
    """Small wrapper around a PySCF molecule with metadata helpers."""

    mol: Any
    name: str = "molecule"
    hf_result: float | None = None
    mf: Any | None = None

    @property
    def num_atoms(self) -> int:
        return int(self.mol.natm)

    @property
    def num_electrons(self) -> int:
        return int(self.mol.nelectron)

    @property
    def charge(self) -> int:
        return int(self.mol.charge)

    @property
    def spin(self) -> int:
        return int(self.mol.spin)

    def __repr__(self) -> str:
        return f"Molecule(name={self.name}, atoms={self.num_atoms}, electrons={self.num_electrons})"


def _build_pyscf_molecule(xyz_string: str, basis: str, charge: int, spin: int) -> Any:
    gto = require_module("pyscf.gto", "chemistry")
    mol = gto.Mole()
    mol.atom = xyz_string
    mol.basis = basis
    mol.charge = charge
    mol.spin = spin
    mol.build()
    return mol


def _read_xyz_atoms(xyz_text: str) -> str:
    """Accept either raw atom lines or full XYZ files with header/comment."""
    lines = [line.strip() for line in xyz_text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("empty XYZ content")
    if lines[0].isdigit():
        atom_count = int(lines[0])
        atom_lines = lines[2 : 2 + atom_count]
        if len(atom_lines) != atom_count:
            raise ValueError("XYZ file does not contain the declared number of atoms")
        return "\n".join(atom_lines)
    return "\n".join(lines)


def load_molecule(xyz_file: str | Path, basis: str = "sto-3g", charge: int = 0, spin: int = 0) -> Molecule:
    """Load a molecule from an XYZ file."""
    path = Path(xyz_file)
    if not path.exists():
        raise FileNotFoundError(f"XYZ file not found: {path}")
    xyz_string = _read_xyz_atoms(path.read_text(encoding="utf-8"))
    mol = _build_pyscf_molecule(xyz_string, basis=basis, charge=charge, spin=spin)
    return Molecule(mol=mol, name=path.stem)


def molecule_from_string(
    xyz_string: str,
    basis: str = "sto-3g",
    charge: int = 0,
    spin: int = 0,
    name: str = "mol",
) -> Molecule:
    """Create a molecule from an atom-coordinate string or XYZ-formatted string."""
    atoms = _read_xyz_atoms(xyz_string)
    mol = _build_pyscf_molecule(atoms, basis=basis, charge=charge, spin=spin)
    return Molecule(mol=mol, name=name)


def get_molecular_data(molecule: Molecule) -> dict[str, Any]:
    """Return serializable metadata for a molecule."""
    return {
        "name": molecule.name,
        "num_atoms": molecule.num_atoms,
        "num_electrons": molecule.num_electrons,
        "charge": molecule.charge,
        "spin": molecule.spin,
        "basis": molecule.mol.basis,
        "atom_coords": molecule.mol.atom_coords().tolist(),
        "atom_symbols": [molecule.mol.atom_symbol(i) for i in range(molecule.num_atoms)],
    }


def H2() -> Molecule:
    """Return the H2 reference molecule."""
    return molecule_from_string("H 0 0 0\nH 0 0 0.74", basis="sto-3g", name="H2")


def LiH() -> Molecule:
    """Return the LiH reference molecule."""
    return molecule_from_string("Li 0 0 0\nH 0 0 1.64", basis="sto-3g", name="LiH")


def H2O() -> Molecule:
    """Return the H2O reference molecule."""
    return molecule_from_string(
        "O 0.000000 0.000000 0.118720\n"
        "H 0.000000 0.755453 -0.474880\n"
        "H 0.000000 -0.755453 -0.474880",
        basis="sto-3g",
        name="H2O",
    )
