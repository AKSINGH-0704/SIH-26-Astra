"""Response envelopes for the public API.

Every response is a declared Pydantic model so the OpenAPI schema is complete and
``packages/contracts`` can be generated from it. The frontend imports those
generated types and renders what it is given; it never redeclares a shape or
recomputes a number (CLAUDE.md section 2.4).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from astra.domain.enums import HazardType, ZoneClass
from astra.domain.model_config import AstraModelConfig, Constant
from astra.domain.models import (
    CandidateSite,
    CompositeHazard,
    ConfidenceReport,
    DatasetRecord,
    Geometry,
    GeoPoint,
    Habitation,
    LayerDescriptor,
    Scenario,
    StudyArea,
)
from astra.domain.notices import Notices
from astra.domain.registry import FormulaSpec


class ModelConfigResponse(BaseModel):
    """The full transparency payload behind the Model and Provenance screen."""

    model_config = ConfigDict(frozen=True)

    config: AstraModelConfig
    constants: list[Constant] = Field(
        description="Every constant in the tree, flattened for the transparency table."
    )
    formulas: list[FormulaSpec] = Field(
        description="Every registered formula, so any number can be traced in one hop."
    )
    notices: Notices = Field(
        description="Standing framing text, served so the UI never retypes it."
    )


class ProvenanceResponse(BaseModel):
    """The dataset registry, with per-class counts kept unblended."""

    model_config = ConfigDict(frozen=True)

    registry_version: str
    datasets: list[DatasetRecord]
    counts_by_class: dict[str, int]
    note: str


class LayersResponse(BaseModel):
    """The layer catalogue, including layers that are declared but not yet available."""

    model_config = ConfigDict(frozen=True)

    layers: list[LayerDescriptor]
    available_count: int
    declared_count: int


class ValidationCheckResponse(BaseModel):
    """The fixture integrity gate result, surfaced rather than hidden in a log."""

    model_config = ConfigDict(frozen=True)

    ok: bool
    summary: str
    checks: list[str]
    errors: list[str]
    warnings: list[str]
    fixture_count: int
    dataset_count: int


class ScenarioResponse(BaseModel):
    """A scenario with the study area it is framed by."""

    model_config = ConfigDict(frozen=True)

    scenario: Scenario
    study_area: StudyArea


class ScenarioListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenarios: list[Scenario]
    study_areas: list[StudyArea]


class HabitationsResponse(BaseModel):
    """The habitation layer, with the totals a planner reads first."""

    model_config = ConfigDict(frozen=True)

    habitations: list[Habitation]
    total_population: int
    total_households: int
    disclaimer: str = Field(
        description="Standing reminder that these records are synthetic and fictional."
    )


class SitesResponse(BaseModel):
    """The candidate-site layer. Capacity analysis lands with the capacity engine."""

    model_config = ConfigDict(frozen=True)

    sites: list[CandidateSite]
    total_gross_area_m2: float
    limitation: str = Field(
        description="The tenure limitation ASTRA states before it is asked."
    )


class DerivedLayerSummary(BaseModel):
    """One computed surface, with the range it actually spans."""

    model_config = ConfigDict(frozen=True)

    name: str
    file: str
    unit: str
    dtype: str
    bytes: int
    min: float
    max: float
    mean: float
    note: str


class StudyAreaDataResponse(BaseModel):
    """What ASTRA has actually built for the study area, and how."""

    model_config = ConfigDict(frozen=True)

    study_area: StudyArea
    grid: dict[str, float]
    methods: dict[str, str]
    channel_threshold_km2: float
    layers: list[DerivedLayerSummary]
    generation: dict[str, Any]
    terrain_preview_url: str
    terrain_preview_bbox: list[float]


class ZoneFeatureProperties(BaseModel):
    """Attributes carried by every published zone polygon."""

    model_config = ConfigDict(frozen=True)

    id: str
    zone_class: ZoneClass
    classification_label: str = Field(
        description="Always the ASTRA analytical label. Never an official designation."
    )
    area_km2: float
    mean_composite: float
    max_composite: float
    dominant_hazard: HazardType
    hazard_mix: dict[str, float]
    mean_confidence: float
    cell_count: int
    population_intersected: int
    habitation_ids: list[str]
    rule_version: str


class ZoneFeature(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["Feature"] = "Feature"
    id: str
    geometry: Geometry
    properties: ZoneFeatureProperties


class ZoneClassSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    count: int
    area_km2: float
    population_intersected: int


class ZonesResponse(BaseModel):
    """Red zones as a GeoJSON feature collection, with the totals precomputed."""

    model_config = ConfigDict(frozen=True)

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[ZoneFeature]
    summary: dict[str, ZoneClassSummary]
    classification_label: str
    decision_authority: str
    model_config_version: str
    engine_version: str
    computed_ms: float


class RiskCellResponse(BaseModel):
    """Everything behind the hazard score at one point on the map."""

    model_config = ConfigDict(frozen=True)

    lon: float
    lat: float
    row: int
    col: int
    cell_bbox: list[float]
    hazard: CompositeHazard
    confidence: ConfidenceReport
    zone_id: str | None
    zone_class: ZoneClass
    formula: FormulaSpec
    composite_formula: FormulaSpec
    model_config_version: str
    engine_version: str
    computed_at: datetime


class HabitationHazardRow(BaseModel):
    """Hazard sampled over one habitation footprint. Exposure arrives in Slice 4."""

    model_config = ConfigDict(frozen=True)

    habitation_id: str
    name: str
    population: int
    households: int
    centroid: GeoPoint
    hazard: CompositeHazard
    footprint_mean_composite: float
    footprint_max_composite: float
    footprint_radius_m: float
    confidence: ConfidenceReport
    zone_id: str | None


class HabitationHazardResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    habitations: list[HabitationHazardRow]
    classification_label: str
    decision_authority: str
    scenario_disclaimer: str
    note: str


class RiskSummaryResponse(BaseModel):
    """What the hazard engine computed, and over what."""

    model_config = ConfigDict(frozen=True)

    study_area: StudyArea
    grid_rows: int
    grid_cols: int
    cell_x_m: float
    cell_y_m: float
    hazards_modelled: list[HazardType]
    class_share_percent: dict[str, float]
    hazard_statistics: dict[str, dict[str, float]]
    zone_summary: dict[str, ZoneClassSummary]
    incidents_used: int
    incidents_excluded: int
    rainfall_points: int
    composite_lambda: float
    zone_thresholds: dict[str, float]
    overlay_url: str
    overlay_bbox: list[float]
    terrain_url: str
    computed_ms: float
    model_config_version: str
    engine_version: str
