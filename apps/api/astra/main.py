"""ASTRA API application.

Startup runs the fixture integrity gate. If the gate fails the application does
not start (CLAUDE.md section 4.5): serving a plan computed from a broken dataset
is a worse outcome than a service that refuses to come up and says why.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from astra import __version__
from astra.api.capacity_router import router as capacity_router
from astra.api.priority_router import router as priority_router
from astra.api.risk_router import router as risk_router
from astra.api.routers import router
from astra.data.validate import FixtureValidationError, enforce, validate_all
from astra.domain.notices import HOW_THIS_WORKS
from astra.settings import get_settings

logger = logging.getLogger("astra")

DESCRIPTION = f"""
ASTRA - Proactive Settlement Risk & Relocation Intelligence.

{HOW_THIS_WORKS}

Decision-support output. Final relocation decisions rest with the SDMA /
District Authority. Habitation and candidate-site records in the demonstration
scenario are synthetic and terrain-calibrated, and are not an official hazard
designation of any real settlement.
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if settings.validate_fixtures_on_startup:
        try:
            report = enforce()
        except FixtureValidationError as exc:
            for error in exc.report.errors:
                logger.error("fixture validation: %s", error)
            raise
    else:
        report = validate_all()
        logger.warning("fixture validation gate disabled by configuration")
    for warning in report.warnings:
        logger.warning("fixture validation: %s", warning)
    # Warm the baseline hazard run so the first request is not the slow one.
    try:
        from astra.engines.service import baseline_risk

        run = baseline_risk()
        logger.info(
            "hazard engine warm: %d zones over a %dx%d grid in %.0f ms",
            len(run.zones),
            run.grid.rows,
            run.grid.cols,
            run.computed_ms,
        )
        from astra.api.priority_router import baseline_priority
        from astra.engines.capacity_service import baseline_capacity

        sites = baseline_capacity()
        logger.info(
            "capacity engine warm: %d of %d candidate sites pass every gate",
            sum(1 for entry in sites if entry.suitable),
            len(sites),
        )
        ranking = baseline_priority()
        logger.info(
            "priority engine warm: %d habitations ranked, top %s at %.1f",
            len(ranking.rows),
            ranking.rows[0].habitation.id if ranking.rows else "-",
            ranking.rows[0].priority_score if ranking.rows else 0.0,
        )
    except Exception as exc:  # noqa: BLE001 - the API still serves without it
        logger.warning(
            "hazard engine could not warm (%s); risk endpoints will report the cause",
            exc,
        )
    logger.info("astra api %s ready - %s", __version__, report.summary())
    logger.info("llm narration mode: %s", settings.llm_mode)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ASTRA API",
        version=__version__,
        description=DESCRIPTION,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.include_router(risk_router)
    app.include_router(priority_router)
    app.include_router(capacity_router)
    return app


app = create_app()
