import type {
  ChemistryJob,
  ChemistryJobSubmission,
  ExperimentConfig,
} from "../types/chemistry";

const CHEMISTRY_API_BASE = (
  import.meta.env.VITE_CHEMISTRY_API_BASE_URL ??
  import.meta.env.VITE_API_BASE_URL ??
  ""
)
  .trim()
  .replace(/\/$/, "");

export const isChemistryBackendConfigured =
  import.meta.env.VITE_STATIC_DEPLOYMENT !== "true" || CHEMISTRY_API_BASE.length > 0;

export class ChemistryApiError extends Error {
  readonly payload: unknown;

  constructor(message: string, payload?: unknown) {
    super(message);
    this.name = "ChemistryApiError";
    this.payload = payload;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${CHEMISTRY_API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new ChemistryApiError(`Chemistry backend unavailable: ${detail}`);
  }

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body?.detail ?? body;
    const message =
      (typeof detail?.message === "string" && detail.message) ||
      (typeof detail === "string" && detail) ||
      `Chemistry request failed with status ${response.status}`;
    throw new ChemistryApiError(message, detail);
  }
  return body as T;
}

export function getChemistryHealth(): Promise<{ status: string; schema_version: string }> {
  return request("/api/chemistry/health");
}

export function submitChemistryExperiment(
  config: ExperimentConfig,
): Promise<ChemistryJobSubmission> {
  return request("/api/chemistry/experiments", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export function getChemistryExperiment(jobId: string): Promise<ChemistryJob> {
  return request(`/api/chemistry/experiments/${encodeURIComponent(jobId)}`);
}
