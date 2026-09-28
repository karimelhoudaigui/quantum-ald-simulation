"""Active-space definitions for quantum chemistry reductions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import comb
from typing import Any

import numpy as np

from ._optional import require_module


@dataclass(frozen=True)
class ActiveSpaceConfig:
    """Serializable user configuration for a complete active space."""

    n_active_electrons: int
    n_active_orbitals: int
    orbital_indices: tuple[int, ...] | None = None
    selection_mode: str = "canonical"

    def __post_init__(self) -> None:
        if self.n_active_electrons <= 0:
            raise ValueError("n_active_electrons must be positive")
        if self.n_active_orbitals <= 0:
            raise ValueError("n_active_orbitals must be positive")
        if self.n_active_electrons > 2 * self.n_active_orbitals:
            raise ValueError("active space has fewer spin orbitals than active electrons")
        if self.selection_mode not in {"canonical", "manual"}:
            raise ValueError("selection_mode must be 'canonical' or 'manual'")
        if self.selection_mode == "canonical" and self.orbital_indices is not None:
            raise ValueError("canonical selection determines orbital_indices automatically")
        if self.selection_mode == "manual" and self.orbital_indices is None:
            raise ValueError("manual selection requires orbital_indices")
        if self.orbital_indices is not None:
            if len(self.orbital_indices) != self.n_active_orbitals:
                raise ValueError("orbital_indices length must equal n_active_orbitals")
            if len(set(self.orbital_indices)) != len(self.orbital_indices):
                raise ValueError("orbital_indices must not contain duplicates")
            if any(index < 0 for index in self.orbital_indices):
                raise ValueError("orbital_indices must be non-negative")

    def validate_for_system(self, total_electrons: int, total_orbitals: int) -> None:
        if self.n_active_electrons > total_electrons:
            raise ValueError("active electrons exceed the molecule electron count")
        if self.n_active_orbitals > total_orbitals:
            raise ValueError("active orbitals exceed the molecular orbital count")
        if (total_electrons - self.n_active_electrons) % 2:
            raise ValueError("RHF frozen-core partition requires an even inactive electron count")
        n_core = (total_electrons - self.n_active_electrons) // 2
        if n_core + self.n_active_orbitals > total_orbitals:
            raise ValueError("core and active orbitals exceed the molecular orbital count")
        if self.orbital_indices is not None and any(
            index >= total_orbitals for index in self.orbital_indices
        ):
            raise ValueError("orbital index is outside the molecular orbital range")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.orbital_indices is not None:
            data["orbital_indices"] = list(self.orbital_indices)
        return data


@dataclass(frozen=True)
class PreparedElectronicProblem:
    """Runtime active Hamiltonian with explicit total-energy accounting.

    Molecular total energies are reconstructed exactly once as
    ``active_energy + constant_energy``. For frozen-core CAS problems the
    PySCF ``ecore`` value already includes nuclear repulsion.
    """

    h1: np.ndarray
    h2: np.ndarray
    n_active_electrons: int
    n_active_orbitals: int
    n_spin_orbitals: int
    active_orbital_indices: tuple[int, ...]
    frozen_core_orbital_indices: tuple[int, ...]
    external_orbital_indices: tuple[int, ...]
    total_electrons: int
    total_orbitals: int
    constant_energy: float
    constant_energy_source: str
    nuclear_repulsion: float
    selection_mode: str
    molecule_name: str
    basis: str
    charge: int
    spin: int

    def __post_init__(self) -> None:
        n = self.n_active_orbitals
        if np.shape(self.h1) != (n, n):
            raise ValueError(f"h1 must have shape {(n, n)}")
        if np.shape(self.h2) != (n, n, n, n):
            raise ValueError(f"h2 must have shape {(n, n, n, n)}")
        if self.n_spin_orbitals != 2 * n:
            raise ValueError("n_spin_orbitals must equal 2 * n_active_orbitals")
        if len(self.active_orbital_indices) != n:
            raise ValueError("active orbital provenance is inconsistent")

    @property
    def cas_dimension(self) -> int:
        return comb(self.n_spin_orbitals, self.n_active_electrons)

    def total_energy(self, active_energy: float) -> float:
        return float(active_energy + self.constant_energy)

    def to_metadata_dict(self) -> dict[str, Any]:
        return {
            "molecule": self.molecule_name,
            "basis": self.basis,
            "n_active_electrons": self.n_active_electrons,
            "n_active_orbitals": self.n_active_orbitals,
            "n_spin_orbitals": self.n_spin_orbitals,
            "num_qubits": self.n_spin_orbitals,
            "cas_dimension": self.cas_dimension,
            "active_orbital_indices": list(self.active_orbital_indices),
            "frozen_core_orbital_indices": list(self.frozen_core_orbital_indices),
            "external_orbital_indices": list(self.external_orbital_indices),
            "total_electrons": self.total_electrons,
            "total_orbitals": self.total_orbitals,
            "constant_energy": self.constant_energy,
            "constant_energy_source": self.constant_energy_source,
            "nuclear_repulsion": self.nuclear_repulsion,
            "selection_mode": self.selection_mode,
            "charge": self.charge,
            "spin": self.spin,
        }


def _active_space_context(
    molecule: Any,
    mf: Any,
    config: ActiveSpaceConfig,
) -> tuple[Any, np.ndarray, tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    total_electrons = int(mf.mol.nelectron)
    total_orbitals = int(np.shape(mf.mo_coeff)[1])
    config.validate_for_system(total_electrons, total_orbitals)
    n_core = (total_electrons - config.n_active_electrons) // 2

    mcscf = require_module("pyscf.mcscf", "chemistry")
    solver = mcscf.CASCI(mf, config.n_active_orbitals, config.n_active_electrons)
    canonical_indices = tuple(range(total_orbitals))
    if config.orbital_indices is None:
        active = tuple(range(n_core, n_core + config.n_active_orbitals))
        mo_coeff = np.asarray(mf.mo_coeff)
    else:
        active = tuple(config.orbital_indices)
        mo_coeff = np.asarray(solver.sort_mo(list(active), mo_coeff=mf.mo_coeff, base=0))

    remaining = tuple(index for index in canonical_indices if index not in active)
    frozen_core = remaining[:n_core]
    external = remaining[n_core:]
    solver.mo_coeff = mo_coeff
    return solver, mo_coeff, active, frozen_core, external


def prepare_active_space_problem(
    molecule: Any,
    mf: Any,
    config: ActiveSpaceConfig,
) -> PreparedElectronicProblem:
    """Prepare effective CAS integrals without embedding a solver result."""
    solver, mo_coeff, active, frozen_core, external = _active_space_context(
        molecule, mf, config
    )
    h1, constant_energy = solver.get_h1eff(mo_coeff=mo_coeff)
    ao2mo = require_module("pyscf.ao2mo", "chemistry")
    h2 = ao2mo.restore(1, solver.get_h2eff(mo_coeff=mo_coeff), config.n_active_orbitals)
    source = "nuclear_repulsion" if not frozen_core else "pyscf_casci_frozen_core_ecore"
    return PreparedElectronicProblem(
        h1=np.asarray(h1),
        h2=np.asarray(h2),
        n_active_electrons=config.n_active_electrons,
        n_active_orbitals=config.n_active_orbitals,
        n_spin_orbitals=2 * config.n_active_orbitals,
        active_orbital_indices=active,
        frozen_core_orbital_indices=frozen_core,
        external_orbital_indices=external,
        total_electrons=int(mf.mol.nelectron),
        total_orbitals=int(np.shape(mf.mo_coeff)[1]),
        constant_energy=float(constant_energy),
        constant_energy_source=source,
        nuclear_repulsion=float(mf.mol.energy_nuc()),
        selection_mode=config.selection_mode,
        molecule_name=molecule.name,
        basis=str(molecule.mol.basis),
        charge=int(mf.mol.charge),
        spin=int(mf.mol.spin),
    )


def run_active_space_casci_reference(
    molecule: Any,
    mf: Any,
    config: ActiveSpaceConfig,
) -> float:
    """Return the independent PySCF CASCI total-energy reference."""
    solver, mo_coeff, _active, _frozen_core, _external = _active_space_context(
        molecule, mf, config
    )
    return float(solver.kernel(mo_coeff)[0])


def define_active_space(n_electrons: int, n_orbitals: int) -> dict[str, int]:
    """Define a complete active space CAS(n_electrons, n_orbitals)."""
    if n_electrons <= 0 or n_orbitals <= 0:
        raise ValueError("active electrons and orbitals must be positive")
    if n_electrons > 2 * n_orbitals:
        raise ValueError("too many electrons for the requested spatial orbitals")
    return {
        "num_electrons": n_electrons,
        "num_spatial_orbitals": n_orbitals,
        "num_qubits_spinorbitals": 2 * n_orbitals,
    }


def simple_active_space(mf: Any, orbital_indices: list[int]) -> tuple[np.ndarray, int]:
    """Select active orbitals manually from a mean-field object."""
    mo_coeff = mf.mo_coeff[:, orbital_indices]
    occupied = set(range(mf.mol.nelectron // 2))
    n_electrons = 2 * sum(index in occupied for index in orbital_indices)
    return np.asarray(mo_coeff), int(n_electrons)


def avas_selection(mf: Any, atomlist: list[str], minao: str = "minao") -> dict[str, Any]:
    """Run PySCF AVAS active-space selection."""
    avas = require_module("pyscf.mcscf.avas", "chemistry")
    ncas, nelecas, mo_coeff = avas.avas(mf, atomlist, minao=minao)
    return {"n_electrons": nelecas, "n_orbitals": ncas, "mo_coeff": mo_coeff}


def CAS_2_2() -> dict[str, int]:
    return define_active_space(2, 2)


def CAS_4_4() -> dict[str, int]:
    return define_active_space(4, 4)


def CAS_6_6() -> dict[str, int]:
    return define_active_space(6, 6)


def CAS_8_8() -> dict[str, int]:
    return define_active_space(8, 8)
