import type { IqcpIntegralResult, IqcpScfResult } from "./iqcpClient";
import type {
  ActiveSpaceConfig,
  ActiveSpaceResult,
  ChemistryComparisonRow,
  ExperimentConfig,
  ExperimentResult,
  StructuredMessage,
} from "../types/chemistry";

const ZERO_TOLERANCE = 1e-12;
const MAX_ACTIVE_ORBITALS = 8;
const MAX_CI_DIMENSION = 1200;
const MAX_LANCZOS_VECTORS = 260;

export interface CorrelatedEngineInput {
  experimentId: string;
  config: ExperimentConfig;
  integrals: IqcpIntegralResult;
  scf: IqcpScfResult;
  wasmVersion: string;
  scfRuntimeSeconds: number;
}

export interface CorrelatedProgress {
  step: "active_space" | "mapping" | "vqe" | "comparison";
  progress: number;
  message: string;
  completedActiveSpaces: number;
  totalActiveSpaces: number;
  currentActiveSpace: ActiveSpaceConfig | null;
}

interface MoIntegrals {
  n: number;
  h1: Float64Array;
  eri: Float64Array;
}

interface ActiveProblem extends MoIntegrals {
  nElectrons: number;
  constantEnergy: number;
  active: number[];
  core: number[];
  external: number[];
}

interface FixedSpinHamiltonian {
  matrix: Float64Array;
  basis: number[];
  indexByState: Map<number, number>;
  dimension: number;
  nSpatial: number;
  nElectrons: number;
  nAlpha: number;
  nBeta: number;
  fermionicTerms: number;
}

interface Excitation {
  occupied: number[];
  virtual: number[];
}

interface VqeResult {
  initialEnergy: number;
  energy: number;
  parameters: number[];
  evaluations: number;
  iterations: number;
  converged: boolean;
  runtimeSeconds: number;
  excitationCount: number;
}

