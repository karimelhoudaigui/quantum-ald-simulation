#!/usr/bin/env python
"""Serve the asynchronous chemistry API for local frontend development."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8002")))
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args(argv)

    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "FastAPI service dependencies are required; install with .[service]"
        ) from exc

    uvicorn.run(
        "quantum_ald.service.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        app_dir=str(SRC_DIR),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
