"""Tasks that wait: what the agent wants to do, saved to a file until a human decides.

A task is "in progress" while it waits for approval. Because it's saved to a JSON
file, it survives the program stopping: one command drafts it, another approves or
rejects it, and a third continues the work. Open the file to see the state yourself.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from common.mocks.ticketing import APPROVED, DONE, FAILED, PENDING_APPROVAL, REJECTED

# Which status a task may move to next. Anything else is a bug, so move_to refuses it.
TRANSITIONS = {
    PENDING_APPROVAL: {APPROVED, REJECTED},  # a person decides
    APPROVED: {DONE, FAILED},  # the ticket was created, or the system couldn't be reached
    FAILED: {APPROVED},  # a person may approve it again, to try once more later
    REJECTED: set(),
    DONE: set(),
}


class TaskNotFound(KeyError):
    """No task with that id."""


@dataclass
class Task:
    task_id: str
    question: str  # what the user asked
    draft: dict  # the proposed ticket: title, description, priority
    status: str  # one of TASK_STATUSES in common/mocks/ticketing.py
    ticket_id: str | None = None  # set once the ticket really exists
    note: str = ""  # the reviewer's note when approving or rejecting
    history: list[str] = field(default_factory=list)  # one line per thing that happened

    def move_to(self, status: str, line: str) -> None:
        """Change the status, if TRANSITIONS allows it, and record why in the history."""
        if status not in TRANSITIONS[self.status]:
            allowed = ", ".join(sorted(TRANSITIONS[self.status])) or "nothing"
            raise ValueError(f"Task {self.task_id} can't go from {self.status!r} to {status!r} "
                             f"(from {self.status!r} it can go to: {allowed}).")
        self.status = status
        self.history.append(line)


class TaskStore:
    """Saves tasks in one JSON file (a list of tasks, oldest first).

    Only one program should write to the file at a time (here: run one command at a time).
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def list(self, status: str | None = None) -> list[Task]:
        return [t for t in self._read() if status is None or t.status == status]

    def get(self, task_id: str) -> Task:
        tasks = self._read()
        for task in tasks:
            if task.task_id == task_id:
                return task
        known = ", ".join(t.task_id for t in tasks) or "none yet"
        raise TaskNotFound(f"No task {task_id!r}. Known tasks: {known}")

    def new_id(self) -> str:
        """One more than the highest id so far, so an id is never handed out twice."""
        highest = max((int(t.task_id.split("-")[-1]) for t in self._read()), default=0)
        return f"T-{highest + 1:03d}"

    def save(self, task: Task) -> None:
        """Add the task, or replace the saved task with the same id."""
        tasks = [t for t in self._read() if t.task_id != task.task_id]
        tasks.append(task)
        tasks.sort(key=lambda t: t.task_id)
        self._write(tasks)

    def _read(self) -> list[Task]:
        if not self.path.exists():
            return []
        return [Task(**data) for data in json.loads(self.path.read_text(encoding="utf-8"))]

    def _write(self, tasks: list[Task]) -> None:
        # Write a temp file, then rename it: a crash mid-write never leaves a half-written file.
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps([asdict(t) for t in tasks], indent=2), encoding="utf-8")
        os.replace(tmp, self.path)