export function runBrowserCorrelatedExperiment(
  input: CorrelatedEngineInput,
  onProgress: (progress: CorrelatedProgress) => void = () => undefined,
): ExperimentResult {
  const started = nowSeconds();
  const { config, integrals, scf } = input;
  const matrices = scf.matrices;
  if (!matrices) throw new Error("RHF molecular-orbital matrices are missing.");
  if (integrals.nbf !== matrices.nbf) {
    throw new Error("Integral and RHF basis dimensions are inconsistent.");
  }

  onProgress({
    step: "active_space",
    progress: 38,
    message: "Transforming AO integrals to the molecular-orbital basis",
    completedActiveSpaces: 0,
    totalActiveSpaces: config.active_spaces.length,
    currentActiveSpace: null,
  });
  const mo = transformIntegralsToMo(integrals, matrices.moCoefficients);
  const warnings: StructuredMessage[] = [];
  const errors: StructuredMessage[] = [];

  let fullFciEnergy: number | null = null;
  let fullFciStatus = config.methods.includes("fci") ? "unavailable" : "not_requested";
  let fullFciDimension: number | null = null;
  if (config.methods.includes("fci")) {
    try {
      const fullDimension = fixedSpinDimension(mo.n, integrals.nelec);
      fullFciDimension = fullDimension;
      if (mo.n > MAX_ACTIVE_ORBITALS || fullDimension > MAX_CI_DIMENSION) {
        throw new Error(
          `Full-space FCI dimension ${fullDimension} exceeds the browser limit ${MAX_CI_DIMENSION}.`,
        );
      }
      const fullHamiltonian = buildFixedSpinHamiltonian(
        mo.h1,
        mo.eri,
        mo.n,
        integrals.nelec,
        integrals.eNuc,
      );
      fullFciEnergy = lowestEigenvalue(fullHamiltonian.matrix, fullHamiltonian.dimension);
      fullFciStatus = "completed";
    } catch (error) {
      warnings.push({
        code: "reference_unavailable",
        field: "methods.fci",
        message: errorMessage(error),
      });
    }
  }

  const activeResults: ActiveSpaceResult[] = [];
  const comparisonRows: ChemistryComparisonRow[] = [];
  const totalActive = config.active_spaces.length;
  for (let index = 0; index < totalActive; index += 1) {
    const activeConfig = config.active_spaces[index];
    const configurationStarted = nowSeconds();
    onProgress({
      step: "active_space",
      progress: 42 + (index / Math.max(totalActive, 1)) * 46,
      message: `Preparing CAS(${activeConfig.n_active_electrons},${activeConfig.n_active_orbitals})`,
      completedActiveSpaces: index,
      totalActiveSpaces: totalActive,
      currentActiveSpace: activeConfig,
    });
    try {
      const problem = prepareActiveProblem(mo, integrals, activeConfig);
      const dimension = fixedSpinDimension(problem.n, problem.nElectrons);
      if (dimension > MAX_CI_DIMENSION) {
        throw new Error(
          `CAS(${problem.nElectrons},${problem.n}) dimension ${dimension} exceeds the browser limit ${MAX_CI_DIMENSION}.`,
        );
      }
      const hamiltonian = buildFixedSpinHamiltonian(
        problem.h1,
        problem.eri,
        problem.n,
        problem.nElectrons,
        problem.constantEnergy,
      );
      const casciStarted = nowSeconds();
      const casciEnergy = lowestEigenvalue(hamiltonian.matrix, hamiltonian.dimension);
      const casciSeconds = nowSeconds() - casciStarted;

      onProgress({
        step: "mapping",
        progress: 55 + (index / Math.max(totalActive, 1)) * 34,
        message: `Jordan-Wigner mapping for ${2 * problem.n} qubits`,
        completedActiveSpaces: index,
        totalActiveSpaces: totalActive,
        currentActiveSpace: activeConfig,
      });
      const pauliTerms = countJordanWignerTerms(
        problem.h1,
        problem.eri,
        problem.n,
        problem.constantEnergy,
      );

      let vqe: VqeResult | null = null;
      if (config.methods.includes("vqe")) {
        onProgress({
          step: "vqe",
          progress: 63 + (index / Math.max(totalActive, 1)) * 30,
          message: `Optimizing local UCCSD statevector for CAS(${problem.nElectrons},${problem.n})`,
          completedActiveSpaces: index,
          totalActiveSpaces: totalActive,
          currentActiveSpace: activeConfig,
        });
        vqe = runUccsdVqe(
          hamiltonian,
          config.ansatz?.reps ?? 1,
          config.solver?.maxiter ?? 100,
          config.solver?.tolerance ?? 1e-9,
          casciEnergy,
        );
        if (!vqe.converged) {
          warnings.push({
            code: "vqe_iteration_limit",
            field: `active_spaces[${index}]`,
            configuration_id: configurationId(activeConfig, index),
            message: `Rotosolve reached ${vqe.iterations} iterations; the best variational energy is retained.`,
          });
        }
      }

      const vqeEnergy = vqe?.energy ?? null;
      const activeError = fullFciEnergy === null ? null : casciEnergy - fullFciEnergy;
      const solverError = vqeEnergy === null ? null : vqeEnergy - casciEnergy;
      const totalError =
        vqeEnergy === null || fullFciEnergy === null ? null : vqeEnergy - fullFciEnergy;
      const id = configurationId(activeConfig, index);
      const configurationSeconds = nowSeconds() - configurationStarted;
      const row: ChemistryComparisonRow = {
        configuration_id: id,
        status: "completed",
        selection_mode: activeConfig.selection_mode,
        n_active_electrons: activeConfig.n_active_electrons,
        n_active_orbitals: activeConfig.n_active_orbitals,
        orbital_indices: problem.active,
        hf_total_hartree: scf.energy,
        casci_total_hartree: casciEnergy,
        vqe_total_hartree: vqeEnergy,
        fci_total_hartree: fullFciEnergy,
        active_space_error_hartree: activeError,
        solver_error_hartree: solverError,
        total_error_hartree: totalError,
        num_qubits: 2 * problem.n,
        num_fermionic_terms: hamiltonian.fermionicTerms,
        num_pauli_terms: pauliTerms,
        ansatz_parameters: vqe?.parameters.length ?? null,
        circuit_depth: null,
        transpiled_depth: null,
        one_qubit_gates: null,
        two_qubit_gates: null,
        optimizer_evaluations: vqe?.evaluations ?? null,
        optimizer_iterations: vqe?.iterations ?? null,
        vqe_runtime_seconds: vqe?.runtimeSeconds ?? 0,
        configuration_runtime_seconds: configurationSeconds,
      };
      comparisonRows.push(row);
      activeResults.push({
        configuration_id: id,
        status: "completed",
        message: "Local active-space calculation completed",
        active_space: {
          ...activeConfig,
          resolved_orbital_indices: problem.active,
          frozen_core_orbital_indices: problem.core,
          external_orbital_indices: problem.external,
        },
        energies_hartree: {
          hartree_fock_total: scf.energy,
          casci_total: casciEnergy,
          vqe_initial_total: vqe?.initialEnergy ?? null,
          vqe_total: vqeEnergy,
          fci_full_space_total: fullFciEnergy,
        },
        errors_hartree: {
          active_space: activeError,
          solver: solverError,
          total: totalError,
          decomposition_residual:
            activeError === null || solverError === null || totalError === null
              ? null
              : totalError - activeError - solverError,
        },
        resources: {
          ci_dimension: hamiltonian.dimension,
          num_qubits: 2 * problem.n,
          num_fermionic_terms: hamiltonian.fermionicTerms,
          num_pauli_terms: pauliTerms,
          ansatz_parameters: vqe?.parameters.length ?? null,
          circuit_depth: null,
          transpiled_depth: null,
          one_qubit_gates: null,
          two_qubit_gates: null,
        },
        optimization: {
          optimizer: "periodic_coordinate",
          converged: vqe?.converged ?? false,
          evaluations: vqe?.evaluations ?? null,
          iterations: vqe?.iterations ?? null,
          excitation_count: vqe?.excitationCount ?? null,
        },
        timings_seconds: {
          casci: casciSeconds,
          vqe: vqe?.runtimeSeconds ?? 0,
          total: configurationSeconds,
        },
      });
    } catch (error) {
      const id = configurationId(activeConfig, index);
      const message = errorMessage(error);
      errors.push({
        code: "invalid_active_space",
        field: `active_spaces[${index}]`,
        message,
        configuration_id: id,
      });
      activeResults.push(failedActiveResult(activeConfig, id, message));
      comparisonRows.push(failedComparisonRow(activeConfig, id, scf.energy, fullFciEnergy));
    }
    onProgress({
      step: "active_space",
      progress: 48 + ((index + 1) / Math.max(totalActive, 1)) * 44,
      message: `Completed ${index + 1} of ${totalActive} active spaces`,
      completedActiveSpaces: index + 1,
      totalActiveSpaces: totalActive,
      currentActiveSpace: null,
    });
  }

  onProgress({
    step: "comparison",
    progress: 97,
    message: "Building the local comparison",
    completedActiveSpaces: totalActive,
    totalActiveSpaces: totalActive,
    currentActiveSpace: null,
  });
  const correlatedSeconds = nowSeconds() - started;
  const requestedFciUnavailable = config.methods.includes("fci") && fullFciEnergy === null;
  const status = errors.length > 0 || requestedFciUnavailable ? "partial" : "completed";
  const executedMethods = config.methods.filter((method) => {
    if (method === "hf") return true;
    if (method === "fci") return fullFciEnergy !== null;
    if (method === "casci") return activeResults.some((entry) => entry.energies_hartree.casci_total !== null);
    if (method === "vqe") return activeResults.some((entry) => entry.energies_hartree.vqe_total !== null);
    return false;
  });
  const result: ExperimentResult = {
    schema_version: "1",
    experiment_id: input.experimentId,
    status,
    normalized_config: config,
    molecule: {
      requested: config.molecule,
      runtime: {
        electron_count: integrals.nelec,
        basis_functions: integrals.nbf,
        nuclear_repulsion_hartree: integrals.eNuc,
        scf_iterations: scf.iterations,
        scf_converged: scf.converged,
      },
    },
    requested_methods: config.methods,
    executed_methods: executedMethods,
    results: {
      global_references: {
        hartree_fock: {
          status: "completed",
          energy_total_hartree: scf.energy,
          iterations: scf.iterations,
        },
        fci_full_space: {
          status: fullFciStatus,
          energy_total_hartree: fullFciEnergy,
          ci_dimension: fullFciDimension,
        },
      },
      active_spaces: activeResults,
      summary: {
        requested: totalActive,
        completed: activeResults.filter((entry) => entry.status === "completed").length,
        execution_location: "visitor_device",
      },
    },
    comparison_table: comparisonRows,
    timings_seconds: {
      integral: Number(integrals.metadata.computeTimeMs ?? 0) / 1000,
      shared_scf: input.scfRuntimeSeconds,
      correlated: correlatedSeconds,
      total: input.scfRuntimeSeconds + correlatedSeconds,
    },
    warnings,
    errors,
    provenance: {
      execution_location: "visitor_device",
      runtime: "Web Worker + WebAssembly",
      integral_scf_engine: "IQCP qc-wasm",
      integral_scf_engine_version: input.wasmVersion,
      correlated_engine: "Q-CHEM Lab browser engine",
      mo_coefficient_layout: "column-major",
      spin_orbital_order: "interleaved_alpha_beta",
      mapping: "Jordan-Wigner",
      vqe_evaluator: "fixed-particle exact statevector",
      optimizer: "periodic_coordinate",
      ansatz: "first-order product UCCSD",
      network_compute: false,
    },
  };
  return result;
}

