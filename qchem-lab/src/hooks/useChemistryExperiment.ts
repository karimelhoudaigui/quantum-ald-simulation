import { useMutation, useQuery } from "@tanstack/react-query";
import { useCallback, useEffect } from "react";

import { getChemistryExperiment, submitChemistryExperiment } from "../lib/chemistryApi";
import {
  buildExperimentConfig,
  chemistryJobFromSubmission,
  useChemistryStore,
  validateChemistryDraft,
} from "../stores/chemistryStore";
import type {
  ChemistryJob,
  ChemistryJobStatus,
  ChemistryValidationError,
  ExperimentConfig,
} from "../types/chemistry";

const ACTIVE_STATUSES: ChemistryJobStatus[] = ["queued", "running"];

export function useChemistryExperiment() {
  const job = useChemistryStore((state) => state.job);
  const setJob = useChemistryStore((state) => state.setJob);
  const setResult = useChemistryStore((state) => state.setResult);
  const setValidationErrors = useChemistryStore((state) => state.setValidationErrors);
  const setNetworkError = useChemistryStore((state) => state.setNetworkError);

  const submit = useMutation({
    mutationFn: (config: ExperimentConfig) => submitChemistryExperiment(config),
    onMutate: () => {
      setJob(null);
      setResult(null);
      setNetworkError(null);
    },
    onSuccess: (submission) => setJob(chemistryJobFromSubmission(submission)),
    onError: (error) => {
      setNetworkError(
        error instanceof Error ? error.message : "Chemistry backend unavailable",
      );
    },
  });

  const status = useQuery({
    queryKey: ["chemistry-experiment", job?.job_id],
    queryFn: () => getChemistryExperiment(job?.job_id ?? ""),
    enabled: Boolean(job?.job_id) && ACTIVE_STATUSES.includes(job?.status ?? "completed"),
    refetchInterval: (query) => {
      const current = query.state.data;
      return current && ACTIVE_STATUSES.includes(current.status) ? 1200 : false;
    },
    retry: 1,
  });

  useEffect(() => {
    if (!status.data || status.data.job_id !== job?.job_id) return;
    setJob(status.data);
    if (status.data.result) setResult(status.data.result);
    if (status.data.status === "invalid_configuration") {
      setValidationErrors(asValidationErrors(status.data.error));
    }
  }, [job?.job_id, setJob, setResult, setValidationErrors, status.data]);

  useEffect(() => {
    if (!status.error) return;
    const message =
      status.error instanceof Error
        ? status.error.message
        : "Chemistry backend unavailable";
    setNetworkError(message);
    const currentJob = useChemistryStore.getState().job;
    if (currentJob && ACTIVE_STATUSES.includes(currentJob.status)) {
      setJob({
        ...currentJob,
        status: "failed",
        error: {
          code: "chemistry_backend_unavailable",
          field: "network",
          message,
        },
      });
    }
  }, [setJob, setNetworkError, status.error]);

  const runExperiment = useCallback(() => {
    const state = useChemistryStore.getState();
    const errors = validateChemistryDraft(state);
    setValidationErrors(errors);
    setNetworkError(null);
    if (errors.length > 0) return false;
    submit.mutate(buildExperimentConfig(state));
    return true;
  }, [setNetworkError, setValidationErrors, submit]);

  return {
    runExperiment,
    submit,
    status,
    isActive: submit.isPending || ACTIVE_STATUSES.includes(job?.status ?? "completed"),
  };
}

function asValidationErrors(error: ChemistryJob["error"]): ChemistryValidationError[] {
  if (!error) return [];
  return (Array.isArray(error) ? error : [error]).map(({ code, field, message }) => ({
    code,
    field,
    message,
  }));
}
