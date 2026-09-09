/**
 * The only place the frontend talks to the API.
 *
 * Every response type comes from `@astra/contracts`, which is generated from the
 * FastAPI OpenAPI schema. Nothing here reshapes, recomputes or rounds a value:
 * the interface renders what the engines produced (CLAUDE.md section 2.4).
 */

import type {
  HabitationsResponse,
  HealthStatus,
  LayersResponse,
  ModelConfigResponse,
  ProvenanceResponse,
  ScenarioListResponse,
  SitesResponse,
  StudyAreaDataResponse,
  ValidationCheckResponse,
} from "@astra/contracts";

export const API_BASE =
  process.env.NEXT_PUBLIC_ASTRA_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export class ApiUnavailableError extends Error {
  constructor(
    readonly path: string,
    readonly cause_: unknown,
  ) {
    super(`ASTRA API did not respond at ${path}`);
    this.name = "ApiUnavailableError";
  }
}

async function get<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      cache: "no-store",
      headers: { accept: "application/json" },
    });
  } catch (error) {
    throw new ApiUnavailableError(path, error);
  }
  if (!response.ok) {
    throw new ApiUnavailableError(path, `HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export const api = {
  health: () => get<HealthStatus>("/health"),
  modelConfig: () => get<ModelConfigResponse>("/model/config"),
  provenance: () => get<ProvenanceResponse>("/provenance"),
  layers: () => get<LayersResponse>("/layers"),
  scenarios: () => get<ScenarioListResponse>("/scenarios"),
  fixtureValidation: () => get<ValidationCheckResponse>("/validation/fixtures"),
  habitations: () => get<HabitationsResponse>("/habitations"),
  sites: () => get<SitesResponse>("/sites"),
  studyAreaData: () => get<StudyAreaDataResponse>("/study-area/data"),
};

/** The API serves the terrain render; the browser fetches it straight from there. */
export const TERRAIN_PREVIEW_URL = `${API_BASE}/study-area/terrain.jpg`;

/**
 * Fetch without letting one dead endpoint blank the whole screen. A failure is
 * reported as a failure - the interface never substitutes a plausible number.
 */
export async function tryFetch<T>(loader: () => Promise<T>): Promise<T | null> {
  try {
    return await loader();
  } catch {
    return null;
  }
}
