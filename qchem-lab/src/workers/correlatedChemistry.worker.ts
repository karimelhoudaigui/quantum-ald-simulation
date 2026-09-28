/// <reference lib="webworker" />

import {
  runBrowserCorrelatedExperiment,
  type CorrelatedEngineInput,
  type CorrelatedProgress,
} from "../lib/browserQuantumChemistry";

interface RunMessage {
  type: "run";
  requestId: string;
  input: CorrelatedEngineInput;
}

self.addEventListener("message", (event: MessageEvent<RunMessage>) => {
  if (event.data.type !== "run") return;
  const { requestId, input } = event.data;
  try {
    const result = runBrowserCorrelatedExperiment(input, (progress: CorrelatedProgress) => {
      self.postMessage({ type: "progress", requestId, progress });
    });
    self.postMessage({ type: "result", requestId, result });
  } catch (error) {
    self.postMessage({
      type: "error",
      requestId,
      message: error instanceof Error ? error.message : String(error),
    });
  }
});

export {};
