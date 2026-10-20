"""Shared behaviour for every mock system: fault injection and a call log.

Real services time out, lose replies and run slowly. The mocks do the same on
purpose, but deterministically, so the same test always sees the same failure:

- ``fail_mode="none"``: always works.
- ``fail_mode="timeout"``: raises ``ToolTimeout`` before doing anything.
- ``fail_mode="lost_reply_after_write"``: a write really happens, then the reply
  is lost (``ToolTimeout``). Retrying blindly would do the write twice.
- ``fail_mode="slow"``: works, but records a simulated latency (no real waiting).

``fail_on_calls={1, 3}`` limits the fault to those call numbers (counted from 1
across all methods of one mock). ``None`` means every call. ``fail_method="create_ticket"``
limits the fault to that one method, and then ``fail_on_calls`` counts only its calls
("the first create_ticket call loses its reply").
"""
from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from typing import Any

FAIL_MODES = ("none", "timeout", "lost_reply_after_write", "slow")


class ToolTimeout(Exception):
    """The tool didn't answer in time. For a write, it may or may not have happened."""


class ApprovalRequired(Exception):
    """An action that needs human approval was attempted without it."""


@dataclass
class CallRecord:
    """One call made to a mock, and what happened."""

    method: str
    args: dict[str, Any]
    outcome: str  # ok | timeout | lost_reply | deduplicated | rejected | error
    latency_ms: int = 0


class MockService:
    def __init__(self, fail_mode: str = "none", seed: int = 0, fail_on_calls: set[int] | None = None,
                 fail_method: str | None = None):
        if fail_mode not in FAIL_MODES:
            raise ValueError(f"Unknown fail_mode {fail_mode!r}. Choose one of {FAIL_MODES}.")
        self.fail_mode = fail_mode
        self.fail_on_calls = set(fail_on_calls) if fail_on_calls is not None else None
        self.fail_method = fail_method
        self.rng = random.Random(seed)
        self.call_log: list[CallRecord] = []
        self._calls_per_method: Counter[str] = Counter()
        self._fault_active = False

    def calls(self, method: str | None = None) -> list[CallRecord]:
        """The call log, optionally only for one method."""
        return [r for r in self.call_log if method is None or r.method == method]

    def _begin(self, method: str, args: dict[str, Any]) -> CallRecord:
        """Log the call and apply any fault that happens *before* the work."""
        record = CallRecord(method, dict(args), "ok")
        self.call_log.append(record)
        self._calls_per_method[method] += 1
        if self.fail_method is None:
            targeted, number = True, len(self.call_log)  # every method, counted together
        else:
            targeted, number = method == self.fail_method, self._calls_per_method[method]
        self._fault_active = targeted and (self.fail_on_calls is None or number in self.fail_on_calls)
        if not self._fault_active:
            return record
        if self.fail_mode == "slow":
            record.latency_ms = self.rng.randint(2_000, 8_000)
        elif self.fail_mode == "timeout":
            record.outcome = "timeout"
            raise ToolTimeout(f"{method} timed out: the service did not answer.")
        return record

    def _finish_write(self, record: CallRecord) -> None:
        """Call after a write has happened, to apply the lost-reply fault."""
        if self._fault_active and self.fail_mode == "lost_reply_after_write":
            record.outcome = "lost_reply"
            raise ToolTimeout(
                f"{record.method} timed out waiting for a reply. The request was sent, so it "
                "may have succeeded — check before trying again."
            )
