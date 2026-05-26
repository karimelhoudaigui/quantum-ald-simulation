"""Utilities for optional scientific dependencies."""

from __future__ import annotations

import importlib
from types import ModuleType


def require_module(module_name: str, extra: str) -> ModuleType:
    """Import an optional module or raise a helpful installation message."""
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError(
            f"Optional dependency '{module_name}' is required for this feature. "
            f"Install it with `pip install -e '.[{extra}]'` or use environment.yml."
        ) from exc
