import { beforeEach, describe, expect, it } from "vitest";

import {
  buildExperimentConfig,
  useChemistryStore,
  validateChemistryDraft,
} from "./chemistryStore";

describe("chemistry store", () => {
  beforeEach(() => useChemistryStore.getState().reset());

  it("adds, updates and removes user atoms", () => {
    const initialCount = useChemistryStore.getState().atoms.length;
    useChemistryStore.getState().addAtom();
    const addedAtoms = useChemistryStore.getState().atoms;
    const added = addedAtoms[addedAtoms.length - 1];
    useChemistryStore.getState().updateAtom(added.id, { symbol: "Al", z: 1.25 });

    expect(useChemistryStore.getState().atoms).toHaveLength(initialCount + 1);
    const updatedAtoms = useChemistryStore.getState().atoms;
    expect(updatedAtoms[updatedAtoms.length - 1]).toMatchObject({ symbol: "Al", z: 1.25 });

    useChemistryStore.getState().removeAtom(added.id);
    expect(useChemistryStore.getState().atoms).toHaveLength(initialCount);
  });

  it("keeps CASCI enabled when VQE is selected", () => {
    useChemistryStore.getState().setMethod("casci", false);
    expect(useChemistryStore.getState().methods.casci).toBe(true);

    useChemistryStore.getState().setMethod("vqe", false);
    useChemistryStore.getState().setMethod("casci", false);
    expect(useChemistryStore.getState().methods.casci).toBe(false);
  });

  it("builds the exact schema-version-1 ExperimentConfig in one place", () => {
    const firstActiveSpace = useChemistryStore.getState().activeSpaces[0];
    useChemistryStore.getState().updateActiveSpace(firstActiveSpace.id, {
      selection_mode: "manual",
      orbitalIndicesInput: "0, 1",
    });
    const config = buildExperimentConfig(useChemistryStore.getState());

    expect(config.schema_version).toBe("1");
    expect(config.molecule.atoms[0]).toEqual({ symbol: "Li", x: 0, y: 0, z: 0 });
    expect(config.active_spaces[0]).toMatchObject({
      n_active_electrons: 2,
      n_active_orbitals: 2,
      selection_mode: "manual",
      orbital_indices: [0, 1],
    });
    expect(config.methods).toEqual(["hf", "casci", "fci", "vqe"]);
    expect(config.ansatz?.ansatz_type).toBe("uccsd");
    expect(config.solver?.execution_mode).toBe("exact_statevector");
  });

  it("reports obvious active-space errors before submission", () => {
    const firstActiveSpace = useChemistryStore.getState().activeSpaces[0];
    useChemistryStore.getState().updateActiveSpace(firstActiveSpace.id, {
      n_active_electrons: 6,
      n_active_orbitals: 2,
    });

    expect(validateChemistryDraft(useChemistryStore.getState())).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: "invalid_active_space", field: "active_spaces[0]" }),
      ]),
    );
  });

  it("rejects the CASCI-only combination exposed by the schema", () => {
    useChemistryStore.getState().setMethod("vqe", false);

    expect(validateChemistryDraft(useChemistryStore.getState())).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ code: "unsupported_method_combination", field: "methods" }),
      ]),
    );
  });

  it("omits inactive active spaces from an HF-only request", () => {
    useChemistryStore.getState().setMethod("vqe", false);
    useChemistryStore.getState().setMethod("casci", false);
    useChemistryStore.getState().setMethod("fci", false);
    const firstActiveSpace = useChemistryStore.getState().activeSpaces[0];
    useChemistryStore.getState().updateActiveSpace(firstActiveSpace.id, {
      n_active_electrons: 6,
      n_active_orbitals: 2,
    });

    expect(validateChemistryDraft(useChemistryStore.getState())).toEqual([]);
    expect(buildExperimentConfig(useChemistryStore.getState()).active_spaces).toEqual([]);
  });
});
