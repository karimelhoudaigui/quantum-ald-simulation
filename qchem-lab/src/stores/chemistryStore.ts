import { create } from "zustand";

import { CHEMISTRY_STEP_LABELS, MOLECULE_PRESETS } from "../config/chemistry";
import type {
  ActiveSpaceDraft,
  AtomDraft,
  ChemistryJob,
  ChemistryJobSubmission,
  ChemistryMethod,
  ChemistryValidationError,
  CoordinateUnit,
  ExperimentConfig,
  ExperimentResult,
} from "../types/chemistry";

let localId = 0;
const nextId = (prefix: string) => `${prefix}-${++localId}`;
const clearDraftFeedback = () => ({
  validationErrors: [] as ChemistryValidationError[],
  networkError: null,
});

export interface ChemistryState {
  selectedPreset: string;
  moleculeName: string | null;
  atoms: AtomDraft[];
  charge: number;
  spin: number;
  basis: string;
  unit: CoordinateUnit;
  selectedAtomId: string | null;
  activeSpaces: ActiveSpaceDraft[];
  methods: Record<ChemistryMethod, boolean>;
  mapping: "jordan-wigner";
  ansatzType: "uccsd";
  reps: number;
  optimizer: "slsqp";
  maxiter: number;
  executionMode: "exact_statevector";
  job: ChemistryJob | null;
  result: ExperimentResult | null;
  validationErrors: ChemistryValidationError[];
  networkError: string | null;
  setPreset: (preset: string) => void;
  addAtom: () => void;
  updateAtom: (id: string, patch: Partial<Omit<AtomDraft, "id">>) => void;
  removeAtom: (id: string) => void;
  replaceAtoms: (atoms: Omit<AtomDraft, "id">[], name?: string | null) => void;
  selectAtom: (id: string | null) => void;
  setCharge: (charge: number) => void;
  setSpin: (spin: number) => void;
  setBasis: (basis: string) => void;
  setUnit: (unit: CoordinateUnit) => void;
  addActiveSpace: () => void;
  updateActiveSpace: (id: string, patch: Partial<Omit<ActiveSpaceDraft, "id">>) => void;
  removeActiveSpace: (id: string) => void;
  setMethod: (method: ChemistryMethod, enabled: boolean) => void;
  setQuantumConfig: (
    patch: Partial<
      Pick<ChemistryState, "mapping" | "ansatzType" | "reps" | "optimizer" | "maxiter" | "executionMode">
    >,
  ) => void;
  setJob: (job: ChemistryJob | null) => void;
  setResult: (result: ExperimentResult | null) => void;
  setValidationErrors: (errors: ChemistryValidationError[]) => void;
  setNetworkError: (message: string | null) => void;
  reset: () => void;
}

function atomsFromPreset(preset: string): AtomDraft[] {
  return MOLECULE_PRESETS[preset].atoms.map((atom) => ({ ...atom, id: nextId("atom") }));
}

function defaultActiveSpace(orbitals = 2): ActiveSpaceDraft {
  return {
    id: nextId("cas"),
    n_active_electrons: 2,
    n_active_orbitals: orbitals,
    orbital_indices: null,
    selection_mode: "canonical",
    orbitalIndicesInput: "",
  };
}

function initialDraft() {
  return {
    selectedPreset: "lih",
    moleculeName: "LiH",
    atoms: atomsFromPreset("lih"),
    charge: 0,
    spin: 0,
    basis: "sto-3g",
    unit: "angstrom" as CoordinateUnit,
    selectedAtomId: null,
    activeSpaces: [defaultActiveSpace(2), defaultActiveSpace(3)],
    methods: { hf: true, casci: true, fci: true, vqe: true },
    mapping: "jordan-wigner" as const,
    ansatzType: "uccsd" as const,
    reps: 1,
    optimizer: "slsqp" as const,
    maxiter: 100,
    executionMode: "exact_statevector" as const,
    job: null,
    result: null,
    validationErrors: [],
    networkError: null,
  };
}

