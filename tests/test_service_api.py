from __future__ import annotations

from importlib.util import find_spec
import json
from pathlib import Path
from threading import Event
from time import monotonic, sleep

from fastapi.testclient import TestClient
import pytest

from quantum_ald.service.api import create_app
from quantum_ald.service.jobs import ChemistryJobManager

PROJECT_ROOT = Path(__file__).resolve().parents[1]
H2_REQUEST = json.loads(
    (PROJECT_ROOT / "results" / "experiments" / "h2" / "request.json").read_text(encoding="utf-8")
)
TERMINAL = {"completed", "partial", "failed", "invalid_configuration"}
SCIENTIFIC_RUNTIME_AVAILABLE = all(
    find_spec(module_name) is not None
    for module_name in ("openfermion", "pyscf", "qiskit", "qiskit_nature")
)


def _wait_for_job(client: TestClient, job_id: str, timeout: float = 20.0) -> dict:
    deadline = monotonic() + timeout
    while monotonic() < deadline:
        response = client.get(f"/api/chemistry/experiments/{job_id}")
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in TERMINAL:
            return payload
        sleep(0.02)
    raise AssertionError(f"chemistry job did not finish within {timeout} seconds")


@pytest.fixture(scope="module")
def real_api():
    manager = ChemistryJobManager(max_workers=1)
    with TestClient(create_app(manager)) as client:
        yield client
    manager.shutdown()


def test_chemistry_health(real_api: TestClient) -> None:
    response = real_api.get("/api/chemistry/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "schema_version": "1"}


def test_service_root(real_api: TestClient) -> None:
    response = real_api.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "quantum-ald-chemistry-api",
        "status": "ok",
        "schema_version": "1",
    }


def test_pages_origin_is_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "QUANTUM_ALD_CORS_ORIGINS",
        "https://karimelhoudaigui.github.io",
    )
    manager = ChemistryJobManager()
    try:
        with TestClient(create_app(manager)) as client:
            response = client.options(
                "/api/chemistry/experiments",
                headers={
                    "Origin": "https://karimelhoudaigui.github.io",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                },
            )
    finally:
        manager.shutdown()

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "https://karimelhoudaigui.github.io"
    )


def test_unknown_chemistry_job_is_structured(real_api: TestClient) -> None:
    response = real_api.get("/api/chemistry/experiments/missing")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "job_not_found"


@pytest.mark.skipif(
    not SCIENTIFIC_RUNTIME_AVAILABLE,
    reason="scientific runtime dependencies are not installed",
)
def test_real_h2_experiment_submission_and_polling(real_api: TestClient) -> None:
    submitted = real_api.post("/api/chemistry/experiments", json=H2_REQUEST)

    assert submitted.status_code == 202
    assert submitted.json()["status"] in {"queued", "running"}
    job = _wait_for_job(real_api, submitted.json()["job_id"])

    assert job["status"] == "completed"
    assert job["progress"] == 100
    assert job["result"]["experiment_id"] == "exp_0f901ebf2d8ec00872760281"
    assert job["result"]["requested_methods"] == ["hf", "casci", "fci", "vqe"]
    assert job["result"]["executed_methods"] == job["result"]["requested_methods"]
    assert job["completed_active_spaces"] == 1
    assert all(step["status"] == "completed" for step in job["steps"])


def test_invalid_experiment_becomes_terminal_job(real_api: TestClient) -> None:
    invalid = {**H2_REQUEST, "methods": ["qpe"]}
    submitted = real_api.post("/api/chemistry/experiments", json=invalid)
    job = _wait_for_job(real_api, submitted.json()["job_id"])

    assert job["status"] == "invalid_configuration"
    assert job["error"]["code"] == "unsupported_method"
    assert job["steps"][0]["status"] == "failed"
    assert job["result"] is None


class _FakeResult:
    def __init__(self, status: str) -> None:
        self.status = status

    def to_dict(self) -> dict:
        return {
            "schema_version": "1",
            "experiment_id": "exp_test",
            "status": self.status,
            "errors": [],
            "warnings": [],
            "comparison_table": [],
        }


def test_partial_result_is_preserved() -> None:
    def partial_runner(_config, progress_callback):
        progress_callback(
            {
                "phase": "comparison",
                "status": "completed",
                "progress": 100,
                "completed_active_spaces": 1,
                "total_active_spaces": 2,
            }
        )
        return _FakeResult("partial")

    manager = ChemistryJobManager(experiment_runner=partial_runner)
    try:
        with TestClient(create_app(manager)) as client:
            submitted = client.post("/api/chemistry/experiments", json=H2_REQUEST)
            job = _wait_for_job(client, submitted.json()["job_id"])
    finally:
        manager.shutdown()

    assert job["status"] == "partial"
    assert job["result"]["status"] == "partial"
    assert job["completed_active_spaces"] == 1


def test_unexpected_runner_failure_is_structured() -> None:
    def failed_runner(_config, progress_callback):
        progress_callback({"phase": "vqe", "status": "running", "progress": 70})
        raise RuntimeError("deliberate worker failure")

    manager = ChemistryJobManager(experiment_runner=failed_runner)
    try:
        with TestClient(create_app(manager)) as client:
            submitted = client.post("/api/chemistry/experiments", json=H2_REQUEST)
            job = _wait_for_job(client, submitted.json()["job_id"])
    finally:
        manager.shutdown()

    assert job["status"] == "failed"
    assert job["error"]["code"] == "experiment_failed"
    assert "deliberate worker failure" in job["error"]["message"]


def test_job_lifecycle_reports_running_before_completion() -> None:
    entered = Event()
    release = Event()

    def blocking_runner(_config, progress_callback):
        progress_callback({"phase": "vqe", "status": "running", "progress": 70})
        entered.set()
        assert release.wait(timeout=5)
        return _FakeResult("completed")

    manager = ChemistryJobManager(experiment_runner=blocking_runner)
    try:
        job_id = manager.submit(H2_REQUEST)["job_id"]
        assert entered.wait(timeout=2)
        running = manager.get(job_id)
        assert running["status"] == "running"
        assert running["steps"][4]["status"] == "running"
        release.set()
        deadline = monotonic() + 2
        while manager.get(job_id)["status"] not in TERMINAL and monotonic() < deadline:
            sleep(0.01)
        completed = manager.get(job_id)
    finally:
        release.set()
        manager.shutdown()

    assert completed["status"] == "completed"
    assert completed["progress"] == 100
