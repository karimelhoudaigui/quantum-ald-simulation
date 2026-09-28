import type { ExperimentConfig } from "../types/chemistry";

export interface IqcpIntegralResult {
  formatVersion: number;
  systemId: string;
  label: string;
  description: string;
  geometry: {
    atoms: Array<{ symbol: string; xyz: [number, number, number]; atomicNumber: number }>;
    units: string;
  };
  basisId: string;
  nbf: number;
  nelec: number;
  eNuc: number;
  sMatrix: number[];
  hCore: number[];
  eriCompressed: number[];
  eriIndexing: string;
  metadata: {
    wasmVersion: string;
    computeTimeMs: number;
    basisType: string;
    [key: string]: unknown;
  };
}

export interface IqcpScfResult {
  energy: number;
  converged: boolean;
  iterations: number;
  aborted: boolean;
  history: Array<{
    iteration: number;
    energy: number;
    delta: number;
    diisError?: number;
  }>;
  matrices?: {
    nbf: number;
    sMatrix: number[];
    hCore: number[];
    fockMatrix: number[];
    densityMatrix: number[];
    moCoefficients: number[];
  };
  orbitalEnergies?: {
    energies: number[];
    nOccupied: number;
  };
}

export interface IqcpScfBundle {
  wasmVersion: string;
  integrals: IqcpIntegralResult;
  scf: IqcpScfResult;
}

export interface IqcpProgress {
  module?: string;
  message?: string;
  overallPercent?: number;
  iteration?: number;
  total?: number;
  current?: number;
  [key: string]: unknown;
}

interface PendingRequest {
  resolve: (value: unknown) => void;
  reject: (reason: Error) => void;
  onProgress?: (progress: IqcpProgress) => void;
}

interface WorkerEnvelope {
  type?: string;
  requestId?: string;
  data?: unknown;
  progress?: IqcpProgress;
  message?: string;
  code?: string;
  wasmVersion?: string;
}

export async function runIqcpScf(
  config: ExperimentConfig,
  onProgress?: (progress: IqcpProgress) => void,
  signal?: AbortSignal,
): Promise<IqcpScfBundle> {
  const client = new IqcpWorkerClient(signal);
  try {
    const pong = await client.request<{ wasmVersion: string }>("ping", {}, onProgress);
    const integrals = await client.request<IqcpIntegralResult>(
      "integral_compute",
      {
        geometry: {
          atoms: config.molecule.atoms.map(({ symbol, x, y, z }) => ({
            symbol,
            xyz: [x, y, z],
          })),
          units: config.molecule.unit,
        },
        basisSet: config.molecule.basis.toLowerCase(),
        useSpherical: true,
      },
      onProgress,
    );
    const scf = await client.request<IqcpScfResult>(
      "scf_run",
      {
        systemId: integrals.systemId,
        options: {
          convergenceProfile: "tight",
          maxIterations: 100,
          useDiis: true,
          diisSize: 8,
          includeMatrices: true,
        },
      },
      onProgress,
    );
    if (!scf.converged) {
      throw new Error(`Local RHF did not converge after ${scf.iterations} iterations.`);
    }
    if (!scf.matrices || !scf.orbitalEnergies) {
      throw new Error("The local RHF engine did not return molecular-orbital matrices.");
    }
    return { wasmVersion: pong.wasmVersion, integrals, scf };
  } finally {
    client.dispose();
  }
}

class IqcpWorkerClient {
  private readonly worker: Worker;
  private readonly pending = new Map<string, PendingRequest>();
  private sequence = 0;
  private readonly abortHandler: () => void;

  constructor(private readonly signal?: AbortSignal) {
    const workerUrl = `${import.meta.env.BASE_URL}wasm/iqcp-compute.worker.js`;
    this.worker = new Worker(workerUrl, { type: "module", name: "qchem-iqcp" });
    this.worker.addEventListener("message", this.handleMessage);
    this.worker.addEventListener("error", this.handleWorkerError);
    this.abortHandler = () => this.failAll(new DOMException("Experiment cancelled", "AbortError"));
    signal?.addEventListener("abort", this.abortHandler, { once: true });
    if (signal?.aborted) this.abortHandler();
  }

  request<T>(
    type: string,
    payload: Record<string, unknown>,
    onProgress?: (progress: IqcpProgress) => void,
  ): Promise<T> {
    if (this.signal?.aborted) {
      return Promise.reject(new DOMException("Experiment cancelled", "AbortError"));
    }
    const requestId = `iqcp-${Date.now()}-${++this.sequence}`;
    return new Promise<T>((resolve, reject) => {
      this.pending.set(requestId, {
        resolve: (value) => resolve(value as T),
        reject,
        onProgress,
      });
      this.worker.postMessage({ type, requestId, ...payload });
    });
  }

  dispose() {
    this.signal?.removeEventListener("abort", this.abortHandler);
    this.worker.removeEventListener("message", this.handleMessage);
    this.worker.removeEventListener("error", this.handleWorkerError);
    this.worker.terminate();
    this.failAll(new Error("Local chemistry worker was closed."));
  }

  private readonly handleMessage = (event: MessageEvent<WorkerEnvelope>) => {
    const response = event.data;
    if (!response.requestId) return;
    const pending = this.pending.get(response.requestId);
    if (!pending) return;
    if (response.type === "progress" && response.progress) {
      pending.onProgress?.(response.progress);
      return;
    }
    this.pending.delete(response.requestId);
    if (response.type === "error") {
      pending.reject(
        new Error(
          `${response.message ?? "Local chemistry worker failed"}${
            response.code ? ` (${response.code})` : ""
          }`,
        ),
      );
      return;
    }
    if (response.type === "pong") {
      pending.resolve({ wasmVersion: response.wasmVersion ?? "unknown" });
      return;
    }
    if (response.type === "result") {
      pending.resolve(response.data);
      return;
    }
    pending.reject(new Error(`Unexpected response from local chemistry worker: ${response.type}`));
  };

  private readonly handleWorkerError = (event: ErrorEvent) => {
    this.failAll(new Error(event.message || "Unable to load the local chemistry engine."));
  };

  private failAll(error: Error) {
    for (const request of this.pending.values()) request.reject(error);
    this.pending.clear();
    this.worker.terminate();
  }
}
