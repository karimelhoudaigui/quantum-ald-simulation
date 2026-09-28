"""Thread-safe in-memory execution queue for chemistry experiments."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Callable
from uuid import uuid4

from ..experiment import ExperimentConfig, ExperimentConfigurationError, run_experiment

ExperimentRunner = Callable[..., Any]

_STEP_LABELS = {
    "validate": "Validate",
    "scf": "Molecule / SCF",
    "active_space": "Active space / CASCI",
    "mapping": "Fermionic / Jordan-Wigner",
    "vqe": "UCCSD / VQE",
    "comparison": "Compare",
}
_TERMINAL_STATUSES = {"completed", "partial", "failed", "invalid_configuration"}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _initial_steps() -> list[dict[str, Any]]:
    return [
        {
            "id": step_id,
            "label": label,
            "status": "pending",
            "message": None,
        }
        for step_id, label in _STEP_LABELS.items()
    ]


class ChemistryJobManager:
    """Run the validated synchronous facade behind a small in-memory queue."""

    def __init__(
        self,
        *,
        max_workers: int = 1,
        experiment_runner: ExperimentRunner = run_experiment,
    ) -> None:
        if max_workers < 1:
            raise ValueError("max_workers must be at least one")
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="quantum-ald-chemistry",
        )
        self._runner = experiment_runner
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def submit(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise TypeError("experiment payload must be a JSON object")
        job_id = f"chem_{uuid4().hex}"
        now = _timestamp()
        total_active_spaces = len(payload.get("active_spaces", []))
        job = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "steps": _initial_steps(),
            "current_active_space": None,
            "completed_active_spaces": 0,
            "total_active_spaces": total_active_spaces,
            "result": None,
            "error": None,
            "created_at_utc": now,
            "updated_at_utc": now,
        }
        with self._lock:
            self._jobs[job_id] = job
        self._executor.submit(self._execute, job_id, deepcopy(payload))
        return self.get(job_id)

    def get(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(job_id)
            return deepcopy(self._jobs[job_id])

    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait, cancel_futures=False)

    def _update(self, job_id: str, **changes: Any) -> None:
        with self._lock:
            job = self._jobs[job_id]
            changes["updated_at_utc"] = _timestamp()
            job.update(changes)

    def _set_step(
        self,
        job_id: str,
        step_id: str,
        status: str,
        message: str | None,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            for step in job["steps"]:
                if step["id"] == step_id:
                    step["status"] = status
                    step["message"] = message
                    break
            job["updated_at_utc"] = _timestamp()

    def _on_progress(self, job_id: str, event: dict[str, Any]) -> None:
        phase = str(event.get("phase", ""))
        step_id = "scf" if phase == "molecule" else phase
        status = str(event.get("status", "running"))
        if step_id in _STEP_LABELS and status in {"pending", "running", "completed", "failed"}:
            self._set_step(job_id, step_id, status, event.get("message"))

        with self._lock:
            job = self._jobs[job_id]
            progress = int(event.get("progress", job["progress"]))
            job["progress"] = max(job["progress"], min(100, max(0, progress)))
            for key in (
                "current_active_space",
                "completed_active_spaces",
                "total_active_spaces",
            ):
                if key in event:
                    job[key] = deepcopy(event[key])
            job["updated_at_utc"] = _timestamp()

    def _execute(self, job_id: str, payload: dict[str, Any]) -> None:
        self._update(job_id, status="running", progress=1)
        self._set_step(job_id, "validate", "running", "Validating ExperimentConfig")
        try:
            config = ExperimentConfig.from_dict(payload)
        except ExperimentConfigurationError as exc:
            self._set_step(job_id, "validate", "failed", exc.message)
            self._update(
                job_id,
                status="invalid_configuration",
                progress=100,
                error=exc.to_dict(),
            )
            return
        except Exception as exc:
            self._set_step(job_id, "validate", "failed", str(exc))
            self._update(
                job_id,
                status="invalid_configuration",
                progress=100,
                error={
                    "code": "invalid_experiment_config",
                    "field": "config",
                    "message": f"{type(exc).__name__}: {exc}",
                },
            )
            return

        self._set_step(job_id, "validate", "completed", "Configuration valid")
        self._update(
            job_id,
            progress=2,
            total_active_spaces=len(config.active_spaces),
        )
        try:
            result = self._runner(
                config,
                progress_callback=lambda event: self._on_progress(job_id, event),
            )
            payload_result = result.to_dict()
        except Exception as exc:
            current_step = self._running_step(job_id)
            if current_step is not None:
                self._set_step(job_id, current_step, "failed", str(exc))
            self._update(
                job_id,
                status="failed",
                progress=100,
                error={
                    "code": "experiment_failed",
                    "field": "experiment",
                    "message": f"{type(exc).__name__}: {exc}",
                },
            )
            return

        status = str(payload_result.get("status", "failed"))
        if status not in _TERMINAL_STATUSES:
            status = "failed"
        if status in {"completed", "partial"}:
            self._set_step(job_id, "comparison", "completed", "Results ready")
        elif status == "failed":
            self._set_step(job_id, "comparison", "failed", "Experiment failed")
        self._update(
            job_id,
            status=status,
            progress=100,
            result=payload_result,
            error=(payload_result.get("errors") or None) if status == "failed" else None,
        )

    def _running_step(self, job_id: str) -> str | None:
        with self._lock:
            for step in self._jobs[job_id]["steps"]:
                if step["status"] == "running":
                    return str(step["id"])
        return None
