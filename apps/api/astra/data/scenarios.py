"""Scenario definitions.

Scenarios are first-class, versioned objects rather than UI toggles (CLAUDE.md
section 5.7). The baseline is defined here; perturbed scenarios created through
``POST /simulate`` are persisted alongside it from the scenario slice onwards.
"""

from __future__ import annotations

from datetime import UTC, datetime

from astra.data.study_area import DEFAULT_STUDY_AREA_ID
from astra.domain.models import Scenario
from astra.domain.notices import SCENARIO_DISCLAIMER

BASELINE_CREATED_AT = datetime(2026, 9, 9, 0, 0, 0, tzinfo=UTC)
"""Fixed so the baseline scenario is byte-identical across runs and machines."""

BASELINE = Scenario(
    id="baseline",
    name="Baseline - current conditions",
    description=(
        "Current-conditions assessment of the Alaknanda valley corridor: observed "
        "terrain and hydrology, recorded incident history and normal-season rainfall, "
        "with no perturbation applied."
    ),
    study_area_id=DEFAULT_STUDY_AREA_ID,
    is_baseline=True,
    created_at=BASELINE_CREATED_AT,
    disclaimer=SCENARIO_DISCLAIMER,
    perturbations={},
)

SCENARIOS: dict[str, Scenario] = {BASELINE.id: BASELINE}

DEFAULT_SCENARIO_ID = BASELINE.id


def get_scenario(scenario_id: str) -> Scenario | None:
    return SCENARIOS.get(scenario_id)


def list_scenarios() -> list[Scenario]:
    return list(SCENARIOS.values())
