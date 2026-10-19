"""Load a starter or, when CHALLENGE_SOLUTIONS=hidden, the matching solution."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_challenge(slug: str):
    if os.environ.get("CHALLENGE_SOLUTIONS") == "hidden":
        path = ROOT / "hidden" / f"{slug}.py"
    else:
        path = ROOT / slug / "starter.py"
    spec = importlib.util.spec_from_file_location(f"challenge_{slug}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
