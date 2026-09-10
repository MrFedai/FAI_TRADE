"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.logging_config import configure_logging, get_logger
from backend.database import close_engine

configure_logging()
logger = get_logger("backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    logger.info("application_starting", env=settings.app_env)
    yield
    logger.info("application_stopping")
    await close_engine()
    logger.info("application_stopped")


app = FastAPI(
    title="Trading Intelligence System",
    description="Personal Trading Intelligence API — Decision Support Only",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "env": settings.app_env}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Trading Intelligence System",
        "version": "0.1.0",
        "description": "Personal Trading Intelligence API — Decision Support Only",
    }