export function transformIntegralsToMo(
  integrals: Pick<IqcpIntegralResult, "nbf" | "hCore" | "eriCompressed">,
  coefficientsColumnMajor: number[],
): MoIntegrals {
  const n = integrals.nbf;
  if (coefficientsColumnMajor.length !== n * n) {
    throw new Error(`Expected ${n * n} MO coefficients, received ${coefficientsColumnMajor.length}.`);
  }
  const h1 = new Float64Array(n * n);
  for (let p = 0; p < n; p += 1) {
    for (let q = 0; q < n; q += 1) {
      let value = 0;
      for (let mu = 0; mu < n; mu += 1) {
        const cMuP = coefficientsColumnMajor[mu + p * n];
        for (let nu = 0; nu < n; nu += 1) {
          value += cMuP * integrals.hCore[mu * n + nu] * coefficientsColumnMajor[nu + q * n];
        }
      }
      h1[p * n + q] = value;
    }
  }

  const size = n ** 4;
  let source = new Float64Array(size);
  for (let p = 0; p < n; p += 1) {
    for (let nu = 0; nu < n; nu += 1) {
      for (let kappa = 0; kappa < n; kappa += 1) {
        for (let lambda = 0; lambda < n; lambda += 1) {
          let value = 0;
          for (let mu = 0; mu < n; mu += 1) {
            value +=
              coefficientsColumnMajor[mu + p * n] *
              eriCompressedGet(integrals.eriCompressed, mu, nu, kappa, lambda);
          }
          source[index4(p, nu, kappa, lambda, n)] = value;
        }
      }
    }
  }

  let target = new Float64Array(size);
  for (let p = 0; p < n; p += 1) {
    for (let q = 0; q < n; q += 1) {
      for (let kappa = 0; kappa < n; kappa += 1) {
        for (let lambda = 0; lambda < n; lambda += 1) {
          let value = 0;
          for (let nu = 0; nu < n; nu += 1) {
            value += coefficientsColumnMajor[nu + q * n] * source[index4(p, nu, kappa, lambda, n)];
          }
          target[index4(p, q, kappa, lambda, n)] = value;
        }
      }
    }
  }

  source = target;
  target = new Float64Array(size);
  for (let p = 0; p < n; p += 1) {
    for (let q = 0; q < n; q += 1) {
      for (let r = 0; r < n; r += 1) {
        for (let lambda = 0; lambda < n; lambda += 1) {
          let value = 0;
          for (let kappa = 0; kappa < n; kappa += 1) {
            value += coefficientsColumnMajor[kappa + r * n] * source[index4(p, q, kappa, lambda, n)];
          }
          target[index4(p, q, r, lambda, n)] = value;
        }
      }
    }
  }

  source = target;
  target = new Float64Array(size);
  for (let p = 0; p < n; p += 1) {
    for (let q = 0; q < n; q += 1) {
      for (let r = 0; r < n; r += 1) {
        for (let s = 0; s < n; s += 1) {
          let value = 0;
          for (let lambda = 0; lambda < n; lambda += 1) {
            value += coefficientsColumnMajor[lambda + s * n] * source[index4(p, q, r, lambda, n)];
          }
          target[index4(p, q, r, s, n)] = value;
        }
      }
    }
  }
  return { n, h1, eri: target };
}

