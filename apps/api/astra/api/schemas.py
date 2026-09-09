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

from astra.domain.enums import (
    ConfidenceBand,
    HazardType,
    PhaseTier,
    ProvenanceClass,
    RoadClass,
    RouteProfile,
    ServiceType,
    ZoneClass,
)
from astra.domain.model_config import AstraModelConfig, Constant
from astra.domain.models import (
    CandidateSite,
    CompositeHazard,
    ConfidenceReport,
    DatasetRecord,
    FactorContribution,
    GateResult,
    Geometry,
    GeoPoint,
    Habitation,
    LayerDescriptor,
    Scenario,
    ServiceCapacity,
    StudyArea,
    ValueExplanation,
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
    landcover_refinement: dict[str, Any] | None = Field(
        default=None,
        description="The scoped machine-learning component: its labelling rules, what "
        "each rule found, its measured accuracy, its agreement with the published "
        "land-cover product, and its caveats. Null until the model has been built.",
    )


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


class ComponentScoreResponse(BaseModel):
    """One input to the priority score, with its own factor decomposition."""

    model_config = ConfigDict(frozen=True)

    value: float = Field(ge=0.0, le=1.0)
    formula_id: str
    factors: list[FactorContribution]
    note: str | None = None


class PhaseDecision(BaseModel):
    """Which relocation phase a habitation falls in, and exactly why."""

    model_config = ConfigDict(frozen=True)

    phase: PhaseTier
    reason: str
    rules_applied: list[str] = Field(
        default_factory=list,
        description="Override rules that fired, named. An escalation is never silent.",
    )
    pending_checks: list[str] = Field(
        default_factory=list,
        description="Constraint checks that belong in this decision but whose engine "
        "has not been built yet. Listed rather than left implicit.",
    )


class HabitationPriorityRow(BaseModel):
    """A habitation's full assessment: hazard, exposure, vulnerability, history."""

    model_config = ConfigDict(frozen=True)

    rank: int
    habitation_id: str
    name: str
    population: int
    households: int
    centroid: GeoPoint
    elevation_m: float | None

    priority_score: float = Field(ge=0.0, le=100.0)
    priority_factors: list[FactorContribution]

    hazard: CompositeHazard
    hazard_component: ComponentScoreResponse
    footprint_mean_composite: float
    footprint_max_composite: float
    footprint_radius_m: float

    exposure: ComponentScoreResponse
    vulnerability: ComponentScoreResponse
    history: ComponentScoreResponse

    confidence: ConfidenceReport
    zone_class: ZoneClass
    zone_id: str | None
    phase: PhaseDecision


class PhaseTotals(BaseModel):
    model_config = ConfigDict(frozen=True)

    habitations: int
    population: int
    households: int


class HabitationPriorityResponse(BaseModel):
    """The ranked decision list behind the Habitation Priority screen."""

    model_config = ConfigDict(frozen=True)

    habitations: list[HabitationPriorityRow]
    totals_by_phase: dict[str, PhaseTotals]
    total_population_assessed: int
    weights: dict[str, float]
    tier_thresholds: dict[str, float]
    classification_label: str
    decision_authority: str
    scenario_disclaimer: str
    priority_note: str
    history_note: str
    computed_at: datetime
    model_config_version: str
    engine_version: str


class HabitationDetailResponse(BaseModel):
    """Everything behind one habitation's ranking, for the reasoning drawer."""

    model_config = ConfigDict(frozen=True)

    row: HabitationPriorityRow
    habitation: Habitation
    explanation: ValueExplanation
    priority_formula: FormulaSpec
    exposure_formula: FormulaSpec
    vulnerability_formula: FormulaSpec
    history_formula: FormulaSpec
    peers_above: list[str] = Field(
        description="Habitations ranked immediately above this one, for context."
    )
    peers_below: list[str]


class UsableAreaResponse(BaseModel):
    """Buildable ground at a site, and exactly how it was measured."""

    model_config = ConfigDict(frozen=True)

    usable_m2: float
    usable_ha: float
    measured_m2: float
    radius_m: float
    buildable_fraction: float
    slope_pass_fraction: float
    flood_pass_fraction: float
    footprint_mean_slope_deg: float
    footprint_mean_hand_m: float
    method: str
    confidence: ConfidenceBand
    refinement_agreement: float | None = None
    refinement_note: str | None = None


class InterventionResponse(BaseModel):
    """One unit of investment and the capacity it actually unlocks."""

    model_config = ConfigDict(frozen=True)

    service: ServiceType
    description: str
    unit_size: float
    unit: str
    capacity_before: float
    capacity_after: float
    capacity_gain: float
    next_bottleneck: ServiceType | None
    next_bottleneck_capacity: float | None
    unlocks: bool


class SiteCapacityResponse(BaseModel):
    """A candidate site's suitability, capacity, bottleneck and interventions."""

    model_config = ConfigDict(frozen=True)

    site_id: str
    name: str
    centroid: GeoPoint
    elevation_m: float
    distance_to_road_m: float
    recorded_parcel_area_m2: float

    suitable: bool
    gates: list[GateResult]
    failed_gates: list[str]

    usable_area: UsableAreaResponse
    services: list[ServiceCapacity]
    theoretical_capacity: float
    effective_capacity: float
    bottleneck: ServiceType | None
    interventions: list[InterventionResponse]
    marginal_headline: str | None

    pending_constraints: list[str]
    limitation: str


class SiteCapacityListResponse(BaseModel):
    """Every candidate site, with the district totals a planner needs first."""

    model_config = ConfigDict(frozen=True)

    sites: list[SiteCapacityResponse]
    suitable_sites: int
    total_effective_capacity: float
    total_theoretical_capacity: float
    population_needing_relocation: int
    unmet_demand: float
    bottleneck_counts: dict[str, int]
    norms: list[Constant]
    decision_authority: str
    limitation: str
    model_config_version: str
    engine_version: str

# ---------------------------------------------------------------------------
# Engine 5 - route reliability and survivability
# ---------------------------------------------------------------------------


class SegmentLegResponse(BaseModel):
    """One stretch of road as travelled, with its own contribution to the risk."""

    model_config = ConfigDict(frozen=True)

    segment_id: str
    name: str | None
    road_class: RoadClass
    length_m: float
    travel_time_min: float
    hazard_max: float
    hazard_coverage: float = 1.0
    is_bridge: bool
    p_fail: float


class PointOfFailureResponse(BaseModel):
    """A stretch of road whose loss on its own decides whether the journey happens."""

    model_config = ConfigDict(frozen=True)

    segment_id: str
    name: str | None
    reason: str
    p_fail: float
    length_m: float
    no_alternative: bool


class RouteResponse(BaseModel):
    """One evaluated journey under one routing objective."""

    model_config = ConfigDict(frozen=True)

    origin_id: str
    destination_id: str
    profile: RouteProfile
    travel_time_min: float
    distance_km: float
    reliability: float = Field(
        description="Product over segments of (1 - p_fail). A survivability figure, "
        "not a confidence in the estimate."
    )
    risk: float
    off_network_m: float
    off_network_min: float
    hazard_segment_count: int
    hazard_exposed_km: float
    longest_hazard_run_km: float
    bridges_crossed: int
    feasible: bool
    scored_share: float = Field(
        description="Share of this route, by length, that runs over ground ASTRA "
        "scored. Below one, part of the road leaves the study area."
    )
    infeasible_reason: str | None
    legs: list[SegmentLegResponse]
    points_of_failure: list[PointOfFailureResponse]
    geometry: list[list[float]] = Field(
        description="The route drawn end to end as [lon, lat] pairs."
    )
    provenance: ProvenanceClass


class RoutePairResponse(BaseModel):
    """Fastest and safest for one habitation-site pair, with the trade stated."""

    model_config = ConfigDict(frozen=True)

    origin_id: str
    destination_id: str
    fastest: RouteResponse
    safest: RouteResponse
    profiles_differ: bool
    minutes_paid: float
    reliability_gained: float
    tradeoff: str
    feasible: bool


class SiteAccessResponse(BaseModel):
    """What the road network means for one candidate site."""

    model_config = ConfigDict(frozen=True)

    site_id: str
    name: str
    reachable_habitations: int
    feasible_habitations: int
    usable_routes: int
    best_reliability: float
    median_travel_time_min: float
    access_capacity_persons: float
    population_with_feasible_route: int


class RouteMatrixRow(BaseModel):
    """One habitation's options, ranked by the reliability it can actually get."""

    model_config = ConfigDict(frozen=True)

    habitation_id: str
    habitation_name: str
    population: int
    site_id: str
    site_name: str
    travel_time_min: float
    distance_km: float
    reliability: float
    feasible: bool
    site_suitable: bool
    bridges_crossed: int
    hazard_exposed_km: float
    points_of_failure: int


class NetworkSummaryResponse(BaseModel):
    """The graph itself: what was built, and how much choice it offers."""

    model_config = ConfigDict(frozen=True)

    nodes: int
    segments: int
    bridge_segments: int
    total_length_km: float
    segments_by_class: dict[str, int]
    unrouted_ways: int
    unscored_segments: int = Field(
        description="Road segments dropped from the graph because they lie outside "
        "the scored hazard surface. Routing over them would assume an unscored road "
        "is a safe one."
    )
    independent_loops: int = Field(
        description="Cycle rank of the network: how many genuinely alternative ways "
        "through it exist. A tree has none."
    )
    segments_without_alternative: int
    share_without_alternative: float
    redundancy_note: str


class RouteAssessmentResponse(BaseModel):
    """Every habitation-to-site pair under one set of closures."""

    model_config = ConfigDict(frozen=True)

    network: NetworkSummaryResponse
    closed_segments: list[str]
    rows: list[RouteMatrixRow]
    access: list[SiteAccessResponse]
    pairs_evaluated: int
    feasible_pairs: int
    habitations_with_a_reachable_suitable_site: int
    route_blocked_habitations: list[str]
    reliability_threshold: float
    profiles_differ_count: int
    constants: list[Constant]
    decision_authority: str
    model_config_version: str
    engine_version: str


class ClosureRequest(BaseModel):
    """Ask what the corridor looks like with these road segments shut."""

    model_config = ConfigDict(frozen=True)

    closed_segments: list[str] = Field(
        default_factory=list,
        description="Segment identifiers to close, as returned on route legs.",
    )


class RouteDeltaRow(BaseModel):
    """How one pair changed between the open network and the closed one."""

    model_config = ConfigDict(frozen=True)

    habitation_id: str
    site_id: str
    reliability_before: float
    reliability_after: float
    travel_time_before_min: float
    travel_time_after_min: float
    feasible_before: bool
    feasible_after: bool
    became_unreachable: bool


class ClosureImpactResponse(BaseModel):
    """The before-and-after of a closure, as two real assessments compared."""

    model_config = ConfigDict(frozen=True)

    closed_segments: list[str]
    closed_segment_detail: list[SegmentLegResponse]
    assessment: RouteAssessmentResponse
    changed: list[RouteDeltaRow]
    newly_infeasible: int
    newly_unreachable: int
    population_losing_a_reachable_site: int
    headline: str
