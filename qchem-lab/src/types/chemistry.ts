export type CoordinateUnit = "angstrom" | "bohr";
export type ChemistryMethod = "hf" | "casci" | "fci" | "vqe";
export type ActiveSpaceSelectionMode = "canonical" | "manual";
export type ChemistryStepStatus = "pending" | "running" | "completed" | "failed";
export type ChemistryJobStatus =
  | "queued"
  | "running"
  | "completed"
  | "partial"
  | "failed"
  | "invalid_configuration";

export interface AtomSpec {
  symbol: string;
  x: number;
  y: number;
  z: number;
}

export interface AtomDraft extends AtomSpec {
  id: string;
}

export interface MoleculeSpec {
  name: string | null;
  atoms: AtomSpec[];
  charge: number;
  spin: number;
  basis: string;
  unit: CoordinateUnit;
}

export interface ActiveSpaceConfig {
  n_active_electrons: number;
  n_active_orbitals: number;
  orbital_indices: number[] | null;
  selection_mode: ActiveSpaceSelectionMode;
}

export interface ActiveSpaceDraft extends ActiveSpaceConfig {
  id: string;
  orbitalIndicesInput: string;
}

export interface AnsatzConfig {
  ansatz_type: "uccsd";
  reps: number;
  preserve_spin: boolean;
  generalized: boolean;
  initialization: "zeros";
}

export interface VQESolverConfig {
  optimizer: "slsqp";
  maxiter: number;
  tolerance: number;
  initialization: "ansatz_default";
  random_seeds: number[];
  random_scale: number;
  execution_mode: "exact_statevector";
}

export interface ExperimentConfig {
  schema_version: "1";
  molecule: MoleculeSpec;
  active_spaces: ActiveSpaceConfig[];
  methods: ChemistryMethod[];
  mapping: "jordan-wigner";
  ansatz: AnsatzConfig | null;
  solver: VQESolverConfig | null;
  execution_mode: "exact_statevector";
  chemical_accuracy_hartree: number;
}

export interface StructuredMessage {
  code: string;
  field: string;
  message: string;
  configuration_id?: string;
}

export interface ActiveSpaceResult {
  configuration_id: string;
  status: string;
  message: string;
  active_space: ActiveSpaceConfig & {
    resolved_orbital_indices?: number[] | null;
    frozen_core_orbital_indices?: number[];
    external_orbital_indices?: number[];
  };
  energies_hartree: {
    hartree_fock_total: number | null;
    casci_total: number | null;
    vqe_initial_total: number | null;
    vqe_total: number | null;
    fci_full_space_total: number | null;
  };
  errors_hartree: {
    active_space: number | null;
    solver: number | null;
    total: number | null;
    decomposition_residual: number | null;
  };
  resources: Record<string, number | null>;
  optimization: Record<string, number | string | boolean | null>;
  timings_seconds: Record<string, number>;
}

export interface ChemistryComparisonRow {
  configuration_id: string;
  status: string;
  selection_mode: ActiveSpaceSelectionMode;
  n_active_electrons: number;
  n_active_orbitals: number;
  orbital_indices: number[] | null;
  hf_total_hartree: number | null;
  casci_total_hartree: number | null;
  vqe_total_hartree: number | null;
  fci_total_hartree: number | null;
  active_space_error_hartree: number | null;
  solver_error_hartree: number | null;
  total_error_hartree: number | null;
  num_qubits: number | null;
  num_fermionic_terms: number | null;
  num_pauli_terms: number | null;
  ansatz_parameters: number | null;
  circuit_depth: number | null;
  transpiled_depth: number | null;
  one_qubit_gates: number | null;
  two_qubit_gates: number | null;
  optimizer_evaluations: number | null;
  optimizer_iterations: number | null;
  vqe_runtime_seconds: number;
  configuration_runtime_seconds: number;
}

export interface ExperimentResult {
  schema_version: "1";
  experiment_id: string;
  status: "completed" | "partial" | "failed" | "invalid_configuration";
  normalized_config: ExperimentConfig;
  molecule: Record<string, unknown>;
  requested_methods: ChemistryMethod[];
  executed_methods: ChemistryMethod[];
  results: {
    global_references: {
      hartree_fock: Record<string, unknown> & { energy_total_hartree?: number | null };
      fci_full_space: Record<string, unknown> & { energy_total_hartree?: number | null };
    };
    active_spaces: ActiveSpaceResult[];
    summary: Record<string, unknown>;
  };
  comparison_table: ChemistryComparisonRow[];
  timings_seconds: Record<string, number>;
  warnings: StructuredMessage[];
  errors: StructuredMessage[];
  provenance: Record<string, unknown>;
}

export interface ChemistryPipelineStep {
  id: "validate" | "scf" | "active_space" | "mapping" | "vqe" | "comparison";
  label: string;
  status: ChemistryStepStatus;
  message: string | null;
}

export interface ChemistryJob {
  job_id: string;
  status: ChemistryJobStatus;
  progress: number;
  steps: ChemistryPipelineStep[];
  current_active_space: ActiveSpaceConfig | null;
  completed_active_spaces: number;
  total_active_spaces: number;
  result: ExperimentResult | null;
  error: StructuredMessage | StructuredMessage[] | null;
  created_at_utc?: string;
  updated_at_utc?: string;
}

export interface ChemistryJobSubmission {
  job_id: string;
  status: "queued" | "running";
}

export interface ChemistryValidationError {
  code: string;
  field: string;
  message: string;
}