function prepareActiveProblem(
  mo: MoIntegrals,
  integrals: IqcpIntegralResult,
  config: ActiveSpaceConfig,
): ActiveProblem {
  const nElectrons = config.n_active_electrons;
  const nActive = config.n_active_orbitals;
  if (nActive > MAX_ACTIVE_ORBITALS) {
    throw new Error(`At most ${MAX_ACTIVE_ORBITALS} active orbitals can be simulated locally.`);
  }
  if (nElectrons > integrals.nelec || (integrals.nelec - nElectrons) % 2 !== 0) {
    throw new Error("Active electrons must be compatible with the neutral closed-shell reference.");
  }
  if (nElectrons % 2 !== 0) {
    throw new Error("The local spin-preserving UCCSD engine requires an even active-electron count.");
  }
  const nCore = (integrals.nelec - nElectrons) / 2;
  const nOccupied = integrals.nelec / 2;
  const active =
    config.selection_mode === "manual"
      ? [...(config.orbital_indices ?? [])]
      : Array.from({ length: nActive }, (_, offset) => nCore + offset);
  if (active.length !== nActive || new Set(active).size !== active.length) {
    throw new Error(`CAS(${nElectrons},${nActive}) requires ${nActive} unique orbital indices.`);
  }
  if (active.some((orbital) => orbital < 0 || orbital >= mo.n)) {
    throw new Error(`An active orbital is outside the available range 0-${mo.n - 1}.`);
  }
  const activeOccupied = active.filter((orbital) => orbital < nOccupied).length;
  if (activeOccupied !== nElectrons / 2) {
    throw new Error(
      `The selected orbitals contain ${activeOccupied} occupied orbitals; ${nElectrons / 2} are required.`,
    );
  }
  const remaining = Array.from({ length: mo.n }, (_, orbital) => orbital).filter(
    (orbital) => !active.includes(orbital),
  );
  const core = remaining.slice(0, nCore);
  if (core.some((orbital) => orbital >= nOccupied)) {
    throw new Error("The manual active-space selection leaves a virtual orbital in the frozen core.");
  }
  const external = remaining.slice(nCore);

  const h1 = new Float64Array(nActive * nActive);
  const eri = new Float64Array(nActive ** 4);
  for (let p = 0; p < nActive; p += 1) {
    for (let q = 0; q < nActive; q += 1) {
      const moP = active[p];
      const moQ = active[q];
      let value = mo.h1[moP * mo.n + moQ];
      for (const orbital of core) {
        value +=
          2 * mo.eri[index4(moP, moQ, orbital, orbital, mo.n)] -
          mo.eri[index4(moP, orbital, orbital, moQ, mo.n)];
      }
      h1[p * nActive + q] = value;
      for (let r = 0; r < nActive; r += 1) {
        for (let s = 0; s < nActive; s += 1) {
          eri[index4(p, q, r, s, nActive)] =
            mo.eri[index4(moP, moQ, active[r], active[s], mo.n)];
        }
      }
    }
  }
  let constantEnergy = integrals.eNuc;
  for (const i of core) {
    constantEnergy += 2 * mo.h1[i * mo.n + i];
    for (const j of core) {
      constantEnergy +=
        2 * mo.eri[index4(i, i, j, j, mo.n)] - mo.eri[index4(i, j, j, i, mo.n)];
    }
  }
  return {
    n: nActive,
    h1,
    eri,
    nElectrons,
    constantEnergy,
    active,
    core,
    external,
  };
}

export function buildFixedSpinHamiltonian(
  h1: Float64Array,
  eri: Float64Array,
  nSpatial: number,
  nElectrons: number,
  constantEnergy = 0,
): FixedSpinHamiltonian {
  if (nElectrons % 2 !== 0) throw new Error("Only closed-shell fixed-spin sectors are supported.");
  if (2 * nSpatial >= 30) throw new Error("This browser statevector is limited to 28 spin orbitals.");
  const nAlpha = nElectrons / 2;
  const nBeta = nElectrons / 2;
  if (nAlpha > nSpatial) throw new Error("The active space has too few orbitals for its electrons.");
  const basis = fixedSpinBasis(nSpatial, nAlpha, nBeta);
  const dimension = basis.length;
  const indexByState = new Map(basis.map((state, index) => [state, index]));
  const matrix = new Float64Array(dimension * dimension);
  let oneBodyTerms = 0;
  let twoBodyTerms = 0;

  for (let p = 0; p < nSpatial; p += 1) {
    for (let q = 0; q < nSpatial; q += 1) {
      const coefficient = h1[p * nSpatial + q];
      if (Math.abs(coefficient) < ZERO_TOLERANCE) continue;
      oneBodyTerms += 2;
      for (const spin of [0, 1]) {
        const P = 2 * p + spin;
        const Q = 2 * q + spin;
        for (let column = 0; column < dimension; column += 1) {
          const applied = applyOneBody(basis[column], P, Q);
          if (!applied) continue;
          const row = indexByState.get(applied.state);
          if (row !== undefined) matrix[row * dimension + column] += coefficient * applied.sign;
        }
      }
    }
  }

  for (let p = 0; p < nSpatial; p += 1) {
    for (let r = 0; r < nSpatial; r += 1) {
      for (let q = 0; q < nSpatial; q += 1) {
        for (let s = 0; s < nSpatial; s += 1) {
          const coefficient = 0.5 * eri[index4(p, r, q, s, nSpatial)];
          if (Math.abs(coefficient) < ZERO_TOLERANCE) continue;
          for (const spinP of [0, 1]) {
            for (const spinQ of [0, 1]) {
              const P = 2 * p + spinP;
              const Q = 2 * q + spinQ;
              const R = 2 * r + spinP;
              const S = 2 * s + spinQ;
              twoBodyTerms += 1;
              for (let column = 0; column < dimension; column += 1) {
                const applied = applyTwoBody(basis[column], P, Q, R, S);
                if (!applied) continue;
                const row = indexByState.get(applied.state);
                if (row !== undefined) {
                  matrix[row * dimension + column] += coefficient * applied.sign;
                }
              }
            }
          }
        }
      }
    }
  }

  for (let index = 0; index < dimension; index += 1) {
    matrix[index * dimension + index] += constantEnergy;
  }
  for (let row = 0; row < dimension; row += 1) {
    for (let column = row + 1; column < dimension; column += 1) {
      const average =
        0.5 * (matrix[row * dimension + column] + matrix[column * dimension + row]);
      matrix[row * dimension + column] = average;
      matrix[column * dimension + row] = average;
    }
  }
  return {
    matrix,
    basis,
    indexByState,
    dimension,
    nSpatial,
    nElectrons,
    nAlpha,
    nBeta,
    fermionicTerms: oneBodyTerms + twoBodyTerms,
  };
}

