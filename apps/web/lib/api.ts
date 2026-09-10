/**
 * The only place the frontend talks to the API.
 *
 * Every response type comes from `@astra/contracts`, which is generated from the
 * FastAPI OpenAPI schema. Nothing here reshapes, recomputes or rounds a value:
 * the interface renders what the engines produced (CLAUDE.md section 2.4).
 */

import type {
  ClosureImpactResponse,
  CounterfactualResponse,
  HabitationDetailResponse,
  HabitationHazardResponse,
  HabitationPriorityResponse,
  HabitationsResponse,
  HealthStatus,
  LayersResponse,
  ModelConfigResponse,
  PlanDependencyListResponse,
  PlanResponse,
  Perturbation,
  ProvenanceResponse,
  RiskCellResponse,
  RiskSummaryResponse,
  RouteAssessmentResponse,
  RoutePairResponse,
  ScenarioDiffResponse,
  ScenarioListResponse,
  SiteCapacityListResponse,
  SitesResponse,
  StudyAreaDataResponse,
  ValidationCheckResponse,
  ZonesResponse,
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

/**
 * The API answered, and refused. Its reason is carried verbatim: a refusal that
 * names the perturbation it would not apply is more useful to the person who
 * built the scenario than a generic failure, and inventing a friendlier reason
 * here would be inventing a fact about the engine.
 */
export class ApiRefusedError extends Error {
  constructor(
    readonly path: string,
    readonly status: number,
    readonly detail: string,
  ) {
    super(detail);
    this.name = "ApiRefusedError";
  }
}

/** Pull the API's own explanation out of an error response, if it gave one. */
async function refusal(path: string, response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail) {
      return new ApiRefusedError(path, response.status, body.detail);
    }
  } catch {
    // No JSON body: fall through to the transport-level error.
  }
  return new ApiUnavailableError(path, `HTTP ${response.status}`);
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
  riskSummary: () => get<RiskSummaryResponse>("/risk/summary"),
  riskZones: () => get<ZonesResponse>("/risk/zones"),
  riskHabitations: () => get<HabitationHazardResponse>("/risk/habitations"),
  capacitySites: () => get<SiteCapacityListResponse>("/capacity/sites"),
  priorityHabitations: () => get<HabitationPriorityResponse>("/priority/habitations"),
  priorityHabitation: (id: string) =>
    get<HabitationDetailResponse>(`/priority/habitations/${encodeURIComponent(id)}`),
  riskCell: (lon: number, lat: number) =>
    get<RiskCellResponse>(`/risk/cell?lon=${lon.toFixed(6)}&lat=${lat.toFixed(6)}`),
  routes: () => get<RouteAssessmentResponse>("/routes"),
  plan: () => get<PlanResponse>("/plan"),
  planDependencies: () =>
    get<PlanDependencyListResponse>("/routes/critical-segments"),
  whyNot: (habitationId: string, siteId: string) =>
    get<CounterfactualResponse>(
      `/plan/why-not/${encodeURIComponent(habitationId)}/${encodeURIComponent(siteId)}`,
    ),
  routePair: (habitationId: string, siteId: string) =>
    get<RoutePairResponse>(
      `/routes/pair/${encodeURIComponent(habitationId)}/${encodeURIComponent(siteId)}`,
    ),
};

/**
 * Close roads and get back a complete second assessment beside the baseline.
 * The only mutating call in the interface, and it mutates nothing on the server:
 * the closure is an argument, not a state change.
 */
/**
 * Re-solve the plan, optionally under closures or with the greedy fallback.
 * Like the closure evaluator, this changes nothing on the server: the baseline
 * plan stays where it is so the two can be compared.
 */
export async function optimisePlan(body: {
  closed_segments?: string[];
  use_fallback?: boolean;
}): Promise<PlanResponse> {
  return post<PlanResponse>("/plan/optimize", body);
}

/**
 * Run the whole chain under a set of perturbations and get back a structured
 * diff against the baseline. The baseline is not replaced.
 */
export async function simulate(
  changes: Perturbation[],
  name?: string,
): Promise<ScenarioDiffResponse> {
  return post<ScenarioDiffResponse>("/simulate", { changes, name });
}

export async function evaluateClosure(
  closedSegments: string[],
): Promise<ClosureImpactResponse> {
  return post<ClosureImpactResponse>("/routes/evaluate", {
    closed_segments: closedSegments,
  });
}

async function post<T>(path: string, body: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      cache: "no-store",
      headers: { "content-type": "application/json", accept: "application/json" },
      body: JSON.stringify(body),
    });
  } catch (error) {
    throw new ApiUnavailableError(path, error);
  }
  if (!response.ok) {
    throw await refusal(path, response);
  }
  return (await response.json()) as T;
}

/** Served by the API so the map works with the network unplugged. */
export const HAZARD_OVERLAY_URL = `${API_BASE}/risk/overlay/composite.png`;
export const ROADS_GEOJSON_URL = `${API_BASE}/layers/roads.geojson`;

/** The routed graph, with each segment's computed failure probability. */
export const ROUTE_NETWORK_URL = `${API_BASE}/routes/network.geojson`;

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
