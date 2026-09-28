import { useCallback, useEffect, useRef } from "react";

import {
  runBrowserChemistryExperiment,
  type BrowserExperimentProgress,
} from "../lib/browserChemistryEngine";
import {
  buildExperimentConfig,
  chemistryJobFromSubmission,
  useChemistryStore,
  validateChemistryDraft,
} from "../stores/chemistryStore";
import type { ChemistryJob, ChemistryJobStatus } from "../types/chemistry";

const ACTIVE_STATUSES: ChemistryJobStatus[] = ["queued", "running"];

export function useChemistryExperiment() {
  const job = useChemistryStore((state) => state.job);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => () => controllerRef.current?.abort(), []);

  const runExperiment = useCallback(() => {
    const state = useChemistryStore.getState();
    if (ACTIVE_STATUSES.includes(state.job?.status ?? "completed")) return false;
    const errors = validateChemistryDraft(state);
    state.setValidationErrors(errors);
    state.setNetworkError(null);
    if (errors.length > 0) return false;

    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    const jobId = createJobId();
    const config = buildExperimentConfig(state);
    const queued = chemistryJobFromSubmission({ job_id: jobId, status: "queued" });
    state.setResult(null);
    state.setJob({ ...queued, total_active_spaces: config.active_spaces.length });

    queueMicrotask(() => {
      updateJob(jobId, (current) => ({ ...current, status: "running" }));
      void runBrowserChemistryExperiment(
        config,
        (progress) => applyProgress(jobId, progress),
        controller.signal,
      )
        .then((result) => {
          if (controller.signal.aborted) return;
          const current = useChemistryStore.getState();
          if (current.job?.job_id !== jobId) return;
          current.setResult(result);
          current.setJob({
            ...current.job,
            status: result.status,
            progress: 100,
            steps: current.job.steps.map((step) => ({
              ...step,
              status: result.status === "failed" ? step.status : "completed",
            })),
            current_active_space: null,
            completed_active_spaces: result.results.active_spaces.filter(
              (entry) => entry.status === "completed",
            ).length,
            result,
            error: result.errors.length ? result.errors : null,
          });
        })
        .catch((error: unknown) => {
          if (controller.signal.aborted) return;
          const message = error instanceof Error ? error.message : String(error);
          const current = useChemistryStore.getState();
          if (current.job?.job_id !== jobId) return;
          current.setNetworkError(message);
          current.setJob({
            ...current.job,
            status: "failed",
            steps: current.job.steps.map((step) =>
              step.status === "running" ? { ...step, status: "failed", message } : step,
            ),
            error: { code: "local_engine_error", field: "runtime", message },
          });
        });
    });
    return true;
  }, []);

  return {
    runExperiment,
    isActive: ACTIVE_STATUSES.includes(job?.status ?? "completed"),
  };
}

function applyProgress(jobId: string, progress: BrowserExperimentProgress) {
  updateJob(jobId, (current) => {
    const currentIndex = current.steps.findIndex((step) => step.id === progress.step);
    return {
      ...current,
      status: "running",
      progress: Math.max(current.progress, Math.min(99, progress.progress)),
      steps: current.steps.map((step, index) => {
        if (index < currentIndex) return { ...step, status: "completed" };
        if (index === currentIndex) {
          return { ...step, status: "running", message: progress.message };
        }
        return step;
      }),
      current_active_space:
        progress.currentActiveSpace === undefined
          ? current.current_active_space
          : progress.currentActiveSpace,
      completed_active_spaces:
        progress.completedActiveSpaces ?? current.completed_active_spaces,
      total_active_spaces: progress.totalActiveSpaces ?? current.total_active_spaces,
    };
  });
}

function updateJob(jobId: string, transform: (current: ChemistryJob) => ChemistryJob) {
  const state = useChemistryStore.getState();
  if (!state.job || state.job.job_id !== jobId) return;
  state.setJob(transform(state.job));
}

function createJobId() {
  const suffix =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID().slice(0, 8)
      : Math.random().toString(16).slice(2, 10);
  return `local_job_${suffix}`;
}
