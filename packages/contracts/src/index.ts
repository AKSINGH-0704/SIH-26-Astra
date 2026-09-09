/**
 * The single source of numeric truth, on the TypeScript side.
 *
 * `api.ts` is generated from the FastAPI OpenAPI schema by
 * `npm run contracts` and is never hand-edited. The aliases below are the only
 * thing this package adds: readable names for the generated component schemas,
 * so application code imports `HealthStatus` rather than digging through
 * `components["schemas"][...]`.
 *
 * There are deliberately no hand-written interfaces here. If the backend
 * changes a field, the frontend fails to compile - which is the point
 * (CLAUDE.md section 2.4).
 */

import type { components, paths } from "./api";

export type { components, paths };

type Schemas = components["schemas"];

export type HealthStatus = Schemas["HealthStatus"];
export type ModelConfigResponse = Schemas["ModelConfigResponse"];
export type ProvenanceResponse = Schemas["ProvenanceResponse"];
export type LayersResponse = Schemas["LayersResponse"];
export type ScenarioListResponse = Schemas["ScenarioListResponse"];
export type ScenarioResponse = Schemas["ScenarioResponse"];
export type ValidationCheckResponse = Schemas["ValidationCheckResponse"];
export type HabitationsResponse = Schemas["HabitationsResponse"];
export type SitesResponse = Schemas["SitesResponse"];
export type StudyAreaDataResponse = Schemas["StudyAreaDataResponse"];

export type AstraModelConfig = Schemas["AstraModelConfig"];
export type Constant = Schemas["Constant"];
export type FormulaSpec = Schemas["FormulaSpec"];
export type Notices = Schemas["Notices"];
export type DatasetRecord = Schemas["DatasetRecord"];
export type LayerDescriptor = Schemas["LayerDescriptor"];
export type Scenario = Schemas["Scenario"];
export type StudyArea = Schemas["StudyArea"];
export type BBox = Schemas["BBox"];
export type Habitation = Schemas["Habitation"];
export type CandidateSite = Schemas["CandidateSite"];
export type DerivedLayerSummary = Schemas["DerivedLayerSummary"];
export type ServiceSupply = Schemas["ServiceSupply"];
export type GeoPoint = Schemas["GeoPoint"];

export type ProvenanceClass = Schemas["ProvenanceClass"];
export type ConfidenceBand = Schemas["ConfidenceBand"];

/** Palette-independent ordering used wherever provenance classes are listed. */
export const PROVENANCE_ORDER: ProvenanceClass[] = [
  "REAL_OPEN",
  "DERIVED",
  "SYNTHETIC_CALIBRATED",
  "DEMO_CONFIG",
];

/** Short labels for the provenance chips. Long text comes from the API. */
export const PROVENANCE_LABEL: Record<ProvenanceClass, string> = {
  REAL_OPEN: "Real open data",
  DERIVED: "Derived by ASTRA",
  SYNTHETIC_CALIBRATED: "Synthetic, calibrated",
  DEMO_CONFIG: "ASTRA demo constant",
};
