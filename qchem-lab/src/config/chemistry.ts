import type { AtomSpec } from "../types/chemistry";

export const ELEMENT_OPTIONS = [
  "H",
  "He",
  "Li",
  "Be",
  "B",
  "C",
  "N",
  "O",
  "F",
  "Ne",
  "Na",
  "Mg",
  "Al",
  "Si",
  "P",
  "S",
  "Cl",
  "Ar",
] as const;

export const MOLECULE_PRESETS: Record<string, { name: string; atoms: AtomSpec[] }> = {
  h2: {
    name: "H2",
    atoms: [
      { symbol: "H", x: 0, y: 0, z: 0 },
      { symbol: "H", x: 0, y: 0, z: 0.74 },
    ],
  },
  lih: {
    name: "LiH",
    atoms: [
      { symbol: "Li", x: 0, y: 0, z: 0 },
      { symbol: "H", x: 0, y: 0, z: 1.64 },
    ],
  },
  h2o: {
    name: "H2O",
    atoms: [
      { symbol: "O", x: 0, y: 0, z: 0.11872 },
      { symbol: "H", x: 0, y: 0.755453, z: -0.47488 },
      { symbol: "H", x: 0, y: -0.755453, z: -0.47488 },
    ],
  },
};

export const CHEMISTRY_STEP_LABELS = [
  ["validate", "Validate"],
  ["scf", "Molecule / SCF"],
  ["active_space", "Active space / CASCI"],
  ["mapping", "Fermionic / JW"],
  ["vqe", "UCCSD / VQE"],
  ["comparison", "Compare"],
] as const;
