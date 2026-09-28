"""Generic chemistry-ansatz preparation from a prepared quantum problem."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .electronic_structure import SPIN_ORBITAL_ORDER, spin_orbital_index
from .quantum_problem import PreparedQuantumProblem

SUPPORTED_ANSATZ_TYPES = ("hf_reference", "uccsd")
TRANSPILATION_BASIS_GATES = ("rz", "sx", "x", "cx")
Excitation = tuple[tuple[int, ...], tuple[int, ...]]


@dataclass(frozen=True)
class AnsatzConfig:
    """Serializable configuration for a solver-independent ansatz factory."""

    ansatz_type: str
    reps: int = 1
    preserve_spin: bool = True
    generalized: bool = False
    initialization: str = "zeros"

    def __post_init__(self) -> None:
        normalized_type = self.ansatz_type.strip().lower()
        object.__setattr__(self, "ansatz_type", normalized_type)
        if normalized_type not in SUPPORTED_ANSATZ_TYPES:
            supported = ", ".join(SUPPORTED_ANSATZ_TYPES)
            raise ValueError(f"unsupported ansatz_type: {self.ansatz_type}; supported: {supported}")
        if isinstance(self.reps, bool) or not isinstance(self.reps, int) or self.reps < 1:
            raise ValueError("reps must be a positive integer")
        if not isinstance(self.preserve_spin, bool):
            raise TypeError("preserve_spin must be a bool")
        if not isinstance(self.generalized, bool):
            raise TypeError("generalized must be a bool")
        if self.initialization != "zeros":
            raise ValueError("only initialization='zeros' is supported")

    def to_dict(self) -> dict[str, Any]:
        return {
            "ansatz_type": self.ansatz_type,
            "reps": self.reps,
            "preserve_spin": self.preserve_spin,
            "generalized": self.generalized,
            "initialization": self.initialization,
        }


@dataclass(frozen=True)
class PreparedAnsatz:
    """Parameterized circuit and serializable resource metadata for a solver."""

    circuit: Any
    config: AnsatzConfig
    num_qubits: int
    num_parameters: int
    num_alpha_particles: int
    num_beta_particles: int
    reference_occupation: tuple[int, ...]
    reference_kind: str
    parameter_names: tuple[str, ...]
    initial_parameters: tuple[float, ...]
    single_excitations: tuple[Excitation, ...]
    double_excitations: tuple[Excitation, ...]
    circuit_depth: int
    gate_counts: dict[str, int]
    transpiled_depth: int
    transpiled_gate_counts: dict[str, int]
    num_one_qubit_gates: int
    num_two_qubit_gates: int

    def __post_init__(self) -> None:
        if int(self.circuit.num_qubits) != self.num_qubits:
            raise ValueError("circuit qubit count is inconsistent")
        if int(self.circuit.num_parameters) != self.num_parameters:
            raise ValueError("circuit parameter count is inconsistent")
        if len(self.parameter_names) != self.num_parameters:
            raise ValueError("parameter_names length is inconsistent")
        if len(self.initial_parameters) != self.num_parameters:
            raise ValueError("initial_parameters length is inconsistent")
        if self.num_alpha_particles + self.num_beta_particles != len(self.reference_occupation):
            raise ValueError("spin-resolved particle counts are inconsistent")

    @property
    def reference_bitstring(self) -> int:
        return sum(1 << index for index in self.reference_occupation)

    @property
    def metadata(self) -> dict[str, Any]:
        return self.to_metadata()

    def to_metadata(self) -> dict[str, Any]:
        """Return JSON-compatible ansatz and resource metadata."""

        def serialize(excitations: tuple[Excitation, ...]) -> list[dict[str, list[int]]]:
            return [
                {"occupied": list(occupied), "virtual": list(virtual)}
                for occupied, virtual in excitations
            ]

        return {
            **self.config.to_dict(),
            "num_qubits": self.num_qubits,
            "num_parameters": self.num_parameters,
            "num_alpha_particles": self.num_alpha_particles,
            "num_beta_particles": self.num_beta_particles,
            "spin_orbital_order": SPIN_ORBITAL_ORDER,
            "reference_kind": self.reference_kind,
            "reference_occupation": list(self.reference_occupation),
            "reference_bitstring": self.reference_bitstring,
            "parameter_names": list(self.parameter_names),
            "initial_parameters": list(self.initial_parameters),
            "num_single_excitations": len(self.single_excitations),
            "num_double_excitations": len(self.double_excitations),
            "single_excitations": serialize(self.single_excitations),
            "double_excitations": serialize(self.double_excitations),
            "qiskit_nature_orbital_order": "blocked_alpha_beta",
            "mapper": "InterleavedQubitMapper(JordanWignerMapper)",
            "circuit_depth": self.circuit_depth,
            "gate_counts": dict(self.gate_counts),
            "circuit_metric_definition": "circuit.decompose(reps=2)",
            "transpiled_depth": self.transpiled_depth,
            "transpiled_gate_counts": dict(self.transpiled_gate_counts),
            "transpilation_basis_gates": list(TRANSPILATION_BASIS_GATES),
            "num_one_qubit_gates": self.num_one_qubit_gates,
            "num_two_qubit_gates": self.num_two_qubit_gates,
            "transpilation_status": "PASS",
        }


def build_reference_state_circuit(quantum_problem: PreparedQuantumProblem) -> Any:
    """Prepare the problem's occupation-number reference in project qubit order."""
    if not isinstance(quantum_problem, PreparedQuantumProblem):
        raise TypeError("quantum_problem must be a PreparedQuantumProblem")
    if quantum_problem.mapping != "jordan-wigner":
        raise ValueError("reference circuits currently require jordan-wigner mapping")

    try:
        from qiskit import QuantumCircuit
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise ImportError(
            "Optional dependency 'qiskit' is required for ansatz preparation. "
            "Install it with `pip install -e '.[quantum]'`."
        ) from exc

    circuit = QuantumCircuit(quantum_problem.num_qubits, name="HFReference")
    for qubit in quantum_problem.reference_occupation:
        circuit.x(qubit)
    return circuit


