import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { useChemistryStore } from "../../stores/chemistryStore";
import { completedResult } from "../../test/chemistryFixtures";
import { ChemistryResultsDashboard } from "./ChemistryResultsDashboard";

describe("ChemistryResultsDashboard", () => {
  beforeEach(() => useChemistryStore.getState().reset());

  it("renders completed comparison rows and scientific metrics", () => {
    useChemistryStore.getState().setResult({
      ...completedResult,
      status: "partial",
      warnings: [{ code: "reference_unavailable", field: "methods.fci", message: "FCI unavailable" }],
    });

    render(<ChemistryResultsDashboard />);

    expect(screen.getAllByText("2,2").length).toBeGreaterThan(0);
    expect(screen.getByText("FCI unavailable")).toBeInTheDocument();
    expect(screen.getAllByText("4").length).toBeGreaterThan(0);
  });

  it("renders structured job errors with their field", () => {
    useChemistryStore.getState().setJob({
      job_id: "chem_invalid",
      status: "invalid_configuration",
      progress: 100,
      steps: [],
      current_active_space: null,
      completed_active_spaces: 0,
      total_active_spaces: 1,
      result: null,
      error: {
        code: "invalid_active_space",
        field: "active_spaces[0]",
        message: "6 active electrons cannot fit in 2 spatial orbitals.",
      },
    });

    render(<ChemistryResultsDashboard />);

    expect(screen.getByText("active_spaces[0] · invalid_active_space")).toBeInTheDocument();
    expect(screen.getByText(/6 active electrons/)).toBeInTheDocument();
  });
});