function runUccsdVqe(
  hamiltonian: FixedSpinHamiltonian,
  reps: number,
  maxIterations: number,
  tolerance: number,
  targetEnergy: number,
): VqeResult {
  const started = nowSeconds();
  const excitations = uccsdExcitations(
    hamiltonian.nSpatial,
    hamiltonian.nAlpha,
    hamiltonian.nBeta,
  );
  const sequence = Array.from({ length: reps }, () => excitations).flat();
  const reference = referenceState(hamiltonian.nAlpha, hamiltonian.nBeta);
  const referenceIndex = hamiltonian.indexByState.get(reference);
  if (referenceIndex === undefined) throw new Error("The Hartree-Fock reference is not in the CI basis.");

  const objective = (parameters: number[]) => {
    const state = new Float64Array(hamiltonian.dimension);
    state[referenceIndex] = 1;
    for (let index = 0; index < sequence.length; index += 1) {
      applyExcitationRotation(
        state,
        hamiltonian.basis,
        hamiltonian.indexByState,
        sequence[index],
        parameters[index],
      );
    }
    return expectationValue(hamiltonian.matrix, state);
  };

  const convergenceTolerance = Math.min(tolerance, 1e-12);
  const targetTolerance = Math.min(tolerance, 1e-10);
  const starts: number[][] = [new Array(sequence.length).fill(0) as number[]];
  if (sequence.length > 0 && hamiltonian.dimension <= 128) {
    for (const scaleValue of [0.15, 0.5, 1]) {
      starts.push(
        Array.from(
          { length: sequence.length },
          (_, index) => scaleValue * Math.sin((index + 1) * (scaleValue + 1) * 1.61803398875),
        ),
      );
    }
  }

  let totalEvaluations = 0;
  let best: ReturnType<typeof optimize> | null = null;
  let zeroInitialEnergy = 0;
  for (let startIndex = 0; startIndex < starts.length; startIndex += 1) {
    const candidate = optimize(starts[startIndex]);
    totalEvaluations += candidate.evaluations;
    if (startIndex === 0) zeroInitialEnergy = candidate.initialEnergy;
    if (!best || candidate.energy < best.energy) best = candidate;
    if (best.energy - targetEnergy <= targetTolerance) break;
  }
  if (!best) throw new Error("The local VQE optimizer did not produce a candidate.");
  return {
    initialEnergy: zeroInitialEnergy,
    energy: best.energy,
    parameters: best.parameters,
    evaluations: totalEvaluations,
    iterations: best.iterations,
    converged: best.converged || best.energy - targetEnergy <= targetTolerance,
    runtimeSeconds: nowSeconds() - started,
    excitationCount: excitations.length,
  };

  function optimize(initialParameters: number[]) {
    const parameters = [...initialParameters];
    let evaluations = 0;
    const evaluate = () => {
      evaluations += 1;
      return objective(parameters);
    };
    const initialEnergy = evaluate();
    let energy = initialEnergy;
    let converged = sequence.length === 0;
    let iterations = 0;
    for (
      let iteration = 1;
      iteration <= Math.max(1, maxIterations) && sequence.length > 0;
      iteration += 1
    ) {
      const previous = energy;
      for (let coordinate = 0; coordinate < parameters.length; coordinate += 1) {
        energy = minimizePeriodicCoordinate(
          parameters,
          coordinate,
          evaluate,
          hamiltonian.dimension <= 128 ? 12 : 6,
          hamiltonian.dimension <= 128 ? 18 : 8,
        );
      }
      iterations = iteration;
      energy = evaluate();
      if (
        energy - targetEnergy <= targetTolerance ||
        Math.abs(previous - energy) <= convergenceTolerance
      ) {
        converged = true;
        break;
      }
    }
    return { initialEnergy, energy, parameters, evaluations, iterations, converged };
  }
}

function minimizePeriodicCoordinate(
  parameters: number[],
  coordinate: number,
  evaluate: () => number,
  sampleCount: number,
  refinementSteps: number,
) {
  const spacing = (2 * Math.PI) / sampleCount;
  let bestAngle = parameters[coordinate];
  let bestEnergy = evaluate();
  for (let sample = 0; sample < sampleCount; sample += 1) {
    const angle = -Math.PI + sample * spacing;
    parameters[coordinate] = angle;
    const energy = evaluate();
    if (energy < bestEnergy) {
      bestEnergy = energy;
      bestAngle = angle;
    }
  }

  let left = bestAngle - spacing;
  let right = bestAngle + spacing;
  const inversePhi = (Math.sqrt(5) - 1) / 2;
  let middleLeft = right - inversePhi * (right - left);
  let middleRight = left + inversePhi * (right - left);
  parameters[coordinate] = middleLeft;
  let energyLeft = evaluate();
  parameters[coordinate] = middleRight;
  let energyRight = evaluate();
  for (let iteration = 0; iteration < refinementSteps; iteration += 1) {
    if (energyLeft <= energyRight) {
      right = middleRight;
      middleRight = middleLeft;
      energyRight = energyLeft;
      middleLeft = right - inversePhi * (right - left);
      parameters[coordinate] = middleLeft;
      energyLeft = evaluate();
    } else {
      left = middleLeft;
      middleLeft = middleRight;
      energyLeft = energyRight;
      middleRight = left + inversePhi * (right - left);
      parameters[coordinate] = middleRight;
      energyRight = evaluate();
    }
  }
  if (energyLeft < bestEnergy) {
    bestEnergy = energyLeft;
    bestAngle = middleLeft;
  }
  if (energyRight < bestEnergy) {
    bestEnergy = energyRight;
    bestAngle = middleRight;
  }
  parameters[coordinate] = bestAngle;
  return bestEnergy;
}

function uccsdExcitations(nSpatial: number, nAlpha: number, nBeta: number): Excitation[] {
  const occupiedAlpha = Array.from({ length: nAlpha }, (_, index) => 2 * index);
  const occupiedBeta = Array.from({ length: nBeta }, (_, index) => 2 * index + 1);
  const virtualAlpha = Array.from(
    { length: nSpatial - nAlpha },
    (_, index) => 2 * (nAlpha + index),
  );
  const virtualBeta = Array.from(
    { length: nSpatial - nBeta },
    (_, index) => 2 * (nBeta + index) + 1,
  );
  const excitations: Excitation[] = [];
  for (const occupied of occupiedAlpha) {
    for (const virtual of virtualAlpha) excitations.push({ occupied: [occupied], virtual: [virtual] });
  }
  for (const occupied of occupiedBeta) {
    for (const virtual of virtualBeta) excitations.push({ occupied: [occupied], virtual: [virtual] });
  }
  for (const occupied of combinations(occupiedAlpha, 2)) {
    for (const virtual of combinations(virtualAlpha, 2)) excitations.push({ occupied, virtual });
  }
  for (const occupied of combinations(occupiedBeta, 2)) {
    for (const virtual of combinations(virtualBeta, 2)) excitations.push({ occupied, virtual });
  }
  for (const occupiedA of occupiedAlpha) {
    for (const occupiedB of occupiedBeta) {
      for (const virtualA of virtualAlpha) {
        for (const virtualB of virtualBeta) {
          excitations.push({
            occupied: [occupiedA, occupiedB],
            virtual: [virtualA, virtualB],
          });
        }
      }
    }
  }
  return excitations;
}

