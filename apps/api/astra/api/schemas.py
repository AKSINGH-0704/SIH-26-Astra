"""Response envelopes for the public API.

Every response is a declared Pydantic model so the OpenAPI schema is complete and
``packages/contracts`` can be generated from it. The frontend imports those
generated types and renders what it is given; it never redeclares a shape or
recomputes a number (CLAUDE.md section 2.4).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from astra.domain.model_config import AstraModelConfig, Constant
from astra.domain.models import DatasetRecord, LayerDescriptor, Scenario, StudyArea
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
