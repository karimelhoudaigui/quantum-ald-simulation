import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { runBrowserChemistryExperiment } from "../lib/browserChemistryEngine";
import { useChemistryStore } from "../stores/chemistryStore";
import { completedResult } from "../test/chemistryFixtures";
import { useChemistryExperiment } from "./useChemistryExperiment";

vi.mock("../lib/browserChemistryEngine", () => ({
  runBrowserChemistryExperiment: vi.fn(),
}));

const runLocal = vi.mocked(runBrowserChemistryExperiment);

describe("useChemistryExperiment", () => {
  beforeEach(() => {
    useChemistryStore.getState().reset();
    runLocal.mockReset();
  });

  it("runs locally, exposes progress, then stores the completed result", async () => {
    let finish: ((value: typeof completedResult) => void) | undefined;
    runLocal.mockImplementation((_config, onProgress) => {
      onProgress({ step: "scf", progress: 25, message: "Local RHF" });
      return new Promise((resolve) => {
        finish = resolve;
      });
    });
    const { result } = renderHook(() => useChemistryExperiment());

    act(() => {
      expect(result.current.runExperiment()).toBe(true);
    });
    await waitFor(() => expect(useChemistryStore.getState().job?.status).toBe("running"));
    expect(useChemistryStore.getState().job?.progress).toBe(25);

    await act(async () => finish?.(completedResult));
    await waitFor(() => expect(useChemistryStore.getState().job?.status).toBe("completed"));
    expect(useChemistryStore.getState().result?.experiment_id).toBe(completedResult.experiment_id);
  });

  it("does not invent a result when the local engine fails", async () => {
    runLocal.mockRejectedValue(new Error("Local engine unavailable"));
    const { result } = renderHook(() => useChemistryExperiment());

    act(() => void result.current.runExperiment());
    await waitFor(() =>
      expect(useChemistryStore.getState().networkError).toMatch(/local engine unavailable/i),
    );

    expect(useChemistryStore.getState().job?.status).toBe("failed");
    expect(useChemistryStore.getState().result).toBeNull();
  });
});