function applyExcitationRotation(
  amplitudes: Float64Array,
  basis: number[],
  indexByState: Map<number, number>,
  excitation: Excitation,
  theta: number,
) {
  if (Math.abs(theta) < 1e-15) return;
  const cosine = Math.cos(theta);
  const sine = Math.sin(theta);
  const occupiedMask = excitation.occupied.reduce((mask, orbital) => mask | (1 << orbital), 0);
  const virtualMask = excitation.virtual.reduce((mask, orbital) => mask | (1 << orbital), 0);
  for (let sourceIndex = 0; sourceIndex < basis.length; sourceIndex += 1) {
    const source = basis[sourceIndex];
    if ((source & occupiedMask) !== occupiedMask || (source & virtualMask) !== 0) continue;
    const applied = applyExcitation(source, excitation);
    if (!applied) continue;
    const targetIndex = indexByState.get(applied.state);
    if (targetIndex === undefined) continue;
    const sourceAmplitude = amplitudes[sourceIndex];
    const targetAmplitude = amplitudes[targetIndex];
    amplitudes[sourceIndex] = cosine * sourceAmplitude - applied.sign * sine * targetAmplitude;
    amplitudes[targetIndex] = applied.sign * sine * sourceAmplitude + cosine * targetAmplitude;
  }
}

function applyExcitation(state: number, excitation: Excitation) {
  let current = state;
  let sign = 1;
  for (const orbital of excitation.occupied) {
    const result = annihilate(current, orbital);
    if (!result) return null;
    current = result.state;
    sign *= result.sign;
  }
  for (const orbital of [...excitation.virtual].reverse()) {
    const result = create(current, orbital);
    if (!result) return null;
    current = result.state;
    sign *= result.sign;
  }
  return { state: current, sign };
}

function expectationValue(matrix: Float64Array, state: Float64Array) {
  const dimension = state.length;
  let energy = 0;
  for (let row = 0; row < dimension; row += 1) {
    let product = 0;
    const offset = row * dimension;
    for (let column = 0; column < dimension; column += 1) {
      product += matrix[offset + column] * state[column];
    }
    energy += state[row] * product;
  }
  return energy;
}

export function lowestEigenvalue(matrix: Float64Array, dimension: number) {
  if (dimension === 0) throw new Error("Cannot diagonalize an empty Hamiltonian.");
  if (dimension === 1) return matrix[0];
  const maxVectors = Math.min(dimension, MAX_LANCZOS_VECTORS);
  let vector = new Float64Array(dimension);
  for (let index = 0; index < dimension; index += 1) {
    vector[index] = Math.sin((index + 1) * 1.61803398875) + 0.25 * Math.cos((index + 1) * 0.731);
  }
  normalize(vector);
  const vectors: Float64Array[] = [vector];
  let previous: Float64Array | null = null;
  let previousBeta = 0;
  const diagonal: number[] = [];
  const offDiagonal: number[] = [];

  for (let iteration = 0; iteration < maxVectors; iteration += 1) {
    const product = matrixVectorProduct(matrix, vector);
    if (previous) addScaled(product, previous, -previousBeta);
    const alpha = dot(vector, product);
    addScaled(product, vector, -alpha);
    for (let pass = 0; pass < 2; pass += 1) {
      for (const existing of vectors) addScaled(product, existing, -dot(existing, product));
    }
    const beta = norm(product);
    diagonal.push(alpha);
    if (beta < 1e-13 || iteration === maxVectors - 1) break;
    offDiagonal.push(beta);
    previous = vector;
    previousBeta = beta;
    vector = product;
    scale(vector, 1 / beta);
    vectors.push(vector);
  }
  return smallestTridiagonalEigenvalue(diagonal, offDiagonal);
}

function smallestTridiagonalEigenvalue(diagonal: number[], offDiagonal: number[]) {
  let lower = Number.POSITIVE_INFINITY;
  let upper = Number.NEGATIVE_INFINITY;
  for (let index = 0; index < diagonal.length; index += 1) {
    const radius =
      (index > 0 ? Math.abs(offDiagonal[index - 1]) : 0) +
      (index < offDiagonal.length ? Math.abs(offDiagonal[index]) : 0);
    lower = Math.min(lower, diagonal[index] - radius);
    upper = Math.max(upper, diagonal[index] + radius);
  }
  const sturmCount = (value: number) => {
    let count = 0;
    let pivot = diagonal[0] - value;
    if (pivot < 0) count += 1;
    for (let index = 1; index < diagonal.length; index += 1) {
      if (Math.abs(pivot) < 1e-18) pivot = pivot < 0 ? -1e-18 : 1e-18;
      pivot = diagonal[index] - value - offDiagonal[index - 1] ** 2 / pivot;
      if (pivot < 0) count += 1;
    }
    return count;
  };
  for (let iteration = 0; iteration < 100; iteration += 1) {
    const midpoint = 0.5 * (lower + upper);
    if (sturmCount(midpoint) >= 1) upper = midpoint;
    else lower = midpoint;
  }
  return 0.5 * (lower + upper);
}