export const useChemistryStore = create<ChemistryState>((set) => ({
  ...initialDraft(),
  setPreset: (preset) => {
    if (preset === "custom") {
      set({ selectedPreset: "custom", ...clearDraftFeedback() });
      return;
    }
    const definition = MOLECULE_PRESETS[preset];
    if (!definition) return;
    set({
      selectedPreset: preset,
      moleculeName: definition.name,
      atoms: atomsFromPreset(preset),
      selectedAtomId: null,
      ...clearDraftFeedback(),
    });
  },
  addAtom: () =>
    set((state) => ({
      selectedPreset: "custom",
      atoms: [...state.atoms, { id: nextId("atom"), symbol: "H", x: 0, y: 0, z: 0 }],
      ...clearDraftFeedback(),
    })),
  updateAtom: (id, patch) =>
    set((state) => ({
      selectedPreset: "custom",
      atoms: state.atoms.map((atom) => (atom.id === id ? { ...atom, ...patch } : atom)),
      ...clearDraftFeedback(),
    })),
  removeAtom: (id) =>
    set((state) => ({
      selectedPreset: "custom",
      atoms: state.atoms.filter((atom) => atom.id !== id),
      selectedAtomId: state.selectedAtomId === id ? null : state.selectedAtomId,
      ...clearDraftFeedback(),
    })),
  replaceAtoms: (atoms, name = "Imported molecule") =>
    set({
      selectedPreset: "custom",
      moleculeName: name,
      atoms: atoms.map((atom) => ({ ...atom, id: nextId("atom") })),
      selectedAtomId: null,
      ...clearDraftFeedback(),
    }),
  selectAtom: (selectedAtomId) => set({ selectedAtomId }),
  setCharge: (charge) => set({ charge, ...clearDraftFeedback() }),
  setSpin: (spin) => set({ spin, ...clearDraftFeedback() }),
  setBasis: (basis) => set({ basis, ...clearDraftFeedback() }),
  setUnit: (unit) => set({ unit, ...clearDraftFeedback() }),
  addActiveSpace: () =>
    set((state) => ({
      activeSpaces: [...state.activeSpaces, defaultActiveSpace(state.activeSpaces.length + 2)],
      ...clearDraftFeedback(),
    })),
  updateActiveSpace: (id, patch) =>
    set((state) => ({
      activeSpaces: state.activeSpaces.map((activeSpace) =>
        activeSpace.id === id ? { ...activeSpace, ...patch } : activeSpace,
      ),
      ...clearDraftFeedback(),
    })),
  removeActiveSpace: (id) =>
    set((state) => ({
      activeSpaces: state.activeSpaces.filter((activeSpace) => activeSpace.id !== id),
      ...clearDraftFeedback(),
    })),
  setMethod: (method, enabled) =>
    set((state) => {
      const methods = { ...state.methods, [method]: enabled };
      if (method === "vqe" && enabled) methods.casci = true;
      if (method === "casci" && !enabled && methods.vqe) methods.casci = true;
      return { methods, ...clearDraftFeedback() };
    }),
  setQuantumConfig: (patch) => set({ ...patch, ...clearDraftFeedback() }),
  setJob: (job) => set({ job }),
  setResult: (result) => set({ result }),
  setValidationErrors: (validationErrors) => set({ validationErrors }),
  setNetworkError: (networkError) => set({ networkError }),
  reset: () => set(initialDraft()),
}));

function parseManualIndices(activeSpace: ActiveSpaceDraft): number[] | null {
  if (activeSpace.selection_mode !== "manual") return null;
  return activeSpace.orbitalIndicesInput
    .split(",")
    .map((value) => Number(value.trim()))
    .filter((value) => Number.isInteger(value));
}

