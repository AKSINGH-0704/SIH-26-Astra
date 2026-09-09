"""HTTP routers.

Endpoints are added as the slice that produces their data lands. An endpoint
that would return an empty list because its engine has not been built yet is not
registered at all - a judge clicking through the API should never meet a hollow
route (CLAUDE.md section 2.3).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from astra import __version__
from astra.api.schemas import (
    LayersResponse,
    ModelConfigResponse,
    ProvenanceResponse,
    ScenarioListResponse,
    ScenarioResponse,
    ValidationCheckResponse,
)
from astra.data.layers import LAYER_CATALOGUE
from astra.data.provenance import get_registry
from astra.data.scenarios import get_scenario, list_scenarios
from astra.data.study_area import STUDY_AREAS, get_study_area
from astra.data.validate import validate_all
from astra.domain.model_config import (
    ENGINE_VERSION,
    MODEL_CONFIG,
    MODEL_CONFIG_VERSION,
)
from astra.domain.models import HealthStatus
from astra.domain.notices import NOTICES
from astra.domain.registry import FORMULAS
from astra.settings import get_settings

router = APIRouter()

STARTED_AT = datetime.now(UTC)


@router.get("/health", response_model=HealthStatus, tags=["system"])
def health() -> HealthStatus:
    """Liveness plus the honest system state the UI header renders."""
    report = validate_all()
    settings = get_settings()
    return HealthStatus(
        status="ok" if report.ok else "degraded",
        api_version=__version__,
        engine_version=ENGINE_VERSION,
        model_config_version=MODEL_CONFIG_VERSION,
        environment=settings.env,
        fixtures_valid=report.ok,
        fixture_count=report.fixture_count,
        llm_mode=settings.llm_mode,  # type: ignore[arg-type]
        started_at=STARTED_AT,
        checked_at=datetime.now(UTC),
    )


@router.get("/model/config", response_model=ModelConfigResponse, tags=["transparency"])
def model_config() -> ModelConfigResponse:
    """Every weight, threshold, norm and formula ASTRA uses, with provenance."""
    return ModelConfigResponse(
        config=MODEL_CONFIG,
        constants=MODEL_CONFIG.constants(),
        formulas=sorted(FORMULAS.values(), key=lambda spec: spec.formula_id),
        notices=NOTICES,
    )


@router.get("/provenance", response_model=ProvenanceResponse, tags=["transparency"])
def provenance() -> ProvenanceResponse:
    """The dataset registry: real, derived, synthetic and demo-config, unblended."""
    registry = get_registry()
    settings = get_settings()
    payload = json.loads(settings.provenance_path.read_text(encoding="utf-8"))
    return ProvenanceResponse(
        registry_version=payload.get("registry_version", "unknown"),
        datasets=registry.records,
        counts_by_class=registry.counts(),
        note=payload.get("note", ""),
    )


@router.get("/layers", response_model=LayersResponse, tags=["transparency"])
def layers() -> LayersResponse:
    """The layer catalogue. Layers not yet produced are declared but unavailable."""
    return LayersResponse(
        layers=LAYER_CATALOGUE,
        available_count=sum(1 for layer in LAYER_CATALOGUE if layer.available),
        declared_count=len(LAYER_CATALOGUE),
    )


@router.get("/validation/fixtures", response_model=ValidationCheckResponse, tags=["transparency"])
def fixture_validation() -> ValidationCheckResponse:
    """The integrity gate result, visible in the interface rather than buried in a log."""
    report = validate_all()
    return ValidationCheckResponse(
        ok=report.ok,
        summary=report.summary(),
        checks=report.checked,
        errors=report.errors,
        warnings=report.warnings,
        fixture_count=report.fixture_count,
        dataset_count=report.dataset_count,
    )


@router.get("/scenarios", response_model=ScenarioListResponse, tags=["scenarios"])
def scenarios() -> ScenarioListResponse:
    return ScenarioListResponse(
        scenarios=list_scenarios(),
        study_areas=list(STUDY_AREAS.values()),
    )


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse, tags=["scenarios"])
def scenario_detail(scenario_id: str) -> ScenarioResponse:
    scenario = get_scenario(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail=f"unknown scenario '{scenario_id}'")
    return ScenarioResponse(
        scenario=scenario,
        study_area=get_study_area(scenario.study_area_id),
    )
