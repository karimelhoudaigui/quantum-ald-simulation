import type {
  CorrelatedEngineInput,
  CorrelatedProgress,
} from "./browserQuantumChemistry";
import { runIqcpScf, type IqcpProgress } from "./iqcpClient";
import type { ExperimentConfig, ExperimentResult } from "../types/chemistry";

export interface BrowserExperimentProgress {
  step: "validate" | "scf" | "active_space" | "mapping" | "vqe" | "comparison";
  progress: number;
  message: string;
  completedActiveSpaces?: number;
  totalActiveSpaces?: number;
  currentActiveSpace?: ExperimentConfig["active_spaces"][number] | null;
}

interface CorrelatedWorkerResponse {
  type?: "progress" | "result" | "error";
  requestId?: string;
  progress?: CorrelatedProgress;
  result?: ExperimentResult;
  message?: string;
}

export async function runBrowserChemistryExperiment(
  config: ExperimentConfig,
  onProgress: (progress: BrowserExperimentProgress) => void,
  signal?: AbortSignal,
): Promise<ExperimentResult> {
  const experimentId = createExperimentId();
  onProgress({ step: "validate", progress: 3, message: "Configuration validated" });
  onProgress({ step: "scf", progress: 6, message: "Loading the local WebAssembly engine" });
  const scfStarted = nowSeconds();
  const bundle = await runIqcpScf(
    config,
    (progress) => onProgress(iqcpProgressToExperiment(progress)),
    signal,
  );
  const scfRuntimeSeconds = nowSeconds() - scfStarted;
  onProgress({
    step: "scf",
    progress: 36,
    message: `RHF converged in ${bundle.scf.iterations} iterations`,
  });

  const input: CorrelatedEngineInput = {
    experimentId,
    config,
    integrals: bundle.integrals,
    scf: bundle.scf,
    wasmVersion: bundle.wasmVersion,
    scfRuntimeSeconds,
  };
  return runCorrelatedWorker(input, onProgress, signal);
}

function runCorrelatedWorker(
  input: CorrelatedEngineInput,
  onProgress: (progress: BrowserExperimentProgress) => void,
  signal?: AbortSignal,
) {
  const worker = new Worker(new URL("../workers/correlatedChemistry.worker.ts", import.meta.url), {
    type: "module",
    name: "qchem-correlated",
  });
  const requestId = `correlated-${Date.now()}`;
  return new Promise<ExperimentResult>((resolve, reject) => {
    let settled = false;
    const finish = () => {
      signal?.removeEventListener("abort", abort);
      worker.terminate();
    };
    const abort = () => {
      if (settled) return;
      settled = true;
      finish();
      reject(new DOMException("Experiment cancelled", "AbortError"));
    };
    signal?.addEventListener("abort", abort, { once: true });
    worker.addEventListener("error", (event) => {
      if (settled) return;
      settled = true;
      finish();
      reject(new Error(event.message || "The local correlated worker failed to load."));
    });
    worker.addEventListener("message", (event: MessageEvent<CorrelatedWorkerResponse>) => {
      const response = event.data;
      if (response.requestId !== requestId || settled) return;
      if (response.type === "progress" && response.progress) {
        onProgress(response.progress);
        return;
      }
      settled = true;
      finish();
      if (response.type === "result" && response.result) resolve(response.result);
      else reject(new Error(response.message || "The local correlated calculation failed."));
    });
    if (signal?.aborted) {
      abort();
      return;
    }
    worker.postMessage({ type: "run", requestId, input });
  });
}

function iqcpProgressToExperiment(progress: IqcpProgress): BrowserExperimentProgress {
  if (progress.module === "scf") {
    const fraction =
      typeof progress.iteration === "number" && typeof progress.total === "number" && progress.total > 0
        ? progress.iteration / progress.total
        : 0.5;
    return {
      step: "scf",
      progress: 20 + Math.min(1, fraction) * 15,
      message: progress.message ?? "Running local RHF iterations",
    };
  }
  const integralPercent =
    typeof progress.overallPercent === "number" ? progress.overallPercent / 100 : 0.5;
  return {
    step: "scf",
    progress: 7 + Math.min(1, Math.max(0, integralPercent)) * 13,
    message: progress.message ?? "Computing molecular integrals locally",
  };
}

function createExperimentId() {
  const id = typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID().replace(/-/g, "").slice(0, 24)
    : `${Date.now().toString(16)}${Math.random().toString(16).slice(2)}`.slice(0, 24);
  return `local_${id}`;
}

function nowSeconds() {
  return (typeof performance === "undefined" ? Date.now() : performance.now()) / 1000;
}
