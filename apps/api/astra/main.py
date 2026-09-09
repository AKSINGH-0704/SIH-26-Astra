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
    return app


app = create_app()
