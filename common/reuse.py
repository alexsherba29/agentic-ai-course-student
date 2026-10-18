"""Reuse your own code from an earlier exercise.

Each exercise builds on the previous one, so exercise 02 imports *your* exercise 01
agent instead of a copy. If your earlier code isn't usable yet (it's unfinished,
or it doesn't load), the exercise falls back to the course's reference version and
tells you why, so you can still work on the new exercise.

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


def load_previous(
    exercise: str,
    module: str,
    *,
    reference_dir: Path,
    repo_root: Path = REPO,
    required: tuple[str, ...] = (),
    log: Callable[[str], None] = print,
) -> ModuleType:
    """Load ``exercises/<exercise>/starter/<module>.py`` (yours), else ``reference_dir/<module>.py``.

    ``required`` names (e.g. ``("run_agent",)``) must exist in your module, or the reference is used.
    """
    own = repo_root / "exercises" / exercise / "starter" / f"{module}.py"
    label = f"exercise {exercise[:2]} {module}.py"
    reason = _why_not_own(own)
    if reason is None:
        try:
            loaded = load_module(own, f"{exercise}_own_{module}")
            missing = [name for name in required if not hasattr(loaded, name)]
            if not missing:
                log(f"(using your {label})")
                return loaded
            reason = f"yours has no {', '.join(missing)}"
        except Exception as err:  # any import-time failure means: use the reference instead
            reason = f"yours doesn't load: {type(err).__name__}: {err}"
    log(f"(using the reference {label}, because {reason})")
    return load_module(reference_dir / f"{module}.py", f"{exercise}_reference_{module}")


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