def _active_aufbau_occupation(quantum_problem: PreparedQuantumProblem) -> tuple[int, ...]:
    occupied = [
        spin_orbital_index(index, 0) for index in range(quantum_problem.num_alpha_particles)
    ]
    occupied.extend(
        spin_orbital_index(index, 1) for index in range(quantum_problem.num_beta_particles)
    )
    return tuple(sorted(occupied))


def _blocked_to_interleaved(index: int, num_spatial_orbitals: int) -> int:
    if index < num_spatial_orbitals:
        return spin_orbital_index(index, 0)
    return spin_orbital_index(index - num_spatial_orbitals, 1)


def _translate_excitation(
    excitation: tuple[tuple[int, ...], tuple[int, ...]],
    num_spatial_orbitals: int,
) -> Excitation:
    occupied, virtual = excitation
    return (
        tuple(_blocked_to_interleaved(index, num_spatial_orbitals) for index in occupied),
        tuple(_blocked_to_interleaved(index, num_spatial_orbitals) for index in virtual),
    )


def _circuit_metrics(circuit: Any) -> tuple[int, dict[str, int], int, dict[str, int], int, int]:
    try:
        from qiskit import transpile
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise ImportError(
            "Optional dependency 'qiskit' is required for ansatz preparation. "
            "Install it with `pip install -e '.[quantum]'`."
        ) from exc

    expanded = circuit.decompose(reps=2)
    gate_counts = {str(name): int(count) for name, count in expanded.count_ops().items()}
    compiled = transpile(
        circuit,
        basis_gates=list(TRANSPILATION_BASIS_GATES),
        optimization_level=0,
    )
    transpiled_counts = {str(name): int(count) for name, count in compiled.count_ops().items()}
    one_qubit = sum(1 for instruction in compiled.data if instruction.operation.num_qubits == 1)
    two_qubit = sum(1 for instruction in compiled.data if instruction.operation.num_qubits == 2)
    return (
        int(expanded.depth() or 0),
        gate_counts,
        int(compiled.depth() or 0),
        transpiled_counts,
        one_qubit,
        two_qubit,
    )