function countJordanWignerTerms(
  h1: Float64Array,
  eri: Float64Array,
  nSpatial: number,
  constantEnergy: number,
) {
  const nSpin = 2 * nSpatial;
  const terms = new Map<string, Complex>();
  addPauli(terms, "I".repeat(nSpin), { re: constantEnergy, im: 0 });
  for (let p = 0; p < nSpatial; p += 1) {
    for (let q = 0; q < nSpatial; q += 1) {
      const coefficient = h1[p * nSpatial + q];
      if (Math.abs(coefficient) < ZERO_TOLERANCE) continue;
      for (const spin of [0, 1]) {
        addFermionMonomial(
          terms,
          [
            { orbital: 2 * p + spin, creation: true },
            { orbital: 2 * q + spin, creation: false },
          ],
          coefficient,
          nSpin,
        );
      }
    }
  }
  for (let p = 0; p < nSpatial; p += 1) {
    for (let r = 0; r < nSpatial; r += 1) {
      for (let q = 0; q < nSpatial; q += 1) {
        for (let s = 0; s < nSpatial; s += 1) {
          const coefficient = 0.5 * eri[index4(p, r, q, s, nSpatial)];
          if (Math.abs(coefficient) < ZERO_TOLERANCE) continue;
          for (const spinP of [0, 1]) {
            for (const spinQ of [0, 1]) {
              addFermionMonomial(
                terms,
                [
                  { orbital: 2 * p + spinP, creation: true },
                  { orbital: 2 * q + spinQ, creation: true },
                  { orbital: 2 * s + spinQ, creation: false },
                  { orbital: 2 * r + spinP, creation: false },
                ],
                coefficient,
                nSpin,
              );
            }
          }
        }
      }
    }
  }
  return [...terms.values()].filter((coefficient) => Math.hypot(coefficient.re, coefficient.im) > 1e-10)
    .length;
}

interface Complex {
  re: number;
  im: number;
}

interface FermionOperator {
  orbital: number;
  creation: boolean;
}

function addFermionMonomial(
  destination: Map<string, Complex>,
  operators: FermionOperator[],
  coefficient: number,
  nSpin: number,
) {
  let expansion = new Map<string, Complex>([["I".repeat(nSpin), { re: coefficient, im: 0 }]]);
  for (const operator of operators) {
    const local = jordanWignerLadder(operator.orbital, operator.creation, nSpin);
    const next = new Map<string, Complex>();
    for (const [left, leftCoefficient] of expansion) {
      for (const [right, rightCoefficient] of local) {
        const product = multiplyPauliStrings(left, right);
        const combined = multiplyComplex(multiplyComplex(leftCoefficient, rightCoefficient), product.phase);
        addPauli(next, product.pauli, combined);
      }
    }
    expansion = next;
  }
  for (const [pauli, value] of expansion) addPauli(destination, pauli, value);
}

function jordanWignerLadder(orbital: number, creation: boolean, nSpin: number) {
  const x = new Array(nSpin).fill("I") as string[];
  const y = new Array(nSpin).fill("I") as string[];
  for (let index = 0; index < orbital; index += 1) {
    x[index] = "Z";
    y[index] = "Z";
  }
  x[orbital] = "X";
  y[orbital] = "Y";
  return new Map<string, Complex>([
    [x.join(""), { re: 0.5, im: 0 }],
    [y.join(""), { re: 0, im: creation ? -0.5 : 0.5 }],
  ]);
}

function multiplyPauliStrings(left: string, right: string) {
  let phase: Complex = { re: 1, im: 0 };
  const result: string[] = [];
  for (let index = 0; index < left.length; index += 1) {
    const product = multiplySinglePauli(left[index], right[index]);
    result.push(product.pauli);
    phase = multiplyComplex(phase, product.phase);
  }
  return { pauli: result.join(""), phase };
}

function multiplySinglePauli(left: string, right: string) {
  if (left === "I") return { pauli: right, phase: { re: 1, im: 0 } };
  if (right === "I") return { pauli: left, phase: { re: 1, im: 0 } };
  if (left === right) return { pauli: "I", phase: { re: 1, im: 0 } };
  const positive: Record<string, string> = { XY: "Z", YZ: "X", ZX: "Y" };
  const key = `${left}${right}`;
  if (positive[key]) return { pauli: positive[key], phase: { re: 0, im: 1 } };
  return { pauli: positive[`${right}${left}`], phase: { re: 0, im: -1 } };
}

function multiplyComplex(left: Complex, right: Complex): Complex {
  return {
    re: left.re * right.re - left.im * right.im,
    im: left.re * right.im + left.im * right.re,
  };
}

function addPauli(destination: Map<string, Complex>, pauli: string, value: Complex) {
  const current = destination.get(pauli) ?? { re: 0, im: 0 };
  destination.set(pauli, { re: current.re + value.re, im: current.im + value.im });
}

function fixedSpinBasis(nSpatial: number, nAlpha: number, nBeta: number) {
  const alphaMasks = combinationMasks(nSpatial, nAlpha);
  const betaMasks = combinationMasks(nSpatial, nBeta);
  const basis: number[] = [];
  for (const alpha of alphaMasks) {
    for (const beta of betaMasks) {
      let state = 0;
      for (let orbital = 0; orbital < nSpatial; orbital += 1) {
        if (alpha & (1 << orbital)) state |= 1 << (2 * orbital);
        if (beta & (1 << orbital)) state |= 1 << (2 * orbital + 1);
      }
      basis.push(state);
    }
  }
  return basis;
}

function combinationMasks(n: number, k: number) {
  const masks: number[] = [];
  const visit = (start: number, remaining: number, mask: number) => {
    if (remaining === 0) {
      masks.push(mask);
      return;
    }
    for (let index = start; index <= n - remaining; index += 1) {
      visit(index + 1, remaining - 1, mask | (1 << index));
    }
  };
  visit(0, k, 0);
  return masks;
}

function combinations(values: number[], size: number) {
  const output: number[][] = [];
  const visit = (start: number, current: number[]) => {
    if (current.length === size) {
      output.push([...current]);
      return;
    }
    for (let index = start; index <= values.length - (size - current.length); index += 1) {
      current.push(values[index]);
      visit(index + 1, current);
      current.pop();
    }
  };
  visit(0, []);
  return output;
}

