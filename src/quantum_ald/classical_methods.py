"""Classical electronic-structure methods used before quantum simulation."""

from __future__ import annotations

from typing import Any

import numpy as np

from ._optional import require_module
from .molecule_loader import Molecule


def run_hartree_fock(molecule: Molecule) -> tuple[Any, float]:
    """Run restricted Hartree-Fock for a closed-shell molecule."""
    scf = require_module("pyscf.scf", "chemistry")
    mf = scf.RHF(molecule.mol)
    energy = float(mf.kernel())
    molecule.mf = mf
    molecule.hf_result = energy
    return mf, energy


def run_dft(molecule: Molecule, functional: str = "lda") -> tuple[Any, float]:
    """Run restricted Kohn-Sham DFT."""
    dft = require_module("pyscf.dft", "chemistry")
    mf = dft.RKS(molecule.mol)
    mf.xc = functional
    energy = float(mf.kernel())
    return mf, energy


def run_casscf(
    molecule: Molecule, mf: Any, n_electrons: int, n_orbitals: int
) -> tuple[Any, float]:
    """Run a compact CASSCF calculation from a mean-field reference."""
    del molecule
    mcscf = require_module("pyscf.mcscf", "chemistry")
    mc = mcscf.CASSCF(mf, n_orbitals, n_electrons)
    energy = float(mc.kernel()[0])
    return mc, energy


def run_casci(molecule: Molecule, mf: Any, n_electrons: int, n_orbitals: int) -> tuple[Any, float]:
    """Run a fixed-orbital CASCI calculation from a mean-field reference."""
    del molecule
    mcscf = require_module("pyscf.mcscf", "chemistry")
    mc = mcscf.CASCI(mf, n_orbitals, n_electrons)
    energy = float(mc.kernel()[0])
    return mc, energy


def get_orbital_energies(mf: Any) -> np.ndarray:
    """Return molecular orbital energies."""
    return np.asarray(mf.mo_energy)


def get_density_matrix(mf: Any) -> np.ndarray:
    """Return the one-particle density matrix."""
    return np.asarray(mf.make_rdm1())


def get_fock_matrix(mf: Any) -> np.ndarray:
    """Return the Fock matrix."""
    return np.asarray(mf.get_fock())


def run_fci(molecule: Molecule, mf: Any) -> tuple[Any, float]:
    """Run a full configuration interaction (FCI) calculation for small systems.

    Returns the FCI solver object and the FCI energy in Hartree.
    This uses pyscf.fci which is suitable for very small molecules used
    in unit tests (H2, LiH minimal basis).
    """
    fci = require_module("pyscf.fci", "chemistry")
    cisolver = fci.FCI(molecule.mol, mf.mo_coeff)
    e, _ = cisolver.kernel()
    energy = float(e)
    return cisolver, energy
