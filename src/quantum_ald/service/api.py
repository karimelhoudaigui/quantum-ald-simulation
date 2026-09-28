"""FastAPI adapter for the synchronous scientific experiment facade."""

from __future__ import annotations

import os
from typing import Any

from fastapi import Body, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from ..experiment import SCHEMA_VERSION
from .jobs import ChemistryJobManager

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def _max_workers() -> int:
    raw = os.getenv("QUANTUM_ALD_MAX_WORKERS", "1")
    try:
        workers = int(raw)
    except ValueError as exc:
        raise ValueError("QUANTUM_ALD_MAX_WORKERS must be an integer") from exc
    if workers < 1:
        raise ValueError("QUANTUM_ALD_MAX_WORKERS must be at least one")
    return workers


def _cors_origins() -> list[str]:
    raw = os.getenv("QUANTUM_ALD_CORS_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    if not origins:
        origins = list(DEFAULT_CORS_ORIGINS)
    if "*" in origins:
        raise ValueError("QUANTUM_ALD_CORS_ORIGINS must list explicit origins")
    return origins


def create_app(job_manager: ChemistryJobManager | None = None) -> FastAPI:
    manager = job_manager or ChemistryJobManager(max_workers=_max_workers())
    application = FastAPI(
        title="Quantum ALD Chemistry API",
        description="Thin asynchronous adapter around run_experiment().",
        version="0.1.0",
    )
    application.state.chemistry_jobs = manager
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.get("/api/chemistry/health")
    def chemistry_health() -> dict[str, str]:
        return {"status": "ok", "schema_version": SCHEMA_VERSION}

    @application.get("/")
    def service_root() -> dict[str, str]:
        return {
            "service": "quantum-ald-chemistry-api",
            "status": "ok",
            "schema_version": SCHEMA_VERSION,
        }

    @application.post(
        "/api/chemistry/experiments",
        status_code=status.HTTP_202_ACCEPTED,
    )
    def submit_experiment(
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        job = manager.submit(payload)
        return {"job_id": job["job_id"], "status": job["status"]}

    @application.get("/api/chemistry/experiments/{job_id}")
    def get_experiment(job_id: str) -> dict[str, Any]:
        try:
            return manager.get(job_id)
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "job_not_found",
                    "field": "job_id",
                    "message": f"chemistry job not found: {job_id}",
                },
            ) from exc

    return application


app = create_app()
