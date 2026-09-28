"""Configurable active-space sweeps built from the generic chemistry pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from time import perf_counter
from typing import Any, Callable

from .active_space import (
    ActiveSpaceConfig,
    prepare_active_space_problem,
    run_active_space_casci_reference,
)
from .ansatz import AnsatzConfig, prepare_ansatz
from .classical_methods import run_fci, run_hartree_fock
from .generic_vqe import VQESolverConfig, run_vqe
from .molecule_loader import Molecule, get_molecular_data
from .quantum_problem import prepare_quantum_problem

CHEMICAL_ACCURACY_HARTREE = 1.6e-3
VARIATIONAL_TOLERANCE_HARTREE = 1e-8
DECOMPOSITION_TOLERANCE_HARTREE = 1e-12
SUPPORTED_SWEEP_MAPPINGS = ("jordan-wigner",)
ProgressCallback = Callable[[dict[str, Any]], None]


def _emit_progress(
    callback: ProgressCallback | None,
    phase: str,
    status: str,
    progress: int,
    **details: Any,
) -> None:
    if callback is None:
        return
    try:
        callback(
            {
                "phase": phase,
                "status": status,
                "progress": progress,
                **details,
            }
        )
    except Exception:
        # Observability must never alter a scientific execution.
        return


@dataclass(frozen=True)
class ActiveSpaceSweepConfig:
    """Serializable user configuration for an active-space comparison."""

    active_spaces: tuple[ActiveSpaceConfig, ...]
    ansatz: AnsatzConfig
    solver: VQESolverConfig
    run_hf: bool = True
    run_casci: bool = True
    run_fci_reference: bool = True
    mapping: str = "jordan-wigner"
    chemical_accuracy_hartree: float = CHEMICAL_ACCURACY_HARTREE

    def __post_init__(self) -> None:
        active_spaces = tuple(self.active_spaces)
        mapping = self.mapping.strip().lower()
        object.__setattr__(self, "active_spaces", active_spaces)
        object.__setattr__(self, "mapping", mapping)
        if not active_spaces:
            raise ValueError("active_spaces must contain at least one configuration")
        if any(not isinstance(item, ActiveSpaceConfig) for item in active_spaces):
            raise TypeError("active_spaces must contain ActiveSpaceConfig values")
        serialized_spaces = [
            json.dumps(item.to_dict(), sort_keys=True, separators=(",", ":"))
            for item in active_spaces
        ]
        if len(set(serialized_spaces)) != len(serialized_spaces):
            raise ValueError("active_spaces must not contain duplicate configurations")
        if not isinstance(self.ansatz, AnsatzConfig):
            raise TypeError("ansatz must be an AnsatzConfig")
        if not isinstance(self.solver, VQESolverConfig):
            raise TypeError("solver must be a VQESolverConfig")
        for name in ("run_hf", "run_casci", "run_fci_reference"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")
        if not self.run_casci:
            raise ValueError("run_casci must be true because CASCI is the solver reference")
        if mapping not in SUPPORTED_SWEEP_MAPPINGS:
            supported = ", ".join(SUPPORTED_SWEEP_MAPPINGS)
            raise ValueError(f"unsupported mapping: {mapping}; supported: {supported}")
        accuracy = float(self.chemical_accuracy_hartree)
        if not (accuracy > 0.0):
            raise ValueError("chemical_accuracy_hartree must be positive")
        object.__setattr__(self, "chemical_accuracy_hartree", accuracy)

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_spaces": [item.to_dict() for item in self.active_spaces],
            "ansatz": self.ansatz.to_dict(),
            "solver": self.solver.to_dict(),
            "run_hf": self.run_hf,
            "run_casci": self.run_casci,
            "run_fci_reference": self.run_fci_reference,
            "mapping": self.mapping,
            "chemical_accuracy_hartree": self.chemical_accuracy_hartree,
        }


@dataclass(frozen=True)
class ActiveSpaceComparisonEntry:
    """Serializable comparison record for one requested active space."""

    configuration_id: str
    status: str
    message: str
    active_space: dict[str, Any]
    provenance: dict[str, Any]
    energies_hartree: dict[str, float | None]
    errors_hartree: dict[str, float | None]
    chemical_accuracy: dict[str, bool | None]
    resources: dict[str, int | None]
    optimization: dict[str, Any]
    timings_seconds: dict[str, float]
    solver_result: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "configuration_id": self.configuration_id,
            "status": self.status,
            "message": self.message,
            "active_space": dict(self.active_space),
            "provenance": dict(self.provenance),
            "energies_hartree": dict(self.energies_hartree),
            "errors_hartree": dict(self.errors_hartree),
            "chemical_accuracy": dict(self.chemical_accuracy),
            "resources": dict(self.resources),
            "optimization": dict(self.optimization),
            "timings_seconds": dict(self.timings_seconds),
            "solver_result": self.solver_result,
        }

    def to_flat_dict(self) -> dict[str, Any]:
        """Return one frontend/dataframe-friendly comparison row."""
        return {
            "configuration_id": self.configuration_id,
            "status": self.status,
            "selection_mode": self.active_space["selection_mode"],
            "n_active_electrons": self.active_space["n_active_electrons"],
            "n_active_orbitals": self.active_space["n_active_orbitals"],
            "orbital_indices": self.active_space.get("resolved_orbital_indices"),
            "hf_total_hartree": self.energies_hartree["hartree_fock_total"],
            "casci_total_hartree": self.energies_hartree["casci_total"],
            "vqe_total_hartree": self.energies_hartree["vqe_total"],
            "fci_total_hartree": self.energies_hartree["fci_full_space_total"],
            "active_space_error_hartree": self.errors_hartree["active_space"],
            "solver_error_hartree": self.errors_hartree["solver"],
            "total_error_hartree": self.errors_hartree["total"],
            "num_qubits": self.resources["num_qubits"],
            "physical_sector_dimension": self.resources["physical_sector_dimension"],
            "num_fermionic_terms": self.resources["num_fermionic_terms"],
            "num_pauli_terms": self.resources["num_pauli_terms"],
            "ansatz_parameters": self.resources["ansatz_parameters"],
            "circuit_depth": self.resources["circuit_depth"],
            "transpiled_depth": self.resources["transpiled_depth"],
            "one_qubit_gates": self.resources["one_qubit_gates"],
            "two_qubit_gates": self.resources["two_qubit_gates"],
            "optimizer_evaluations": self.optimization["evaluations"],
            "optimizer_iterations": self.optimization["iterations"],
            "vqe_runtime_seconds": self.timings_seconds["vqe_optimization"],
            "configuration_runtime_seconds": self.timings_seconds["total"],
            "solver_within_chemical_accuracy": self.chemical_accuracy["solver"],
            "active_space_within_chemical_accuracy": self.chemical_accuracy["active_space"],
            "total_within_chemical_accuracy": self.chemical_accuracy["total"],
        }


@dataclass(frozen=True)
class ActiveSpaceSweepResult:
    """Normalized result for a molecule and a list of active-space choices."""

    status: str
    molecule: dict[str, Any]
    sweep_config: dict[str, Any]
    common_references: dict[str, Any]
    entries: tuple[ActiveSpaceComparisonEntry, ...]
    comparison_table: tuple[dict[str, Any], ...]
    summary: dict[str, Any]
    timings_seconds: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "status": self.status,
            "molecule": dict(self.molecule),
            "sweep_config": dict(self.sweep_config),
            "common_references": dict(self.common_references),
            "entries": [entry.to_dict() for entry in self.entries],
            "comparison_table": [dict(row) for row in self.comparison_table],
            "summary": dict(self.summary),
            "timings_seconds": dict(self.timings_seconds),
        }


def _molecule_metadata(molecule: Molecule) -> dict[str, Any]:
    metadata = get_molecular_data(molecule)
    metadata["basis"] = str(metadata["basis"])
    metadata["geometry_unit"] = "bohr"
    return metadata


def _configuration_id(
    molecule_metadata: dict[str, Any],
    active_space: ActiveSpaceConfig,
    config: ActiveSpaceSweepConfig,
) -> str:
    payload = {
        "schema": "active-space-experiment-v1",
        "molecule": molecule_metadata,
        "active_space": active_space.to_dict(),
        "mapping": config.mapping,
        "ansatz": config.ansatz.to_dict(),
        "solver": config.solver.to_dict(),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"ase_{sha256(canonical.encode('utf-8')).hexdigest()[:20]}"


def _empty_entry(
    molecule_metadata: dict[str, Any],
    active_space: ActiveSpaceConfig,
    config: ActiveSpaceSweepConfig,
    status: str,
    message: str,
    timings: dict[str, float] | None = None,
) -> ActiveSpaceComparisonEntry:
    active_metadata = active_space.to_dict()
    active_metadata["resolved_orbital_indices"] = (
        None if active_space.orbital_indices is None else list(active_space.orbital_indices)
    )
    return ActiveSpaceComparisonEntry(
        configuration_id=_configuration_id(molecule_metadata, active_space, config),
        status=status,
        message=message,
        active_space=active_metadata,
        provenance={
            "selection_mode": active_space.selection_mode,
            "requested_orbital_indices": (
                None if active_space.orbital_indices is None else list(active_space.orbital_indices)
            ),
            "reference_type": None,
            "mapping": config.mapping,
            "ansatz": config.ansatz.to_dict(),
            "optimizer": config.solver.optimizer,
            "evaluation_mode": config.solver.execution_mode,
        },
        energies_hartree={
            "hartree_fock_total": None,
            "casci_total": None,
            "vqe_initial_total": None,
            "vqe_total": None,
            "fci_full_space_total": None,
        },
        errors_hartree={
            "active_space": None,
            "solver": None,
            "total": None,
            "decomposition_residual": None,
        },
        chemical_accuracy={"solver": None, "active_space": None, "total": None},
        resources={
            "num_qubits": 2 * active_space.n_active_orbitals,
            "physical_sector_dimension": None,
            "num_fermionic_terms": None,
            "num_pauli_terms": None,
            "ansatz_parameters": None,
            "circuit_depth": None,
            "transpiled_depth": None,
            "one_qubit_gates": None,
            "two_qubit_gates": None,
        },
        optimization={
            "optimizer": config.solver.optimizer,
            "converged": False,
            "evaluations": None,
            "iterations": None,
            "num_starts": 1 + len(config.solver.random_seeds),
            "termination_message": message,
        },
        timings_seconds={
            "active_space_preparation": 0.0,
            "casci_reference": 0.0,
            "quantum_problem_preparation": 0.0,
            "ansatz_preparation": 0.0,
            "vqe_optimization": 0.0,
            "total": 0.0,
            **(timings or {}),
        },
        solver_result=None,
    )


def _run_configuration(
    molecule: Molecule,
    molecule_metadata: dict[str, Any],
    mf: Any,
    hf_total: float,
    fci_total: float | None,
    active_space: ActiveSpaceConfig,
    config: ActiveSpaceSweepConfig,
    progress_callback: ProgressCallback | None = None,
    configuration_index: int = 0,
    total_configurations: int = 1,
) -> ActiveSpaceComparisonEntry:
    started = perf_counter()
    timings: dict[str, float] = {}
    span = 70.0 / max(total_configurations, 1)
    base_progress = 20.0 + configuration_index * span
    progress_details = {
        "current_active_space": active_space.to_dict(),
        "active_space_index": configuration_index,
        "completed_active_spaces": configuration_index,
        "total_active_spaces": total_configurations,
    }
    try:
        active_space.validate_for_system(
            total_electrons=int(mf.mol.nelectron),
            total_orbitals=int(mf.mo_coeff.shape[1]),
        )
    except ValueError as exc:
        _emit_progress(
            progress_callback,
            "active_space",
            "failed",
            round(base_progress + span),
            message=str(exc),
            **progress_details,
        )
        return _empty_entry(
            molecule_metadata,
            active_space,
            config,
            "invalid_configuration",
            str(exc),
            {"total": perf_counter() - started},
        )

    try:
        _emit_progress(
            progress_callback,
            "active_space",
            "running",
            round(base_progress),
            message=(
                f"Preparing CAS({active_space.n_active_electrons},"
                f"{active_space.n_active_orbitals})"
            ),
            **progress_details,
        )
        step_started = perf_counter()
        electronic_problem = prepare_active_space_problem(molecule, mf, active_space)
        timings["active_space_preparation"] = perf_counter() - step_started

        step_started = perf_counter()
        casci_total = run_active_space_casci_reference(molecule, mf, active_space)
        timings["casci_reference"] = perf_counter() - step_started

        _emit_progress(
            progress_callback,
            "active_space",
            "completed",
            round(base_progress + span * 0.3),
            message="Active-space preparation and CASCI completed",
            **progress_details,
        )

        _emit_progress(
            progress_callback,
            "mapping",
            "running",
            round(base_progress + span * 0.3),
            message="Building fermionic and Jordan-Wigner operators",
            **progress_details,
        )
        step_started = perf_counter()
        quantum_problem = prepare_quantum_problem(
            electronic_problem,
            mapping=config.mapping,
        )
        timings["quantum_problem_preparation"] = perf_counter() - step_started

        step_started = perf_counter()
        prepared_ansatz = prepare_ansatz(quantum_problem, config.ansatz)
        timings["ansatz_preparation"] = perf_counter() - step_started

        _emit_progress(
            progress_callback,
            "mapping",
            "completed",
            round(base_progress + span * 0.55),
            message="Qubit Hamiltonian and UCCSD ansatz prepared",
            **progress_details,
        )

        _emit_progress(
            progress_callback,
            "vqe",
            "running",
            round(base_progress + span * 0.55),
            message="Optimizing exact-statevector VQE",
            **progress_details,
        )
        step_started = perf_counter()
        vqe_result = run_vqe(quantum_problem, prepared_ansatz, config.solver)
        timings["vqe_optimization"] = perf_counter() - step_started
        timings["total"] = perf_counter() - started
        _emit_progress(
            progress_callback,
            "vqe",
            "completed",
            round(base_progress + span),
            message="VQE optimization completed",
            **{
                **progress_details,
                "completed_active_spaces": configuration_index + 1,
            },
        )
    except Exception as exc:
        _emit_progress(
            progress_callback,
            "vqe",
            "failed",
            round(base_progress + span),
            message=f"{type(exc).__name__}: {exc}",
            **progress_details,
        )
        return _empty_entry(
            molecule_metadata,
            active_space,
            config,
            "failed",
            f"{type(exc).__name__}: {exc}",
            {**timings, "total": perf_counter() - started},
        )

    vqe_total = vqe_result.optimal_energy_total
    solver_error = None if vqe_total is None else float(vqe_total - casci_total)
    active_error = None if fci_total is None else float(casci_total - fci_total)
    total_error = None if fci_total is None or vqe_total is None else float(vqe_total - fci_total)
    decomposition_residual = (
        None
        if active_error is None or solver_error is None or total_error is None
        else float(total_error - (active_error + solver_error))
    )
    accuracy = config.chemical_accuracy_hartree
    problem_metadata = quantum_problem.to_metadata()
    status = "completed" if vqe_result.converged else vqe_result.status
    message = vqe_result.termination_message
    if (
        decomposition_residual is not None
        and abs(decomposition_residual) > DECOMPOSITION_TOLERANCE_HARTREE
    ):
        status = "failed"
        message = "energy-error decomposition is inconsistent"
    variational_bound = (
        None if solver_error is None else solver_error >= -VARIATIONAL_TOLERANCE_HARTREE
    )
    return ActiveSpaceComparisonEntry(
        configuration_id=_configuration_id(molecule_metadata, active_space, config),
        status=status,
        message=message,
        active_space={
            **active_space.to_dict(),
            "resolved_orbital_indices": list(electronic_problem.active_orbital_indices),
            "frozen_core_orbital_indices": list(electronic_problem.frozen_core_orbital_indices),
            "external_orbital_indices": list(electronic_problem.external_orbital_indices),
        },
        provenance={
            "selection_mode": active_space.selection_mode,
            "requested_orbital_indices": (
                None if active_space.orbital_indices is None else list(active_space.orbital_indices)
            ),
            "reference_type": quantum_problem.reference_state_kind,
            "mapping": quantum_problem.mapping,
            "spin_orbital_order": problem_metadata["spin_orbital_order"],
            "ansatz": config.ansatz.to_dict(),
            "optimizer": config.solver.optimizer,
            "evaluation_mode": config.solver.execution_mode,
        },
        energies_hartree={
            "hartree_fock_total": hf_total if config.run_hf else None,
            "casci_total": casci_total,
            "vqe_initial_total": vqe_result.initial_energy_total,
            "vqe_total": vqe_total,
            "fci_full_space_total": fci_total,
        },
        errors_hartree={
            "active_space": active_error,
            "solver": solver_error,
            "total": total_error,
            "decomposition_residual": decomposition_residual,
        },
        chemical_accuracy={
            "solver": None if solver_error is None else abs(solver_error) < accuracy,
            "active_space": None if active_error is None else abs(active_error) < accuracy,
            "total": None if total_error is None else abs(total_error) < accuracy,
        },
        resources={
            "num_qubits": quantum_problem.num_qubits,
            "physical_sector_dimension": quantum_problem.physical_sector_dimension,
            "num_fermionic_terms": quantum_problem.num_fermionic_terms,
            "num_pauli_terms": quantum_problem.num_pauli_terms,
            "ansatz_parameters": prepared_ansatz.num_parameters,
            "circuit_depth": prepared_ansatz.circuit_depth,
            "transpiled_depth": prepared_ansatz.transpiled_depth,
            "one_qubit_gates": prepared_ansatz.num_one_qubit_gates,
            "two_qubit_gates": prepared_ansatz.num_two_qubit_gates,
        },
        optimization={
            "optimizer": vqe_result.optimizer,
            "converged": vqe_result.converged,
            "evaluations": vqe_result.num_evaluations,
            "iterations": vqe_result.num_iterations,
            "num_starts": len(vqe_result.runs),
            "termination_message": vqe_result.termination_message,
            "variational_bound_respected": variational_bound,
        },
        timings_seconds=timings,
        solver_result=vqe_result.to_metadata(),
    )


def _summary(entries: tuple[ActiveSpaceComparisonEntry, ...]) -> dict[str, Any]:
    counts = {
        status: sum(entry.status == status for entry in entries)
        for status in ("completed", "not_converged", "failed", "invalid_configuration")
    }
    completed = [entry for entry in entries if entry.status == "completed"]
    solver_errors = [
        abs(float(entry.errors_hartree["solver"]))
        for entry in completed
        if entry.errors_hartree["solver"] is not None
    ]
    active_errors = [
        abs(float(entry.errors_hartree["active_space"]))
        for entry in completed
        if entry.errors_hartree["active_space"] is not None
    ]
    return {
        "counts": counts,
        "completed_configuration_ids": [entry.configuration_id for entry in completed],
        "all_solver_errors_within_chemical_accuracy": (
            bool(solver_errors) and all(entry.chemical_accuracy["solver"] for entry in completed)
        ),
        "maximum_absolute_solver_error_hartree": (
            None if not solver_errors else max(solver_errors)
        ),
        "minimum_absolute_active_space_error_hartree": (
            None if not active_errors else min(active_errors)
        ),
        "comparison_axes": {
            "accuracy": [
                "active_space_error_hartree",
                "solver_error_hartree",
                "total_error_hartree",
            ],
            "resources": [
                "num_qubits",
                "num_pauli_terms",
                "ansatz_parameters",
                "transpiled_depth",
                "two_qubit_gates",
            ],
            "cost": [
                "optimizer_evaluations",
                "optimizer_iterations",
                "vqe_runtime_seconds",
                "configuration_runtime_seconds",
            ],
        },
        "single_composite_score": None,
    }


def run_active_space_sweep(
    molecule: Molecule,
    config: ActiveSpaceSweepConfig,
    progress_callback: ProgressCallback | None = None,
) -> ActiveSpaceSweepResult:
    """Run a generic active-space comparison while reusing common references."""
    if not isinstance(molecule, Molecule):
        raise TypeError("molecule must be a Molecule")
    if not isinstance(config, ActiveSpaceSweepConfig):
        raise TypeError("config must be an ActiveSpaceSweepConfig")

    started = perf_counter()
    molecule_metadata = _molecule_metadata(molecule)
    scf_started = perf_counter()
    _emit_progress(
        progress_callback,
        "scf",
        "running",
        10,
        message="Preparing shared restricted Hartree-Fock orbitals",
        completed_active_spaces=0,
        total_active_spaces=len(config.active_spaces),
    )
    try:
        mf, hf_total = run_hartree_fock(molecule)
    except Exception as exc:
        _emit_progress(
            progress_callback,
            "scf",
            "failed",
            20,
            message=f"{type(exc).__name__}: {exc}",
            completed_active_spaces=0,
            total_active_spaces=len(config.active_spaces),
        )
        scf_runtime = perf_counter() - scf_started
        entries = tuple(
            _empty_entry(
                molecule_metadata,
                active_space,
                config,
                "failed",
                f"shared Hartree-Fock failed: {type(exc).__name__}: {exc}",
            )
            for active_space in config.active_spaces
        )
        table = tuple(entry.to_flat_dict() for entry in entries)
        return ActiveSpaceSweepResult(
            status="failed",
            molecule=molecule_metadata,
            sweep_config=config.to_dict(),
            common_references={
                "hartree_fock": {
                    "requested": config.run_hf,
                    "status": "failed",
                    "energy_total_hartree": None,
                    "message": f"{type(exc).__name__}: {exc}",
                },
                "fci_full_space": {
                    "requested": config.run_fci_reference,
                    "status": "unavailable",
                    "energy_total_hartree": None,
                    "message": "Hartree-Fock reference unavailable",
                },
            },
            entries=entries,
            comparison_table=table,
            summary=_summary(entries),
            timings_seconds={
                "shared_scf": scf_runtime,
                "shared_fci": 0.0,
                "configurations": 0.0,
                "total": perf_counter() - started,
            },
        )
    scf_runtime = perf_counter() - scf_started
    _emit_progress(
        progress_callback,
        "scf",
        "completed",
        20,
        message="Shared molecular orbitals prepared",
        completed_active_spaces=0,
        total_active_spaces=len(config.active_spaces),
    )

    fci_total: float | None = None
    fci_runtime = 0.0
    if config.run_fci_reference:
        fci_started = perf_counter()
        try:
            _fci_solver, fci_total = run_fci(molecule, mf)
            fci_status = "completed"
            fci_message = ""
        except Exception as exc:
            fci_status = "unavailable"
            fci_message = f"{type(exc).__name__}: {exc}"
        fci_runtime = perf_counter() - fci_started
    else:
        fci_status = "not_requested"
        fci_message = "full-space FCI was disabled by the sweep configuration"

    configurations_started = perf_counter()
    entries_list = []
    for index, active_space in enumerate(config.active_spaces):
        entries_list.append(
            _run_configuration(
                molecule,
                molecule_metadata,
                mf,
                hf_total,
                fci_total,
                active_space,
                config,
                progress_callback=progress_callback,
                configuration_index=index,
                total_configurations=len(config.active_spaces),
            )
        )
    entries = tuple(entries_list)
    configurations_runtime = perf_counter() - configurations_started
    completed_count = sum(entry.status == "completed" for entry in entries)
    if completed_count == len(entries):
        status = "completed"
    elif completed_count:
        status = "partial"
    else:
        status = "failed"
    table = tuple(entry.to_flat_dict() for entry in entries)
    return ActiveSpaceSweepResult(
        status=status,
        molecule=molecule_metadata,
        sweep_config=config.to_dict(),
        common_references={
            "hartree_fock": {
                "requested": config.run_hf,
                "status": "completed",
                "energy_total_hartree": hf_total if config.run_hf else None,
                "orbital_preparation_energy_total_hartree": hf_total,
                "message": (
                    ""
                    if config.run_hf
                    else "SCF was still required once to prepare molecular orbitals"
                ),
            },
            "fci_full_space": {
                "requested": config.run_fci_reference,
                "status": fci_status,
                "energy_total_hartree": fci_total,
                "message": fci_message,
            },
        },
        entries=entries,
        comparison_table=table,
        summary=_summary(entries),
        timings_seconds={
            "shared_scf": scf_runtime,
            "shared_fci": fci_runtime,
            "configurations": configurations_runtime,
            "total": perf_counter() - started,
        },
    )
