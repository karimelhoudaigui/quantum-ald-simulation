import type { AtomSpec } from "../types/chemistry";

export function parseXyz(text: string): AtomSpec[] {
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  if (lines.length === 0) {
    throw new Error("XYZ file is empty.");
  }

  const declaredCount = /^\d+$/.test(lines[0]) ? Number(lines[0]) : null;
  const atomLines = declaredCount === null ? lines : lines.slice(2, 2 + declaredCount);
  if (declaredCount !== null && atomLines.length !== declaredCount) {
    throw new Error("XYZ atom count does not match the file contents.");
  }

  const atoms = atomLines.map((line, index) => {
    const fields = line.split(/\s+/);
    if (fields.length < 4) {
      throw new Error(`XYZ atom row ${index + 1} must contain symbol, x, y and z.`);
    }
    const coordinates = fields.slice(1, 4).map(Number);
    if (coordinates.some((value) => !Number.isFinite(value))) {
      throw new Error(`XYZ atom row ${index + 1} contains a non-numeric coordinate.`);
    }
    return {
      symbol: fields[0],
      x: coordinates[0],
      y: coordinates[1],
      z: coordinates[2],
    };
  });
  if (atoms.length === 0) {
    throw new Error("XYZ file does not contain atoms.");
  }
  return atoms;
}

export function serializeXyz(name: string | null, atoms: AtomSpec[]): string {
  const rows = atoms.map(
    (atom) => `${atom.symbol} ${atom.x.toFixed(10)} ${atom.y.toFixed(10)} ${atom.z.toFixed(10)}`,
  );
  return `${atoms.length}\n${name ?? "Custom molecule"}\n${rows.join("\n")}\n`;
}
