"""Reuse your own code from an earlier exercise.

Each exercise builds on the previous one, so exercise 02 imports *your* exercise 01
agent instead of a copy. That happens silently. If your earlier code isn't usable yet
(it's unfinished, or it doesn't load), the exercise falls back to the course's
reference version and prints one line saying why, so you can still work on the new one.

Set the environment variable ``USE_REFERENCE=1`` to always use the reference version.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable

REPO = Path(__file__).resolve().parents[1]
TODO_MARKER = 'raise NotImplementedError("TODO(student)'
_loaded: dict[tuple, ModuleType] = {}  # each earlier module is loaded once per run
_inside_reference = 0  # > 0 while a reference copy is loading: its own earlier loads stay quiet


def load_previous(
    exercise: str,
    module: str,
    *,
    reference_dir: Path | None = None,
    repo_root: Path = REPO,
    required: tuple[str, ...] = (),
    log: Callable[[str], None] = print,
) -> ModuleType:
    """Load ``exercises/<exercise>/starter/<module>.py`` (yours), else the reference copy.

    The reference for exercise NN lives in the *next* exercise's ``reference/`` folder
    (e.g. exercise 01's in ``exercises/02-…/reference``), unless ``reference_dir`` says otherwise.
    ``required`` names (e.g. ``("run_agent",)``) must exist in your module, or the reference is used.
    """
    key = (exercise, module, str(repo_root), os.environ.get("USE_REFERENCE") == "1")
    if key not in _loaded:
        _loaded[key] = _load_own_or_reference(exercise, module, reference_dir, repo_root, required, log)
    return _loaded[key]


def _load_own_or_reference(exercise, module, reference_dir, repo_root, required, log) -> ModuleType:
    """Your module if it's usable (silently), else the reference with one line saying why."""
    global _inside_reference
    own = repo_root / "exercises" / exercise / "starter" / f"{module}.py"
    reason = _why_not_own(own)
    if reason is None:
        try:
            loaded = load_module(own, f"{exercise}_own_{module}")
            missing = [name for name in required if not hasattr(loaded, name)]
            if not missing:
                return loaded
            reason = f"yours has no {', '.join(missing)}"
        except Exception as err:  # any import-time failure means: use the reference instead
            reason = f"yours doesn't load: {type(err).__name__}: {err}"
    if not _inside_reference:  # one line per file *you* depend on, not for the reference's own imports
        log(f"(using the reference exercise {exercise[:2]} {module}.py, because {reason})")
    reference_dir = reference_dir or _reference_dir(exercise, repo_root)
    _inside_reference += 1
    try:
        return load_module(reference_dir / f"{module}.py", f"{exercise}_reference_{module}")
    finally:
        _inside_reference -= 1


def _reference_dir(exercise: str, repo_root: Path) -> Path:
    next_exercise = f"{int(exercise[:2]) + 1:02d}"
    following = sorted((repo_root / "exercises").glob(f"{next_exercise}-*/reference"))
    if not following:
        raise FileNotFoundError(f"No reference copy of exercise {exercise} (expected exercises/"
                                f"{next_exercise}-*/reference). Ask the course staff.")
    return following[0]


def _why_not_own(path: Path) -> str | None:
    if os.environ.get("USE_REFERENCE") == "1":
        return "USE_REFERENCE=1 is set"
    if not path.is_file():
        return f"{path.name} was not found in your exercise folder"
    if TODO_MARKER in path.read_text(encoding="utf-8", errors="replace"):
        return "yours still has unfinished TODO(student) parts"
    return None


def load_module(path: Path, name: str) -> ModuleType:
    """Import a Python file by its path, under a unique module name (used by the tests too)."""
    unique = name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(unique, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[unique] = loaded  # dataclasses look their module up while loading
    try:
        spec.loader.exec_module(loaded)
    except Exception:
        del sys.modules[unique]
        raise
    return loaded
