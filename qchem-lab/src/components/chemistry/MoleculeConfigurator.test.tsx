import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it } from "vitest";

import { useChemistryStore } from "../../stores/chemistryStore";
import { MoleculeConfigurator } from "./MoleculeConfigurator";

function wrapper({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={new QueryClient()}>{children}</QueryClientProvider>;
}

describe("MoleculeConfigurator", () => {
  beforeEach(() => useChemistryStore.getState().reset());

  it("adds and removes an editable atom row", async () => {
    const user = userEvent.setup();
    render(<MoleculeConfigurator />, { wrapper });

    await user.click(screen.getByRole("button", { name: /add atom/i }));
    expect(screen.getByLabelText("Atom 3 element")).toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText("Atom 3 element"), "Al");
    expect(useChemistryStore.getState().atoms[2].symbol).toBe("Al");

    await user.click(screen.getByRole("button", { name: "Delete atom 3" }));
    expect(screen.queryByLabelText("Atom 3 element")).not.toBeInTheDocument();
  });

  it("requires CASCI while VQE is enabled", () => {
    render(<MoleculeConfigurator />, { wrapper });

    expect(screen.getByRole("checkbox", { name: "CASCI" })).toBeDisabled();
    expect(screen.getByText(/CASCI is required/)).toBeInTheDocument();
  });

  it("reserves a disabled hardware execution action", () => {
    render(<MoleculeConfigurator />, { wrapper });

    expect(screen.getByRole("button", { name: "RUN HARDWARE" })).toBeDisabled();
  });
});
