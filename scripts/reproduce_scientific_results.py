#!/usr/bin/env python
"""Reproduce the scientific validation artifacts for the project."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = PROJECT_ROOT / "results" / "scientific_reproduction_summary.json"


WORKFLOWS = [
    {
        "name": "ald_proxy_catalog",
        "description": "Controlled ALD-inspired proxy model catalog",
        "command": ["scripts/prepare_ald_proxy_models.py", "--check-load"],
    },
    {
        "name": "h2_pipeline",
        "description": "H2 HF, FCI, local diagonalization and fallback VQE",
        "command": ["scripts/validate_h2_pipeline.py"],
    },
    {
        "name": "h2_energy_curve",
        "description": "H2 potential-energy curve",
        "command": ["scripts/run_h2_energy_curve.py"],
    },
    {
        "name": "lih_casci",
        "description": "LiH reduced CASCI active-space validation",
        "command": ["scripts/validate_lih_pipeline.py"],
    },
    {
        "name": "h2_jordan_wigner",
        "description": "H2 Jordan-Wigner fixed-particle-sector validation",
        "command": ["scripts/validate_jw_h2.py"],
    },
    {
        "name": "h2_qiskit_vqe",
        "description": "H2 noiseless Qiskit statevector VQE",
        "command": ["scripts/run_h2_qiskit_vqe.py"],
    },
    {
        "name": "h2_noisy_vqe_mitigation",
        "description": "H2 analytic noisy VQE with ZNE and CDR",
        "command": ["scripts/run_h2_noisy_vqe.py"],
    },
]


def _classify(returncode: int, output: str) -> str:
    if "optional dependency" in output.lower() and "is required for this feature" in output.lower():
        return "SKIPPED"
    if returncode != 0:
        return "FAIL"
    if "skipped" in output.lower():
        return "SKIPPED"
    if "status: check" in output.lower():
        return "CHECK"
    return "PASS"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def run_reproduction(
    workflows: list[dict[str, Any]] | None = None,
    strict: bool = False,
    summary_path: Path = SUMMARY_PATH,
) -> dict[str, Any]:
    """Run all configured validation workflows and write a reproducibility manifest."""
    workflows = workflows or WORKFLOWS
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    env = os.environ.copy()
    env.setdefault("MPLCONFIGDIR", str(Path("/tmp") / "quantum_ald_matplotlib"))
    for workflow in workflows:
        command = [sys.executable, *workflow["command"]]
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        output = completed.stdout + completed.stderr
        status = _classify(completed.returncode, output)
        results.append(
            {
                "name": workflow["name"],
                "description": workflow["description"],
                "command": command,
                "returncode": completed.returncode,
                "status": status,
                "stdout_tail": completed.stdout[-4000:],
                "stderr_tail": completed.stderr[-4000:],
            }
        )

    failed = [item for item in results if item["status"] == "FAIL"]
    skipped = [item for item in results if item["status"] == "SKIPPED"]
    checks = [item for item in results if item["status"] == "CHECK"]
    if failed or (strict and (skipped or checks)):
        overall_status = "FAIL"
    elif skipped or checks:
        overall_status = "PARTIAL"
    else:
        overall_status = "PASS"

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_executable": sys.executable,
        "project_root": str(PROJECT_ROOT),
        "strict": strict,
        "overall_status": overall_status,
        "counts": {
            "pass": sum(item["status"] == "PASS" for item in results),
            "check": len(checks),
            "skipped": len(skipped),
            "fail": len(failed),
        },
        "workflows": results,
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return failure if optional scientific workflows are skipped or marked CHECK.",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=SUMMARY_PATH,
        help="Path for the JSON reproduction summary.",
    )
    args = parser.parse_args(argv)

    summary = run_reproduction(strict=args.strict, summary_path=args.summary_path)
    print("Scientific reproduction")
    print("-----------------------")
    print(f"Overall status: {summary['overall_status']}")
    for item in summary["workflows"]:
        print(f"{item['status']:7s} {item['name']} - {' '.join(item['command'])}")
    print(f"Summary saved to: {_display_path(args.summary_path)}")
    return 0 if summary["overall_status"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
