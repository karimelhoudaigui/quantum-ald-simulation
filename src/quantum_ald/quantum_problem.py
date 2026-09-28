"""Generic runtime representation of a mapped electronic problem."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Any

from .active_space import ActiveSpaceConfig, PreparedElectronicProblem
from .electronic_structure import SPIN_ORBITAL_ORDER, spin_orbital_index
from .hamiltonian_mapping import (
    get_fermion_hamiltonian_from_problem,
    map_fermion_hamiltonian,
)
from .vqe_solver import openfermion_qubit_operator_to_sparse_pauli

SUPPORTED_QUANTUM_PROBLEM_MAPPINGS = ("jordan-wigner",)


def _hartree_fock_reference_occupation(
    problem: PreparedElectronicProblem,
) -> tuple[int, ...]:
    """Return the spin-adapted Aufbau determinant in the active register."""
    n_electrons = problem.n_active_electrons
    spin = problem.spin
    if abs(spin) > n_electrons or (n_electrons + spin) % 2:
        raise ValueError("active electrons and molecular spin are incompatible")

    n_alpha = (n_electrons + spin) // 2
    n_beta = n_electrons - n_alpha
    if max(n_alpha, n_beta) > problem.n_active_orbitals:
        raise ValueError("active space cannot represent the requested spin occupation")

    occupied = [spin_orbital_index(index, 0) for index in range(n_alpha)]
    occupied.extend(spin_orbital_index(index, 1) for index in range(n_beta))
    return tuple(sorted(occupied))


def _molecular_hf_active_occupation(
    problem: PreparedElectronicProblem,
) -> tuple[int, ...] | None:
    """Project the molecular HF occupation when the chosen CAS can represent it."""
    n_alpha = (problem.total_electrons + problem.spin) // 2
    n_beta = problem.total_electrons - n_alpha
    if (problem.total_electrons + problem.spin) % 2:
        return None
    if any(index >= n_alpha or index >= n_beta for index in problem.frozen_core_orbital_indices):
        return None
    if any(index < n_alpha or index < n_beta for index in problem.external_orbital_indices):
        return None

    occupied = []
    for active_index, molecular_index in enumerate(problem.active_orbital_indices):
        if molecular_index < n_alpha:
            occupied.append(spin_orbital_index(active_index, 0))
        if molecular_index < n_beta:
            occupied.append(spin_orbital_index(active_index, 1))
    if len(occupied) != problem.n_active_electrons:
        return None
    return tuple(sorted(occupied))


@dataclass(frozen=True)
class PreparedQuantumProblem:
    """Mapped active Hamiltonian and solver-independent quantum metadata.

    ``hamiltonian`` is the operator-valued active Hamiltonian. Molecular total
    energies are obtained through ``total_energy``; ``constant_energy`` is not
    embedded in the Pauli identity term.
    """

    electronic_problem: PreparedElectronicProblem
    fermion_hamiltonian: Any
    hamiltonian: Any
    mapping: str
    reference_occupation: tuple[int, ...]
    reference_bitstring: int
    reference_matches_molecular_hf: bool
    num_fermionic_terms: int
    num_pauli_terms: int

    def __post_init__(self) -> None:
        if self.mapping not in SUPPORTED_QUANTUM_PROBLEM_MAPPINGS:
            raise ValueError(f"unsupported prepared-quantum-problem mapping: {self.mapping}")
        if tuple(sorted(set(self.reference_occupation))) != self.reference_occupation:
            raise ValueError("reference_occupation must be sorted and contain no duplicates")
        if len(self.reference_occupation) != self.num_particles:
            raise ValueError("reference occupation does not match num_particles")
        if any(index < 0 or index >= self.num_qubits for index in self.reference_occupation):
            raise ValueError("reference occupation is outside the qubit register")
        expected_bitstring = sum(1 << index for index in self.reference_occupation)
        if self.reference_bitstring != expected_bitstring:
            raise ValueError("reference_bitstring is inconsistent with reference_occupation")
        if int(self.hamiltonian.num_qubits) != self.num_qubits:
            raise ValueError("SparsePauliOp qubit count does not match the electronic problem")
        if self.num_fermionic_terms != len(self.fermion_hamiltonian.terms):
            raise ValueError("num_fermionic_terms is inconsistent")
        if self.num_pauli_terms != int(self.hamiltonian.size):
            raise ValueError("num_pauli_terms is inconsistent")

    @property
    def num_qubits(self) -> int:
        return self.electronic_problem.n_spin_orbitals

    @property
    def num_particles(self) -> int:
        return self.electronic_problem.n_active_electrons

    @property
    def num_alpha_particles(self) -> int:
        particle_spin_sum = self.num_particles + self.electronic_problem.spin
        if particle_spin_sum % 2:
            raise ValueError("active particle count and spin are incompatible")
        return particle_spin_sum // 2

    @property
    def num_beta_particles(self) -> int:
        return self.num_particles - self.num_alpha_particles

    @property
    def num_particles_by_spin(self) -> tuple[int, int]:
        return self.num_alpha_particles, self.num_beta_particles

    @property
    def constant_energy(self) -> float:
        return self.electronic_problem.constant_energy

    @property
    def full_fock_dimension(self) -> int:
        return 2**self.num_qubits

    @property
    def physical_sector_dimension(self) -> int:
        return comb(self.num_qubits, self.num_particles)

    @property
    def active_space(self) -> ActiveSpaceConfig:
        orbital_indices = (
            self.electronic_problem.active_orbital_indices
            if self.electronic_problem.selection_mode == "manual"
            else None
        )
        return ActiveSpaceConfig(
            n_active_electrons=self.electronic_problem.n_active_electrons,
            n_active_orbitals=self.electronic_problem.n_active_orbitals,
            orbital_indices=orbital_indices,
            selection_mode=self.electronic_problem.selection_mode,
        )

    @property
    def reference_state_kind(self) -> str:
        if self.reference_matches_molecular_hf:
            return "molecular_hartree_fock"
        return "active_space_aufbau"

    def total_energy(self, active_energy: float) -> float:
        return self.electronic_problem.total_energy(active_energy)

    def to_metadata(self) -> dict[str, Any]:
        active_space = self.active_space.to_dict()
        active_space.update(
            {
                "resolved_orbital_indices": list(self.electronic_problem.active_orbital_indices),
                "frozen_core_orbital_indices": list(
                    self.electronic_problem.frozen_core_orbital_indices
                ),
                "external_orbital_indices": list(self.electronic_problem.external_orbital_indices),
            }
        )
        return {
            "molecule": self.electronic_problem.molecule_name,
            "basis": self.electronic_problem.basis,
            "charge": self.electronic_problem.charge,
            "spin": self.electronic_problem.spin,
            "mapping": self.mapping,
            "spin_orbital_order": SPIN_ORBITAL_ORDER,
            "num_qubits": self.num_qubits,
            "num_particles": self.num_particles,
            "num_alpha_particles": self.num_alpha_particles,
            "num_beta_particles": self.num_beta_particles,
            "num_fermionic_terms": self.num_fermionic_terms,
            "num_pauli_terms": self.num_pauli_terms,
            "full_fock_dimension": self.full_fock_dimension,
            "physical_sector_dimension": self.physical_sector_dimension,
            "constant_energy": self.constant_energy,
            "constant_energy_source": self.electronic_problem.constant_energy_source,
            "constant_embedded_in_hamiltonian": False,
            "reference_occupation": list(self.reference_occupation),
            "reference_bitstring": self.reference_bitstring,
            "reference_state_kind": self.reference_state_kind,
            "reference_matches_molecular_hf": self.reference_matches_molecular_hf,
            "active_space": active_space,
        }


def prepare_quantum_problem(
    electronic_problem: PreparedElectronicProblem,
    mapping: str = "jordan-wigner",
) -> PreparedQuantumProblem:
    """Map a prepared electronic problem without re-entering PySCF."""
    if not isinstance(electronic_problem, PreparedElectronicProblem):
        raise TypeError("electronic_problem must be a PreparedElectronicProblem")
    if mapping not in SUPPORTED_QUANTUM_PROBLEM_MAPPINGS:
        supported = ", ".join(SUPPORTED_QUANTUM_PROBLEM_MAPPINGS)
        raise ValueError(f"unsupported mapping: {mapping}; supported: {supported}")

    fermion_hamiltonian = get_fermion_hamiltonian_from_problem(electronic_problem)
    qubit_operator = map_fermion_hamiltonian(fermion_hamiltonian, mapping=mapping)
    hamiltonian = openfermion_qubit_operator_to_sparse_pauli(
        qubit_operator,
        electronic_problem.n_spin_orbitals,
    )
    molecular_hf_occupation = _molecular_hf_active_occupation(electronic_problem)
    reference_matches_molecular_hf = molecular_hf_occupation is not None
    reference_occupation = (
        molecular_hf_occupation
        if molecular_hf_occupation is not None
        else _hartree_fock_reference_occupation(electronic_problem)
    )
    reference_bitstring = sum(1 << index for index in reference_occupation)
    return PreparedQuantumProblem(
        electronic_problem=electronic_problem,
        fermion_hamiltonian=fermion_hamiltonian,
        hamiltonian=hamiltonian,
        mapping=mapping,
        reference_occupation=reference_occupation,
        reference_bitstring=reference_bitstring,
        reference_matches_molecular_hf=reference_matches_molecular_hf,
        num_fermionic_terms=len(fermion_hamiltonian.terms),
        num_pauli_terms=len(qubit_operator.terms),
    )
