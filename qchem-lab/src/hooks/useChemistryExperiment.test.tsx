import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { CHEMISTRY_STEP_LABELS } from "../config/chemistry";
import { useChemistryStore } from "../stores/chemistryStore";
import { completedResult } from "../test/chemistryFixtures";
import type { ChemistryJob } from "../types/chemistry";
import { useChemistryExperiment } from "./useChemistryExperiment";

function response(body: unknown, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } }));
}

function job(status: ChemistryJob["status"], result = status === "completed" ? completedResult : null): ChemistryJob {
  return {
    job_id: "chem_123",
    status,
    progress: status === "completed" ? 100 : 45,
    steps: CHEMISTRY_STEP_LABELS.map(([id, label]) => ({ id, label, status: status === "completed" ? "completed" : "running", message: null })),
    current_active_space: null,
    completed_active_spaces: status === "completed" ? 1 : 0,
    total_active_spaces: 1,
    result,
    error: null,
  };
}

describe("useChemistryExperiment", () => {
  beforeEach(() => useChemistryStore.getState().reset());
  afterEach(() => vi.unstubAllGlobals());

  it("submits, polls running state, then stores the completed result", async () => {
    const fetchMock = vi
      .fn()
      .mockImplementationOnce(() => response({ job_id: "chem_123", status: "queued" }, 202))
      .mockImplementationOnce(() => response(job("running")))
      .mockImplementationOnce(() => response(job("completed")));
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    const { result } = renderHook(() => useChemistryExperiment(), { wrapper });

    act(() => {
      expect(result.current.runExperiment()).toBe(true);
    });
    await waitFor(() => expect(useChemistryStore.getState().job?.status).toBe("running"));
    await waitFor(
      () => expect(useChemistryStore.getState().job?.status).toBe("completed"),
      { timeout: 2500 },
    );

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(useChemistryStore.getState().result?.experiment_id).toBe(completedResult.experiment_id);
  });

  it("does not invent a result when the backend is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
    const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    const { result } = renderHook(() => useChemistryExperiment(), { wrapper });

    act(() => void result.current.runExperiment());
    await waitFor(() => expect(useChemistryStore.getState().networkError).toMatch(/backend unavailable/i));

    expect(useChemistryStore.getState().result).toBeNull();
  });
});
