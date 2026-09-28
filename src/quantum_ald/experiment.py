"""Serializable user experiment contract and thin scientific-engine facade."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
from math import isfinite
from pathlib import Path
import platform
from time import perf_counter
from typing import Any, Callable

from .active_space import ActiveSpaceConfig
from .active_space_sweep import (
    CHEMICAL_ACCURACY_HARTREE,
    ActiveSpaceSweepConfig,
    run_active_space_sweep,
)
from .ansatz import AnsatzConfig
from .classical_methods import run_fci, run_hartree_fock
from .generic_vqe import VQESolverConfig
from .molecule_loader import Molecule, get_molecular_data, molecule_from_string

SCHEMA_VERSION = "1"
SUPPORTED_METHODS = ("hf", "casci", "fci", "vqe")
SUPPORTED_EXECUTION_MODES = ("exact_statevector",)
SUPPORTED_MAPPINGS = ("jordan-wigner",)
IDENTITY_FLOAT_SIGNIFICANT_DIGITS = 15
ProgressCallback = Callable[[dict[str, Any]], None]

_ELEMENT_SYMBOLS = tuple(
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co "
    "Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb "
    "Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re "
    "Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es "
    "Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split()
)
_ATOMIC_NUMBERS = {symbol: index for index, symbol in enumerate(_ELEMENT_SYMBOLS, 1)}


class ExperimentConfigurationError(ValueError):
    """Small structured error suitable for a future API response."""

    def __init__(self, code: str, field: str, message: str) -> None:
        self.code = code
        self.field = field
        self.message = message
        super().__init__(message)

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "field": self.field, "message": self.message}


def _configuration_error(code: str, field: str, message: str) -> None:
    raise ExperimentConfigurationError(code, field, message)


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
        # Progress reporting is observational and cannot change the result.
        return


@dataclass(frozen=True)
class AtomSpec:
    """One user-provided atom in the molecule's declared coordinate unit."""

    symbol: str
    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        if not isinstance(self.symbol, str) or not self.symbol.strip():
            _configuration_error(
                "invalid_atom_symbol",
                "symbol",
                "atom symbol must be a non-empty chemical element symbol",
            )
        symbol = self.symbol.strip().capitalize()
        if symbol not in _ATOMIC_NUMBERS:
            _configuration_error(
                "invalid_atom_symbol",
                "symbol",
                f"unsupported chemical element symbol: {self.symbol!r}",
            )
        object.__setattr__(self, "symbol", symbol)
        for field_name in ("x", "y", "z"):
            raw_value = getattr(self, field_name)
            if isinstance(raw_value, bool):
                _configuration_error(
                    "invalid_coordinate",
                    field_name,
                    f"coordinate {field_name} must be a finite number",
                )
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                _configuration_error(
                    "invalid_coordinate",
                    field_name,
                    f"coordinate {field_name} must be a finite number",
                )
            if not isfinite(value):
                _configuration_error(
                    "invalid_coordinate",
                    field_name,
                    f"coordinate {field_name} must be a finite number",
                )
            object.__setattr__(self, field_name, value)

    def to_dict(self) -> dict[str, Any]:
        return {"symbol": self.symbol, "x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AtomSpec:
        if not isinstance(data, dict):
            _configuration_error("invalid_atom", "atoms", "each atom must be an object")
        try:
            return cls(
                symbol=data["symbol"],
                x=data["x"],
                y=data["y"],
                z=data["z"],
            )
        except KeyError as exc:
            _configuration_error(
                "missing_field",
                f"atoms.{exc.args[0]}",
                f"atom field {exc.args[0]!r} is required",
            )


@dataclass(frozen=True)
class MoleculeSpec:
    """PySCF-independent molecular input requested by a user."""

    atoms: tuple[AtomSpec, ...]
    charge: int = 0
    spin: int = 0
    basis: str = "sto-3g"
    unit: str = "angstrom"
    name: str | None = None

    def __post_init__(self) -> None:
        atoms = tuple(self.atoms)
        object.__setattr__(self, "atoms", atoms)
        if not atoms:
            _configuration_error(
                "empty_molecule",
                "molecule.atoms",
                "a molecule must contain at least one atom",
            )
        if any(not isinstance(atom, AtomSpec) for atom in atoms):
            _configuration_error(
                "invalid_atom",
                "molecule.atoms",
                "molecule atoms must be AtomSpec values",
            )
        if isinstance(self.charge, bool) or not isinstance(self.charge, int):
            _configuration_error(
                "invalid_charge",
                "molecule.charge",
                "molecular charge must be an integer",
            )
        if isinstance(self.spin, bool) or not isinstance(self.spin, int) or self.spin < 0:
            _configuration_error(
                "invalid_spin",
                "molecule.spin",
                "spin must be a non-negative integer equal to N_alpha - N_beta = 2S",
            )
        if not isinstance(self.basis, str) or not self.basis.strip():
            _configuration_error(
                "invalid_basis",
                "molecule.basis",
                "basis must be a non-empty string",
            )
        basis = self.basis.strip().lower()
        unit = self.unit.strip().lower() if isinstance(self.unit, str) else ""
        if unit not in {"angstrom", "bohr"}:
            _configuration_error(
                "unsupported_unit",
                "molecule.unit",
                "supported coordinate units are 'angstrom' and 'bohr'",
            )
        name = self.name
        if name is not None:
            if not isinstance(name, str) or not name.strip():
                _configuration_error(
                    "invalid_name",
                    "molecule.name",
                    "molecule name must be null or a non-empty string",
                )
            name = name.strip()
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "unit", unit)
        object.__setattr__(self, "name", name)

        electrons = sum(_ATOMIC_NUMBERS[atom.symbol] for atom in atoms) - self.charge
        if electrons <= 0:
            _configuration_error(
                "invalid_charge",
                "molecule.charge",
                "molecular charge leaves no electrons in the requested molecule",
            )
        if self.spin > electrons or (electrons - self.spin) % 2:
            _configuration_error(
                "invalid_spin",
                "molecule.spin",
                (
                    f"spin={self.spin} is incompatible with {electrons} electrons; "
                    "PySCF uses spin = N_alpha - N_beta = 2S"
                ),
            )

    @property
    def num_electrons(self) -> int:
        return sum(_ATOMIC_NUMBERS[atom.symbol] for atom in self.atoms) - self.charge

    @property
    def runtime_name(self) -> str:
        return self.name or "".join(atom.symbol for atom in self.atoms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "atoms": [atom.to_dict() for atom in self.atoms],
            "charge": self.charge,
            "spin": self.spin,
            "basis": self.basis,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MoleculeSpec:
        if not isinstance(data, dict):
            _configuration_error(
                "invalid_molecule",
                "molecule",
                "molecule must be a JSON object",
            )
        try:
            atoms_data = data["atoms"]
        except KeyError:
            _configuration_error(
                "missing_field",
                "molecule.atoms",
                "molecule atoms are required",
            )
        if not isinstance(atoms_data, (list, tuple)):
            _configuration_error(
                "invalid_molecule",
                "molecule.atoms",
                "molecule atoms must be an array",
            )
        return cls(
            name=data.get("name"),
            atoms=tuple(AtomSpec.from_dict(atom) for atom in atoms_data),
            charge=data.get("charge", 0),
            spin=data.get("spin", 0),
            basis=data.get("basis", "sto-3g"),
            unit=data.get("unit", "angstrom"),
        )

    @classmethod
    def from_xyz(
        cls,
        xyz_text: str,
        *,
        name: str | None = None,
        charge: int = 0,
        spin: int = 0,
        basis: str = "sto-3g",
        unit: str = "angstrom",
    ) -> MoleculeSpec:
        if not isinstance(xyz_text, str) or not xyz_text.strip():
            _configuration_error("invalid_xyz", "xyz", "XYZ content must not be empty")
        lines = xyz_text.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if lines and lines[0].strip().isdigit():
            atom_count = int(lines[0].strip())
            if len(lines) < atom_count + 2:
                _configuration_error(
                    "invalid_xyz",
                    "xyz",
                    "XYZ content has fewer atom rows than its declared atom count",
                )
            atom_lines = lines[2 : 2 + atom_count]
        else:
            atom_lines = [line for line in lines if line.strip()]
        atoms = []
        for index, line in enumerate(atom_lines):
            fields = line.split()
            if len(fields) < 4:
                _configuration_error(
                    "invalid_xyz",
                    f"xyz.atoms[{index}]",
                    "each XYZ atom row must contain symbol, x, y and z",
                )
            atoms.append(AtomSpec(fields[0], fields[1], fields[2], fields[3]))
        return cls(
            name=name,
            atoms=tuple(atoms),
            charge=charge,
            spin=spin,
            basis=basis,
            unit=unit,
        )

    @classmethod
    def from_xyz_file(
        cls,
        path: str | Path,
        **kwargs: Any,
    ) -> MoleculeSpec:
        source = Path(path)
        if not source.exists():
            _configuration_error(
                "xyz_not_found",
                "xyz_file",
                f"XYZ file not found: {source}",
            )
        kwargs.setdefault("name", source.stem)
        return cls.from_xyz(source.read_text(encoding="utf-8"), **kwargs)

    @classmethod
    def predefined(cls, name: str) -> MoleculeSpec:
        normalized = name.strip().lower()
        presets = {
            "h2": cls(
                name="H2",
                atoms=(AtomSpec("H", 0, 0, 0), AtomSpec("H", 0, 0, 0.74)),
            ),
            "lih": cls(
                name="LiH",
                atoms=(AtomSpec("Li", 0, 0, 0), AtomSpec("H", 0, 0, 1.64)),
            ),
            "h2o": cls(
                name="H2O",
                atoms=(
                    AtomSpec("O", 0.0, 0.0, 0.118720),
                    AtomSpec("H", 0.0, 0.755453, -0.474880),
                    AtomSpec("H", 0.0, -0.755453, -0.474880),
                ),
            ),
        }
        if normalized not in presets:
            _configuration_error(
                "unsupported_predefined_molecule",
                "molecule.name",
                f"unsupported predefined molecule: {name!r}",
            )
        return presets[normalized]

    def to_runtime_molecule(self) -> Molecule:
        atom_lines = "\n".join(
            f"{atom.symbol} {atom.x:.17g} {atom.y:.17g} {atom.z:.17g}" for atom in self.atoms
        )
        return molecule_from_string(
            atom_lines,
            basis=self.basis,
            charge=self.charge,
            spin=self.spin,
            name=self.runtime_name,
            unit=self.unit,
        )


def _active_space_from_dict(data: dict[str, Any], index: int) -> ActiveSpaceConfig:
    if not isinstance(data, dict):
        _configuration_error(
            "invalid_active_space",
            f"active_spaces[{index}]",
            "active-space configuration must be an object",
        )
    values = dict(data)
    if values.get("orbital_indices") is not None:
        values["orbital_indices"] = tuple(values["orbital_indices"])
        values.setdefault("selection_mode", "manual")
    try:
        return ActiveSpaceConfig(**values)
    except (TypeError, ValueError) as exc:
        _configuration_error(
            "invalid_active_space",
            f"active_spaces[{index}]",
            str(exc),
        )


def _ansatz_from_dict(data: dict[str, Any] | None) -> AnsatzConfig | None:
    if data is None:
        return None
    if not isinstance(data, dict):
        _configuration_error("invalid_ansatz", "ansatz", "ansatz must be an object or null")
    try:
        return AnsatzConfig(**data)
    except (TypeError, ValueError) as exc:
        _configuration_error("invalid_ansatz", "ansatz", str(exc))


def _solver_from_dict(data: dict[str, Any] | None) -> VQESolverConfig | None:
    if data is None:
        return None
    if not isinstance(data, dict):
        _configuration_error("invalid_solver", "solver", "solver must be an object or null")
    values = dict(data)
    if values.get("random_seeds") is not None:
        values["random_seeds"] = tuple(values["random_seeds"])
    try:
        return VQESolverConfig(**values)
    except (TypeError, ValueError) as exc:
        _configuration_error("invalid_solver", "solver", str(exc))


@dataclass(frozen=True)
class ExperimentConfig:
    """Versioned scientific intent supplied by a user or frontend."""

    molecule: MoleculeSpec
    active_spaces: tuple[ActiveSpaceConfig, ...]
    methods: tuple[str, ...]
    mapping: str = "jordan-wigner"
    ansatz: AnsatzConfig | None = None
    solver: VQESolverConfig | None = None
    execution_mode: str = "exact_statevector"
    chemical_accuracy_hartree: float = CHEMICAL_ACCURACY_HARTREE
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.molecule, MoleculeSpec):
            _configuration_error(
                "invalid_molecule",
                "molecule",
                "molecule must be a MoleculeSpec",
            )
        active_spaces = tuple(self.active_spaces)
        if any(not isinstance(item, ActiveSpaceConfig) for item in active_spaces):
            _configuration_error(
                "invalid_active_space",
                "active_spaces",
                "active_spaces must contain ActiveSpaceConfig values",
            )
        serialized_spaces = [
            json.dumps(item.to_dict(), sort_keys=True, separators=(",", ":"))
            for item in active_spaces
        ]
        if len(set(serialized_spaces)) != len(serialized_spaces):
            _configuration_error(
                "duplicate_active_space",
                "active_spaces",
                "active-space configurations must not be duplicated",
            )
        object.__setattr__(self, "active_spaces", active_spaces)

        if not isinstance(self.methods, (list, tuple)) or not self.methods:
            _configuration_error(
                "missing_methods",
                "methods",
                "at least one method must be requested",
            )
        normalized_methods = []
        for method in self.methods:
            if not isinstance(method, str):
                _configuration_error(
                    "unsupported_method",
                    "methods",
                    "method names must be strings",
                )
            normalized_methods.append(method.strip().lower())
        unsupported = sorted(set(normalized_methods) - set(SUPPORTED_METHODS))
        if unsupported:
            _configuration_error(
                "unsupported_method",
                "methods",
                f"unsupported methods: {', '.join(unsupported)}",
            )
        if len(set(normalized_methods)) != len(normalized_methods):
            _configuration_error(
                "duplicate_method",
                "methods",
                "methods must not contain duplicates",
            )
        methods = tuple(method for method in SUPPORTED_METHODS if method in normalized_methods)
        object.__setattr__(self, "methods", methods)

        mapping = self.mapping.strip().lower() if isinstance(self.mapping, str) else ""
        if mapping not in SUPPORTED_MAPPINGS:
            _configuration_error(
                "unsupported_mapping",
                "mapping",
                f"supported mappings: {', '.join(SUPPORTED_MAPPINGS)}",
            )
        object.__setattr__(self, "mapping", mapping)
        execution_mode = (
            self.execution_mode.strip().lower() if isinstance(self.execution_mode, str) else ""
        )
        if execution_mode not in SUPPORTED_EXECUTION_MODES:
            _configuration_error(
                "unsupported_execution_mode",
                "execution_mode",
                f"supported execution modes: {', '.join(SUPPORTED_EXECUTION_MODES)}",
            )
        object.__setattr__(self, "execution_mode", execution_mode)

        if self.schema_version != SCHEMA_VERSION:
            _configuration_error(
                "unsupported_schema_version",
                "schema_version",
                f"supported experiment schema version: {SCHEMA_VERSION}",
            )
        try:
            accuracy = float(self.chemical_accuracy_hartree)
        except (TypeError, ValueError):
            _configuration_error(
                "invalid_chemical_accuracy",
                "chemical_accuracy_hartree",
                "chemical accuracy must be a positive finite number",
            )
        if not isfinite(accuracy) or accuracy <= 0.0:
            _configuration_error(
                "invalid_chemical_accuracy",
                "chemical_accuracy_hartree",
                "chemical accuracy must be a positive finite number",
            )
        object.__setattr__(self, "chemical_accuracy_hartree", accuracy)

        has_active_method = "casci" in methods or "vqe" in methods
        if has_active_method and not active_spaces:
            _configuration_error(
                "missing_active_space",
                "active_spaces",
                "CASCI or VQE requires at least one active-space configuration",
            )
        if active_spaces and not has_active_method:
            _configuration_error(
                "unused_active_space",
                "active_spaces",
                "active spaces require CASCI and VQE in schema version 1",
            )
        if "vqe" in methods and "casci" not in methods:
            _configuration_error(
                "missing_method_dependency",
                "methods",
                "VQE requires CASCI as its same-active-space reference in schema version 1",
            )
        if "casci" in methods and "vqe" not in methods:
            _configuration_error(
                "unsupported_method_combination",
                "methods",
                "CASCI-only sweeps are not yet supported; request CASCI with VQE",
            )
        if "vqe" in methods:
            if not isinstance(self.ansatz, AnsatzConfig):
                _configuration_error(
                    "missing_ansatz",
                    "ansatz",
                    "VQE requires an explicit AnsatzConfig",
                )
            if not isinstance(self.solver, VQESolverConfig):
                _configuration_error(
                    "missing_solver",
                    "solver",
                    "VQE requires an explicit VQESolverConfig",
                )
            if self.solver.execution_mode != execution_mode:
                _configuration_error(
                    "execution_mode_mismatch",
                    "solver.execution_mode",
                    "solver execution mode must match the experiment execution mode",
                )
        elif self.ansatz is not None or self.solver is not None:
            _configuration_error(
                "unexpected_quantum_configuration",
                "ansatz",
                "ansatz and solver must be null when VQE is not requested",
            )

        for index, active_space in enumerate(active_spaces):
            if active_space.n_active_electrons > self.molecule.num_electrons:
                _configuration_error(
                    "invalid_active_space",
                    f"active_spaces[{index}].n_active_electrons",
                    (
                        f"CAS({active_space.n_active_electrons},"
                        f"{active_space.n_active_orbitals}) requests more active electrons "
                        f"than the molecule's {self.molecule.num_electrons} electrons"
                    ),
                )
            inactive = self.molecule.num_electrons - active_space.n_active_electrons
            if inactive % 2:
                _configuration_error(
                    "invalid_active_space",
                    f"active_spaces[{index}].n_active_electrons",
                    "the RHF frozen-core partition requires an even inactive electron count",
                )
            if (
                active_space.n_active_electrons < self.molecule.spin
                or (active_space.n_active_electrons + self.molecule.spin) % 2
            ):
                _configuration_error(
                    "invalid_active_space",
                    f"active_spaces[{index}]",
                    "active electrons are incompatible with the requested molecular spin",
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "molecule": self.molecule.to_dict(),
            "active_spaces": [item.to_dict() for item in self.active_spaces],
            "methods": list(self.methods),
            "mapping": self.mapping,
            "ansatz": None if self.ansatz is None else self.ansatz.to_dict(),
            "solver": None if self.solver is None else self.solver.to_dict(),
            "execution_mode": self.execution_mode,
            "chemical_accuracy_hartree": self.chemical_accuracy_hartree,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExperimentConfig:
        if not isinstance(data, dict):
            _configuration_error(
                "invalid_experiment_config",
                "config",
                "experiment configuration must be a JSON object",
            )
        try:
            molecule = MoleculeSpec.from_dict(data["molecule"])
            active_data = data.get("active_spaces", [])
            if not isinstance(active_data, (list, tuple)):
                _configuration_error(
                    "invalid_active_space",
                    "active_spaces",
                    "active_spaces must be an array",
                )
            active_spaces = tuple(
                _active_space_from_dict(item, index) for index, item in enumerate(active_data)
            )
            return cls(
                schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
                molecule=molecule,
                active_spaces=active_spaces,
                methods=tuple(data["methods"]),
                mapping=data.get("mapping", "jordan-wigner"),
                ansatz=_ansatz_from_dict(data.get("ansatz")),
                solver=_solver_from_dict(data.get("solver")),
                execution_mode=data.get("execution_mode", "exact_statevector"),
                chemical_accuracy_hartree=data.get(
                    "chemical_accuracy_hartree",
                    CHEMICAL_ACCURACY_HARTREE,
                ),
            )
        except KeyError as exc:
            _configuration_error(
                "missing_field",
                str(exc.args[0]),
                f"experiment field {exc.args[0]!r} is required",
            )

    def _identity_payload(self) -> dict[str, Any]:
        molecule = self.molecule.to_dict()
        molecule.pop("name", None)
        for atom in molecule["atoms"]:
            for coordinate in ("x", "y", "z"):
                atom[coordinate] = float(
                    format(
                        atom[coordinate],
                        f".{IDENTITY_FLOAT_SIGNIFICANT_DIGITS}g",
                    )
                )
        active_spaces = sorted(
            (item.to_dict() for item in self.active_spaces),
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
        payload = self.to_dict()
        payload["molecule"] = molecule
        payload["active_spaces"] = active_spaces
        payload["methods"] = sorted(self.methods)
        return payload

    @property
    def experiment_id(self) -> str:
        canonical = json.dumps(
            self._identity_payload(),
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = sha256(canonical.encode("utf-8")).hexdigest()[:24]
        return f"exp_{digest}"


@dataclass(frozen=True)
class ExperimentResult:
    """JSON-compatible response returned by the public experiment facade."""

    schema_version: str
    experiment_id: str
    status: str
    normalized_config: dict[str, Any]
    molecule: dict[str, Any]
    requested_methods: tuple[str, ...]
    executed_methods: tuple[str, ...]
    results: dict[str, Any]
    comparison_table: tuple[dict[str, Any], ...]
    timings_seconds: dict[str, float]
    warnings: tuple[dict[str, Any], ...]
    errors: tuple[dict[str, Any], ...]
    provenance: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "experiment_id": self.experiment_id,
            "status": self.status,
            "normalized_config": dict(self.normalized_config),
            "molecule": dict(self.molecule),
            "requested_methods": list(self.requested_methods),
            "executed_methods": list(self.executed_methods),
            "results": dict(self.results),
            "comparison_table": [dict(row) for row in self.comparison_table],
            "timings_seconds": dict(self.timings_seconds),
            "warnings": [dict(item) for item in self.warnings],
            "errors": [dict(item) for item in self.errors],
            "provenance": dict(self.provenance),
        }


def _package_versions() -> dict[str, str | None]:
    packages = (
        "quantum-ald-simulation",
        "numpy",
        "scipy",
        "pyscf",
        "qiskit",
        "qiskit-nature",
        "qiskit-algorithms",
        "qiskit-aer",
    )
    versions = {}
    for package in packages:
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            versions[package] = None
    return versions


def _provenance(config: ExperimentConfig) -> dict[str, Any]:
    return {
        "schema_version": config.schema_version,
        "experiment_id": config.experiment_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "packages": _package_versions(),
        "scientific_engine": (
            "run_active_space_sweep" if config.active_spaces else "classical_references"
        ),
        "identity_float_significant_digits": IDENTITY_FLOAT_SIGNIFICANT_DIGITS,
    }


def _run_global_references(
    config: ExperimentConfig,
    molecule: Molecule,
    started: float,
    molecule_build_runtime: float,
) -> ExperimentResult:
    engine_started = perf_counter()
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    executed: list[str] = []
    references: dict[str, Any] = {
        "hartree_fock": {"status": "not_requested", "energy_total_hartree": None},
        "fci_full_space": {"status": "not_requested", "energy_total_hartree": None},
    }
    try:
        mf, hf_total = run_hartree_fock(molecule)
        if "hf" in config.methods:
            references["hartree_fock"] = {
                "status": "completed",
                "energy_total_hartree": hf_total,
            }
            executed.append("hf")
        else:
            references["hartree_fock"] = {
                "status": "preparation_only",
                "energy_total_hartree": None,
                "orbital_preparation_energy_total_hartree": hf_total,
            }
    except Exception as exc:
        errors.append(
            {
                "code": "hartree_fock_failed",
                "field": "methods",
                "message": f"{type(exc).__name__}: {exc}",
            }
        )
        mf = None
    if "fci" in config.methods and mf is not None:
        try:
            _solver, fci_total = run_fci(molecule, mf)
            references["fci_full_space"] = {
                "status": "completed",
                "energy_total_hartree": fci_total,
            }
            executed.append("fci")
        except Exception as exc:
            references["fci_full_space"] = {
                "status": "unavailable",
                "energy_total_hartree": None,
                "message": f"{type(exc).__name__}: {exc}",
            }
            warnings.append(
                {
                    "code": "reference_unavailable",
                    "field": "methods.fci",
                    "message": f"{type(exc).__name__}: {exc}",
                }
            )
    status = "failed" if errors else "completed"
    engine_runtime = perf_counter() - engine_started
    return ExperimentResult(
        schema_version=config.schema_version,
        experiment_id=config.experiment_id,
        status=status,
        normalized_config=config.to_dict(),
        molecule={
            "requested": config.molecule.to_dict(),
            "runtime": get_molecular_data(molecule),
        },
        requested_methods=config.methods,
        executed_methods=tuple(method for method in SUPPORTED_METHODS if method in executed),
        results={
            "global_references": references,
            "active_spaces": [],
            "summary": {"counts": {}},
        },
        comparison_table=(),
        timings_seconds={
            "molecule_build": molecule_build_runtime,
            "scientific_engine": engine_runtime,
            "total": perf_counter() - started,
        },
        warnings=tuple(warnings),
        errors=tuple(errors),
        provenance=_provenance(config),
    )


def run_experiment(
    config: ExperimentConfig,
    progress_callback: ProgressCallback | None = None,
) -> ExperimentResult:
    """Execute validated user intent through the existing scientific engine."""
    if not isinstance(config, ExperimentConfig):
        _configuration_error(
            "invalid_experiment_config",
            "config",
            "run_experiment expects an ExperimentConfig",
        )
    _emit_progress(progress_callback, "validate", "completed", 2, message="Configuration valid")
    started = perf_counter()
    molecule_started = perf_counter()
    _emit_progress(progress_callback, "molecule", "running", 4, message="Building molecule")
    try:
        molecule = config.molecule.to_runtime_molecule()
    except Exception as exc:
        _emit_progress(
            progress_callback,
            "molecule",
            "failed",
            10,
            message=f"{type(exc).__name__}: {exc}",
        )
        raise
    molecule_build_runtime = perf_counter() - molecule_started
    _emit_progress(progress_callback, "molecule", "completed", 10, message="Molecule built")
    if not config.active_spaces:
        _emit_progress(progress_callback, "scf", "running", 20, message="Running references")
        result = _run_global_references(
            config,
            molecule,
            started,
            molecule_build_runtime,
        )
        _emit_progress(
            progress_callback,
            "scf",
            "failed" if result.status == "failed" else "completed",
            90,
            message="Global references completed",
        )
        _emit_progress(
            progress_callback,
            "comparison",
            "completed",
            100,
            message="Experiment result normalized",
        )
        return result

    sweep_config = ActiveSpaceSweepConfig(
        active_spaces=config.active_spaces,
        ansatz=config.ansatz,
        solver=config.solver,
        run_hf="hf" in config.methods,
        run_casci=True,
        run_fci_reference="fci" in config.methods,
        mapping=config.mapping,
        chemical_accuracy_hartree=config.chemical_accuracy_hartree,
    )
    engine_started = perf_counter()
    sweep = run_active_space_sweep(
        molecule,
        sweep_config,
        progress_callback=progress_callback,
    )
    engine_runtime = perf_counter() - engine_started
    _emit_progress(
        progress_callback,
        "comparison",
        "running",
        95,
        message="Building active-space comparison",
        completed_active_spaces=sum(entry.status == "completed" for entry in sweep.entries),
        total_active_spaces=len(sweep.entries),
    )
    entries = [entry.to_dict() for entry in sweep.entries]
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    fci_reference = sweep.common_references["fci_full_space"]
    if "fci" in config.methods and fci_reference["status"] != "completed":
        warnings.append(
            {
                "code": "reference_unavailable",
                "field": "methods.fci",
                "message": fci_reference.get("message", "full-space FCI is unavailable"),
            }
        )
    for index, entry in enumerate(sweep.entries):
        if entry.status == "completed":
            continue
        code = {
            "invalid_configuration": "invalid_active_space",
            "not_converged": "vqe_not_converged",
            "failed": "configuration_failed",
        }.get(entry.status, "configuration_failed")
        errors.append(
            {
                "code": code,
                "field": f"active_spaces[{index}]",
                "message": entry.message,
                "configuration_id": entry.configuration_id,
            }
        )

    executed = []
    if "hf" in config.methods and sweep.common_references["hartree_fock"]["status"] == "completed":
        executed.append("hf")
    if any(entry.energies_hartree["casci_total"] is not None for entry in sweep.entries):
        executed.append("casci")
    if "fci" in config.methods and fci_reference["status"] == "completed":
        executed.append("fci")
    if any(entry.energies_hartree["vqe_total"] is not None for entry in sweep.entries):
        executed.append("vqe")

    if sweep.status == "completed":
        status = "completed"
    elif sweep.status == "partial":
        status = "partial"
    elif sweep.entries and all(entry.status == "invalid_configuration" for entry in sweep.entries):
        status = "invalid_configuration"
    else:
        status = "failed"
    result = ExperimentResult(
        schema_version=config.schema_version,
        experiment_id=config.experiment_id,
        status=status,
        normalized_config=config.to_dict(),
        molecule={
            "requested": config.molecule.to_dict(),
            "runtime": sweep.molecule,
        },
        requested_methods=config.methods,
        executed_methods=tuple(method for method in SUPPORTED_METHODS if method in executed),
        results={
            "global_references": sweep.common_references,
            "active_spaces": entries,
            "summary": sweep.summary,
        },
        comparison_table=sweep.comparison_table,
        timings_seconds={
            "molecule_build": molecule_build_runtime,
            "scientific_engine": engine_runtime,
            "shared_scf": sweep.timings_seconds["shared_scf"],
            "shared_fci": sweep.timings_seconds["shared_fci"],
            "configurations": sweep.timings_seconds["configurations"],
            "total": perf_counter() - started,
        },
        warnings=tuple(warnings),
        errors=tuple(errors),
        provenance=_provenance(config),
    )
    _emit_progress(
        progress_callback,
        "comparison",
        "completed" if status in {"completed", "partial"} else "failed",
        100,
        message="Experiment result normalized",
        completed_active_spaces=sum(entry.status == "completed" for entry in sweep.entries),
        total_active_spaces=len(sweep.entries),
    )
    return result