export function validateChemistryDraft(state: ChemistryState): ChemistryValidationError[] {
  const errors: ChemistryValidationError[] = [];
  if (state.atoms.length === 0) {
    errors.push({ code: "empty_molecule", field: "molecule.atoms", message: "Add at least one atom." });
  }
  state.atoms.forEach((atom, index) => {
    if (!atom.symbol || [atom.x, atom.y, atom.z].some((value) => !Number.isFinite(value))) {
      errors.push({
        code: "invalid_atom",
        field: `molecule.atoms[${index}]`,
        message: "Choose an element and enter finite X, Y and Z coordinates.",
      });
    }
  });
  if (!Number.isInteger(state.charge)) {
    errors.push({ code: "invalid_charge", field: "molecule.charge", message: "Charge must be an integer." });
  }
  if (!Number.isInteger(state.spin) || state.spin < 0) {
    errors.push({ code: "invalid_spin", field: "molecule.spin", message: "Spin must be a non-negative integer." });
  }
  if (!Object.values(state.methods).some(Boolean)) {
    errors.push({ code: "missing_methods", field: "methods", message: "Select at least one method." });
  }
  if ((state.methods.casci || state.methods.vqe) && state.activeSpaces.length === 0) {
    errors.push({ code: "missing_active_space", field: "active_spaces", message: "Add at least one active space." });
  }
  if (state.methods.casci && !state.methods.vqe) {
    errors.push({
      code: "unsupported_method_combination",
      field: "methods",
      message: "CASCI-only execution is not supported by schema 1; enable VQE or disable CASCI.",
    });
  }
  if (state.methods.casci || state.methods.vqe) {
    state.activeSpaces.forEach((activeSpace, index) => {
      const field = `active_spaces[${index}]`;
      if (!Number.isInteger(activeSpace.n_active_electrons) || activeSpace.n_active_electrons <= 0) {
        errors.push({ code: "invalid_active_space", field, message: "Active electrons must be a positive integer." });
      }
      if (!Number.isInteger(activeSpace.n_active_orbitals) || activeSpace.n_active_orbitals <= 0) {
        errors.push({ code: "invalid_active_space", field, message: "Active orbitals must be a positive integer." });
      }
      if (activeSpace.n_active_electrons > 2 * activeSpace.n_active_orbitals) {
        errors.push({
          code: "invalid_active_space",
          field,
          message: `${activeSpace.n_active_electrons} active electrons cannot fit in ${activeSpace.n_active_orbitals} spatial orbitals.`,
        });
      }
      if (activeSpace.selection_mode === "manual") {
        const indices = parseManualIndices(activeSpace) ?? [];
        if (
          indices.length !== activeSpace.n_active_orbitals ||
          new Set(indices).size !== indices.length ||
          indices.some((value) => value < 0)
        ) {
          errors.push({
            code: "invalid_active_space",
            field: `${field}.orbital_indices`,
            message: `Enter ${activeSpace.n_active_orbitals} unique, zero-based orbital indices.`,
          });
        }
      }
    });
  }
  if (state.reps < 1 || !Number.isInteger(state.reps)) {
    errors.push({ code: "invalid_ansatz", field: "ansatz.reps", message: "Ansatz repetitions must be a positive integer." });
  }
  if (state.maxiter < 1 || !Number.isInteger(state.maxiter)) {
    errors.push({ code: "invalid_solver", field: "solver.maxiter", message: "Max iterations must be a positive integer." });
  }
  return errors;
}

export function buildExperimentConfig(state: ChemistryState): ExperimentConfig {
  const methods = (["hf", "casci", "fci", "vqe"] as ChemistryMethod[]).filter(
    (method) => state.methods[method],
  );
  const usesVqe = state.methods.vqe;
  return {
    schema_version: "1",
    molecule: {
      name: state.moleculeName,
      atoms: state.atoms.map(({ id: _id, ...atom }) => atom),
      charge: state.charge,
      spin: state.spin,
      basis: state.basis,
      unit: state.unit,
    },
    active_spaces:
      state.methods.casci || state.methods.vqe
        ? state.activeSpaces.map((activeSpace) => ({
            n_active_electrons: activeSpace.n_active_electrons,
            n_active_orbitals: activeSpace.n_active_orbitals,
            orbital_indices: parseManualIndices(activeSpace),
            selection_mode: activeSpace.selection_mode,
          }))
        : [],
    methods,
    mapping: state.mapping,
    ansatz: usesVqe
      ? {
          ansatz_type: state.ansatzType,
          reps: state.reps,
          preserve_spin: true,
          generalized: false,
          initialization: "zeros",
        }
      : null,
    solver: usesVqe
      ? {
          optimizer: state.optimizer,
          maxiter: state.maxiter,
          tolerance: 1e-9,
          initialization: "ansatz_default",
          random_seeds: [],
          random_scale: 0.05,
          execution_mode: state.executionMode,
        }
      : null,
    execution_mode: state.executionMode,
    chemical_accuracy_hartree: 0.0016,
  };
}

export function chemistryJobFromSubmission(submission: ChemistryJobSubmission): ChemistryJob {
  return {
    job_id: submission.job_id,
    status: submission.status,
    progress: 0,
    steps: CHEMISTRY_STEP_LABELS.map(([id, label]) => ({
      id,
      label,
      status: "pending",
      message: null,
    })),
    current_active_space: null,
    completed_active_spaces: 0,
    total_active_spaces: 0,
    result: null,
    error: null,
  };
}
