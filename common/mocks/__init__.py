"""Deterministic mock systems the support agent talks to."""
from common.mocks.base import FAIL_MODES, ApprovalRequired, CallRecord, MockService, ToolTimeout
from common.mocks.documents import DocumentNotFound, DocumentStore
from common.mocks.status_api import StatusAPI
from common.mocks.ticketing import TicketSystem

__all__ = [
    "FAIL_MODES", "ApprovalRequired", "CallRecord", "DocumentNotFound", "DocumentStore",
    "MockService", "StatusAPI", "TicketSystem", "ToolTimeout",
]
