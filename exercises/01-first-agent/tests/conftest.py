"""Loads the code under test for this exercise.

By default the tests check *your* code in ``starter/``. (The course staff can point
them at other folders with the EXERCISE_TARGET environment variable.)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

EXERCISE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = EXERCISE_DIR.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load(module_name: str):
    target = os.environ.get("EXERCISE_TARGET", "starter")
    path = EXERCISE_DIR / target / f"{module_name}.py"
    if not path.exists():
        pytest.fail(f"Cannot find {path} — did you move or rename it?", pytrace=False)
    from common.reuse import load_module

    return load_module(path, f"{EXERCISE_DIR.name}_{target}_{module_name}")


@pytest.fixture(scope="session")
def agent_module():
    return _load("agent")


@pytest.fixture(scope="session")
def tools_module():
    return _load("tools")


@pytest.fixture(scope="session")
def demo_module():
    return _load("demo")


@pytest.fixture
def quiet():
    """A log function that collects lines instead of printing them."""
    lines: list[str] = []
    return lines.append
