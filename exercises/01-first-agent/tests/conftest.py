"""Loads the code under test for this exercise.

By default the tests check *your* code in ``starter/``. (The course staff can point
them at other folders with the EXERCISE_TARGET environment variable.)
"""
from __future__ import annotations

import importlib.util
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
    unique = f"{EXERCISE_DIR.name.replace('-', '_')}_{target}_{module_name}"
    spec = importlib.util.spec_from_file_location(unique, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique] = module  # dataclasses look their module up while loading
    spec.loader.exec_module(module)
    return module


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
