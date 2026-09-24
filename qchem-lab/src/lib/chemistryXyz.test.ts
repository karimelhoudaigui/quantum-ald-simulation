import { describe, expect, it } from "vitest";

import { parseXyz, serializeXyz } from "./chemistryXyz";

describe("chemistry XYZ utilities", () => {
  it("parses a headered XYZ file into detached atom data", () => {
    const atoms = parseXyz("2\nLiH upload\nLi 0 0 0\nH 0 0 1.64\n");

    expect(atoms).toEqual([
      { symbol: "Li", x: 0, y: 0, z: 0 },
      { symbol: "H", x: 0, y: 0, z: 1.64 },
    ]);
  });

  it("serializes geometry without retaining a source path", () => {
    const text = serializeXyz("LiH", parseXyz("Li 0 0 0\nH 0 0 1.64"));

    expect(text).toContain("2\nLiH\n");
    expect(text).not.toContain("/");
  });

  it("rejects malformed coordinate rows", () => {
    expect(() => parseXyz("1\ncomment\nH zero 0 0")).toThrow("non-numeric");
  });
});
