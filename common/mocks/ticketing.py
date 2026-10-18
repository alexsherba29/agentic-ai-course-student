"""A mock support-ticket system with an approval gate and idempotency keys.

Two safety features that exercises 03 and 04 rely on:

- **Approval gate**: ``create_ticket`` refuses to run unless the task's status is
  ``"approved"``. This is the last line of defence if an agent tries to skip approval.
- **Idempotency key**: if you send the same ``idempotency_key`` twice, you get the
  first ticket back instead of a duplicate. ``find_by_key`` lets you check whether
  a create that "timed out" actually happened.
"""
from __future__ import annotations

import copy

from common.mocks.base import ApprovalRequired, MockService

PENDING_APPROVAL = "pending_approval"
APPROVED = "approved"
REJECTED = "rejected"
DONE = "done"
FAILED = "failed"
TASK_STATUSES = (PENDING_APPROVAL, APPROVED, REJECTED, DONE, FAILED)


class TicketSystem(MockService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tickets: dict[str, dict] = {}
        self._by_key: dict[str, str] = {}

    def create_ticket(
        self,
        title: str,
        description: str,
        *,
        approval_status: str,
        idempotency_key: str | None = None,
        priority: str = "normal",
    ) -> dict:
        record = self._begin("create_ticket", {
            "title": title, "description": description, "approval_status": approval_status,
            "idempotency_key": idempotency_key, "priority": priority,
        })
        if approval_status != APPROVED:
            record.outcome = "rejected"
            raise ApprovalRequired(
                f"create_ticket refused: the task status is {approval_status!r}. "
                f"It must be {APPROVED!r} by a human first."
            )
        if idempotency_key is not None and idempotency_key in self._by_key:
            record.outcome = "deduplicated"
            return copy.deepcopy(self._tickets[self._by_key[idempotency_key]])

        ticket_id = self._new_id()
        ticket = {
            "ticket_id": ticket_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "open",
            "idempotency_key": idempotency_key,
        }
        self._tickets[ticket_id] = ticket
        if idempotency_key is not None:
            self._by_key[idempotency_key] = ticket_id
        self._finish_write(record)
        return copy.deepcopy(ticket)

    def find_by_key(self, idempotency_key: str) -> dict | None:
        """The ticket created with this key, or None if no such create happened."""
        self._begin("find_by_key", {"idempotency_key": idempotency_key})
        ticket_id = self._by_key.get(idempotency_key)
        return copy.deepcopy(self._tickets[ticket_id]) if ticket_id else None

    def get_ticket(self, ticket_id: str) -> dict | None:
        self._begin("get_ticket", {"ticket_id": ticket_id})
        ticket = self._tickets.get(ticket_id)
        return copy.deepcopy(ticket) if ticket else None

    def list_tickets(self) -> list[dict]:
        """All tickets, oldest first (not logged: it's for tests and graders)."""
        return copy.deepcopy(list(self._tickets.values()))

    def _new_id(self) -> str:
        while True:
            ticket_id = f"TCK-{self.rng.randint(1000, 9999)}"
            if ticket_id not in self._tickets:
                return ticket_id
