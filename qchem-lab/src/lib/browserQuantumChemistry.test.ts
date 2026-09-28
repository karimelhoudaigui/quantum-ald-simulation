import { describe, expect, it } from "vitest";

import {
  buildFixedSpinHamiltonian,
  runBrowserCorrelatedExperiment,
  transformIntegralsToMo,
} from "./browserQuantumChemistry";
import type { IqcpIntegralResult, IqcpScfResult } from "./iqcpClient";
import type { ExperimentConfig } from "../types/chemistry";

describe("browser quantum chemistry", () => {
  it("builds the closed-shell one-orbital energy with the constant exactly once", () => {
    const hamiltonian = buildFixedSpinHamiltonian(
      new Float64Array([-1]),
      new Float64Array([0.7]),
      1,
      2,
      0.5,
    );

    expect(hamiltonian.dimension).toBe(1);
    expect(hamiltonian.matrix[0]).toBeCloseTo(-0.8, 12);
  });

  it("preserves AO integrals under an identity MO transform", () => {
    const transformed = transformIntegralsToMo(
      {
        nbf: 2,
        hCore: [-1, 0.2, 0.2, -0.3],
        eriCompressed: [0.7, 0.1, 0.2, 0.6, 0.05, 0.5],
      },
      [1, 0, 0, 1],
    );

    expect([...transformed.h1]).toEqual([-1, 0.2, 0.2, -0.3]);
    expect(transformed.eri[0]).toBeCloseTo(0.7, 12);
    expect(transformed.eri[3]).toBeCloseTo(0.6, 12);
    expect(transformed.eri[15]).toBeCloseTo(0.5, 12);
  });

  it("runs a real two-orbital UCCSD VQE to the CASCI reference", () => {
    const integrals = integralFixture();
    const result = runBrowserCorrelatedExperiment({
      experimentId: "local_test",
      config: configFixture(),
      integrals,
      scf: scfFixture(),
      wasmVersion: "test",
      scfRuntimeSeconds: 0.01,
    });
    const row = result.comparison_table[0];

    expect(result.provenance.execution_location).toBe("visitor_device");
    expect(row.casci_total_hartree).not.toBeNull();
    expect(row.vqe_total_hartree).not.toBeNull();
    expect(Math.abs(row.solver_error_hartree ?? 1)).toBeLessThan(1e-10);
    expect(row.optimizer_evaluations).toBeGreaterThan(0);
    expect(row.num_pauli_terms).toBeGreaterThan(0);
  });
});

function configFixture(): ExperimentConfig {
  return {
    schema_version: "1",
    molecule: {
      name: "H2 model",
      atoms: [
        { symbol: "H", x: 0, y: 0, z: 0 },
        { symbol: "H", x: 0, y: 0, z: 0.74 },
      ],
      charge: 0,
      spin: 0,
      basis: "sto-3g",
      unit: "angstrom",
    },
    active_spaces: [
      {
        n_active_electrons: 2,
        n_active_orbitals: 2,
        orbital_indices: null,
        selection_mode: "canonical",
      },
    ],
    methods: ["hf", "casci", "fci", "vqe"],
    mapping: "jordan-wigner",
    ansatz: {
      ansatz_type: "uccsd",
      reps: 1,
      preserve_spin: true,
      generalized: false,
      initialization: "zeros",
    },
    solver: {
      optimizer: "periodic_coordinate",
      maxiter: 40,
      tolerance: 1e-10,
      initialization: "ansatz_default",
      random_seeds: [],
      random_scale: 0.05,
      execution_mode: "exact_statevector",
    },
    execution_mode: "exact_statevector",
    chemical_accuracy_hartree: 0.0016,
  };
}

function integralFixture(): IqcpIntegralResult {
  return {
    formatVersion: 1,
    systemId: "test",
    label: "test",
    description: "test",
    geometry: { atoms: [], units: "bohr" },
    basisId: "sto-3g",
    nbf: 2,
    nelec: 2,
    eNuc: 0.7,
    sMatrix: [1, 0, 0, 1],
    hCore: [-1, 0, 0, -0.2],
    eriCompressed: [0.7, 0, 0.15, 0.6, 0, 0.5],
    eriIndexing: "8-fold symmetry",
    metadata: { wasmVersion: "test", computeTimeMs: 1, basisType: "cartesian" },
  };
}

function scfFixture(): IqcpScfResult {
  return {
    energy: -0.6,
    converged: true,
    iterations: 4,
    aborted: false,
    history: [],
    matrices: {
      nbf: 2,
      sMatrix: [1, 0, 0, 1],
      hCore: [-1, 0, 0, -0.2],
      fockMatrix: [-0.3, 0, 0, 0.1],
      densityMatrix: [2, 0, 0, 0],
      moCoefficients: [1, 0, 0, 1],
    },
    orbitalEnergies: { energies: [-0.3, 0.1], nOccupied: 1 },
  };
}