function referenceState(nAlpha: number, nBeta: number) {
  let state = 0;
  for (let orbital = 0; orbital < nAlpha; orbital += 1) state |= 1 << (2 * orbital);
  for (let orbital = 0; orbital < nBeta; orbital += 1) state |= 1 << (2 * orbital + 1);
  return state;
}

function applyOneBody(state: number, p: number, q: number) {
  const removed = annihilate(state, q);
  if (!removed) return null;
  const added = create(removed.state, p);
  if (!added) return null;
  return { state: added.state, sign: removed.sign * added.sign };
}

function applyTwoBody(state: number, p: number, q: number, r: number, s: number) {
  const first = annihilate(state, r);
  if (!first) return null;
  const second = annihilate(first.state, s);
  if (!second) return null;
  const third = create(second.state, q);
  if (!third) return null;
  const fourth = create(third.state, p);
  if (!fourth) return null;
  return {
    state: fourth.state,
    sign: first.sign * second.sign * third.sign * fourth.sign,
  };
}

function annihilate(state: number, orbital: number) {
  if (((state >>> orbital) & 1) === 0) return null;
  const sign = popcount(state & ((1 << orbital) - 1)) % 2 === 0 ? 1 : -1;
  return { state: state & ~(1 << orbital), sign };
}

function create(state: number, orbital: number) {
  if (((state >>> orbital) & 1) === 1) return null;
  const sign = popcount(state & ((1 << orbital) - 1)) % 2 === 0 ? 1 : -1;
  return { state: state | (1 << orbital), sign };
}

function popcount(value: number) {
  let remaining = value >>> 0;
  let count = 0;
  while (remaining) {
    remaining &= remaining - 1;
    count += 1;
  }
  return count;
}

function fixedSpinDimension(nSpatial: number, nElectrons: number) {
  if (nElectrons % 2 !== 0) throw new Error("Full-space FCI requires a closed-shell molecule.");
  const occupied = nElectrons / 2;
  return binomial(nSpatial, occupied) ** 2;
}

function binomial(n: number, k: number) {
  if (k < 0 || k > n) return 0;
  let result = 1;
  for (let index = 1; index <= Math.min(k, n - k); index += 1) {
    result = (result * (n - index + 1)) / index;
  }
  return Math.round(result);
}

function eriCompressedGet(eri: number[], i: number, j: number, k: number, l: number) {
  const pairA = pairIndex(i, j);
  const pairB = pairIndex(k, l);
  const high = Math.max(pairA, pairB);
  const low = Math.min(pairA, pairB);
  return eri[(high * (high + 1)) / 2 + low];
}

function pairIndex(i: number, j: number) {
  const high = Math.max(i, j);
  const low = Math.min(i, j);
  return (high * (high + 1)) / 2 + low;
}

function index4(a: number, b: number, c: number, d: number, n: number) {
  return ((a * n + b) * n + c) * n + d;
}

function matrixVectorProduct(matrix: Float64Array, vector: Float64Array) {
  const dimension = vector.length;
  const result = new Float64Array(dimension);
  for (let row = 0; row < dimension; row += 1) {
    let value = 0;
    const offset = row * dimension;
    for (let column = 0; column < dimension; column += 1) value += matrix[offset + column] * vector[column];
    result[row] = value;
  }
  return result;
}

function dot(left: Float64Array, right: Float64Array) {
  let result = 0;
  for (let index = 0; index < left.length; index += 1) result += left[index] * right[index];
  return result;
}

function norm(vector: Float64Array) {
  return Math.sqrt(dot(vector, vector));
}

function normalize(vector: Float64Array) {
  const length = norm(vector);
  if (length === 0) throw new Error("Cannot normalize a zero vector.");
  scale(vector, 1 / length);
}

function scale(vector: Float64Array, factor: number) {
  for (let index = 0; index < vector.length; index += 1) vector[index] *= factor;
}

function addScaled(target: Float64Array, source: Float64Array, factor: number) {
  for (let index = 0; index < target.length; index += 1) target[index] += factor * source[index];
}

function configurationId(config: ActiveSpaceConfig, index: number) {
  const orbitals = config.orbital_indices?.join("-") ?? "canonical";
  return `local_cas_${config.n_active_electrons}_${config.n_active_orbitals}_${orbitals}_${index + 1}`;
}

function failedActiveResult(
  config: ActiveSpaceConfig,
  configurationIdValue: string,
  message: string,
): ActiveSpaceResult {
  return {
    configuration_id: configurationIdValue,
    status: "invalid_configuration",
    message,
    active_space: config,
    energies_hartree: {
      hartree_fock_total: null,
      casci_total: null,
      vqe_initial_total: null,
      vqe_total: null,
      fci_full_space_total: null,
    },
    errors_hartree: {
      active_space: null,
      solver: null,
      total: null,
      decomposition_residual: null,
    },
    resources: {},
    optimization: {},
    timings_seconds: { total: 0 },
  };
}

function failedComparisonRow(
  config: ActiveSpaceConfig,
  configurationIdValue: string,
  hfEnergy: number,
  fciEnergy: number | null,
): ChemistryComparisonRow {
  return {
    configuration_id: configurationIdValue,
    status: "invalid_configuration",
    selection_mode: config.selection_mode,
    n_active_electrons: config.n_active_electrons,
    n_active_orbitals: config.n_active_orbitals,
    orbital_indices: config.orbital_indices,
    hf_total_hartree: hfEnergy,
    casci_total_hartree: null,
    vqe_total_hartree: null,
    fci_total_hartree: fciEnergy,
    active_space_error_hartree: null,
    solver_error_hartree: null,
    total_error_hartree: null,
    num_qubits: 2 * config.n_active_orbitals,
    num_fermionic_terms: null,
    num_pauli_terms: null,
    ansatz_parameters: null,
    circuit_depth: null,
    transpiled_depth: null,
    one_qubit_gates: null,
    two_qubit_gates: null,
    optimizer_evaluations: null,
    optimizer_iterations: null,
    vqe_runtime_seconds: 0,
    configuration_runtime_seconds: 0,
  };
}

function nowSeconds() {
  return (typeof performance === "undefined" ? Date.now() : performance.now()) / 1000;
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}
