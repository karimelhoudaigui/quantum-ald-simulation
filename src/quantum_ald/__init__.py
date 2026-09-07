"""Hybrid quantum-classical workflow for Atomic Layer Deposition reactions."""

from .active_space import CAS_2_2, CAS_4_4, CAS_6_6, CAS_8_8, avas_selection, define_active_space
from .ald_models import ALDProxyModel, get_ald_proxy_model, list_ald_proxy_models
from .classical_methods import (
    get_density_matrix,
    get_fock_matrix,
    get_orbital_energies,
    run_casscf,
    run_casci,
    run_dft,
    run_hartree_fock,
    run_fci,
)
from .error_mitigation import CDR, ZNE
from .hamiltonian_mapping import (
    build_many_body_hamiltonian,
    build_many_body_hamiltonian_from_integrals,
    get_fermion_hamiltonian,
    map_to_qubit_hamiltonian,
    particle_number_basis,
    restrict_to_particle_number,
)
from .molecule_loader import H2, H2O, LiH, Molecule, get_molecular_data, load_molecule, molecule_from_string
from .noise_models import DepolarizingNoiseProfile, NoiseModel, carbon_nanotube_noise, simple_noise_model
from .plotting import plot_comparison, plot_energy_profile, plot_vqe_convergence
from .vqe_solver import (
    QiskitVQESolver,
    VQESolver,
    dense_matrix_to_sparse_pauli,
    openfermion_qubit_operator_to_sparse_pauli,
)

__version__ = "0.1.0"
__author__ = "Karim El Houdaigui"

__all__ = [
    "CAS_2_2",
    "CAS_4_4",
    "CAS_6_6",
    "CAS_8_8",
    "ALDProxyModel",
    "CDR",
    "H2",
    "H2O",
    "LiH",
    "Molecule",
    "DepolarizingNoiseProfile",
    "NoiseModel",
    "QiskitVQESolver",
    "VQESolver",
    "ZNE",
    "avas_selection",
    "carbon_nanotube_noise",
    "define_active_space",
    "dense_matrix_to_sparse_pauli",
    "build_many_body_hamiltonian",
    "build_many_body_hamiltonian_from_integrals",
    "get_density_matrix",
    "get_ald_proxy_model",
    "get_fermion_hamiltonian",
    "get_fock_matrix",
    "get_molecular_data",
    "get_orbital_energies",
    "load_molecule",
    "list_ald_proxy_models",
    "map_to_qubit_hamiltonian",
    "molecule_from_string",
    "openfermion_qubit_operator_to_sparse_pauli",
    "particle_number_basis",
    "plot_comparison",
    "plot_energy_profile",
    "plot_vqe_convergence",
    "restrict_to_particle_number",
    "run_casscf",
    "run_casci",
    "run_dft",
    "run_hartree_fock",
    "run_fci",
    "simple_noise_model",
]