def _prepare_uccsd(
    quantum_problem: PreparedQuantumProblem,
    config: AnsatzConfig,
    reference_circuit: Any,
) -> tuple[Any, tuple[Excitation, ...], tuple[Excitation, ...]]:
    expected_reference = _active_aufbau_occupation(quantum_problem)
    if quantum_problem.reference_occupation != expected_reference:
        raise ValueError(
            "Qiskit Nature UCCSD generates excitations from the active-space Aufbau "
            f"occupation {expected_reference}, but the prepared reference is "
            f"{quantum_problem.reference_occupation}; refusing a mismatched ansatz"
        )

    try:
        from qiskit_nature.second_q.circuit.library import UCCSD
        from qiskit_nature.second_q.mappers import (
            InterleavedQubitMapper,
            JordanWignerMapper,
        )
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise ImportError(
            "Optional dependency 'qiskit-nature>=0.8,<0.9' is required for UCCSD. "
            "Install it with `pip install -e '.[quantum]'`."
        ) from exc

    num_spatial_orbitals = quantum_problem.electronic_problem.n_active_orbitals
    mapper = InterleavedQubitMapper(JordanWignerMapper())
    circuit = UCCSD(
        num_spatial_orbitals=num_spatial_orbitals,
        num_particles=(
            quantum_problem.num_alpha_particles,
            quantum_problem.num_beta_particles,
        ),
        qubit_mapper=mapper,
        reps=config.reps,
        initial_state=reference_circuit,
        generalized=config.generalized,
        preserve_spin=config.preserve_spin,
    )
    raw_excitations = circuit.excitation_list
    translated = tuple(
        _translate_excitation(excitation, num_spatial_orbitals) for excitation in raw_excitations
    )
    singles = tuple(excitation for excitation in translated if len(excitation[0]) == 1)
    doubles = tuple(excitation for excitation in translated if len(excitation[0]) == 2)
    if len(singles) + len(doubles) != len(translated):
        raise RuntimeError("UCCSD returned an unsupported excitation rank")
    if circuit.num_parameters != len(translated) * config.reps:
        raise RuntimeError("UCCSD parameter and excitation counts are inconsistent")
    return circuit, singles, doubles


def prepare_ansatz(
    quantum_problem: PreparedQuantumProblem,
    config: AnsatzConfig,
) -> PreparedAnsatz:
    """Build a generic reference or chemistry ansatz without solver logic."""
    if not isinstance(quantum_problem, PreparedQuantumProblem):
        raise TypeError("quantum_problem must be a PreparedQuantumProblem")
    if not isinstance(config, AnsatzConfig):
        raise TypeError("config must be an AnsatzConfig")

    reference_circuit = build_reference_state_circuit(quantum_problem)
    singles: tuple[Excitation, ...] = ()
    doubles: tuple[Excitation, ...] = ()
    if config.ansatz_type == "hf_reference":
        circuit = reference_circuit
    elif config.ansatz_type == "uccsd":
        circuit, singles, doubles = _prepare_uccsd(
            quantum_problem,
            config,
            reference_circuit,
        )
    else:  # pragma: no cover - guarded by AnsatzConfig
        raise ValueError(f"unsupported ansatz_type: {config.ansatz_type}")

    parameters = tuple(circuit.parameters)
    metrics = _circuit_metrics(circuit)
    return PreparedAnsatz(
        circuit=circuit,
        config=config,
        num_qubits=quantum_problem.num_qubits,
        num_parameters=len(parameters),
        num_alpha_particles=quantum_problem.num_alpha_particles,
        num_beta_particles=quantum_problem.num_beta_particles,
        reference_occupation=quantum_problem.reference_occupation,
        reference_kind=quantum_problem.reference_state_kind,
        parameter_names=tuple(str(parameter) for parameter in parameters),
        initial_parameters=tuple(0.0 for _ in parameters),
        single_excitations=singles,
        double_excitations=doubles,
        circuit_depth=metrics[0],
        gate_counts=metrics[1],
        transpiled_depth=metrics[2],
        transpiled_gate_counts=metrics[3],
        num_one_qubit_gates=metrics[4],
        num_two_qubit_gates=metrics[5],
    )
