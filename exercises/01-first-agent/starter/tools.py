"""The support agent's tools: what it can *do*, beyond writing text.

Each tool is a plain Python function that returns a dict. ``TOOL_SPECS`` describes
the same tools to the model, so it can decide which one to call and with what
arguments. The model never runs the code itself; it only asks, and the agent runs it.
"""
from __future__ import annotations

from typing import Callable

from common.llm import tool_spec
from common.mocks import DocumentStore, StatusAPI
from common.mocks.status_api import DEFAULT_STATUSES

TOOL_SPECS = [
    tool_spec(
        "check_service_status",
        "Check whether a company IT service is working right now. Use this first when the user "
        "has a problem with a service, because a known outage changes what you should tell them.",
        {"service": f"Service name: one of {', '.join(DEFAULT_STATUSES)}"},
    ),
    tool_spec(
        "lookup_solution",
        "Look up the support guide for a problem and return its steps. Use this when the "
        "service is working, so the problem is probably on the user's side.",
        {"problem": "Short description of the user's problem, e.g. 'cannot connect to vpn'"},
    ),
]


def make_tools(
    status_api: StatusAPI | None = None, docs: DocumentStore | None = None
) -> dict[str, Callable[..., dict]]:
    """Build the tools, connected to the given mock systems (fresh defaults if None).

    Returns a dict from tool name to function, which is how the agent finds the
    tool the model chose.
    """
    status_api = status_api or StatusAPI()
    docs = docs or DocumentStore()

    def check_service_status(service: str) -> dict:
        return status_api.check_status(service)

    def lookup_solution(problem: str) -> dict:
        hits = docs.search(problem, k=1)
        if not hits:
            return {"found": False, "message": "No support guide matches this problem."}
        guide = docs.get(hits[0]["doc_id"])
        return {"found": True, "doc_id": guide["doc_id"], "guide": guide["title"], "text": guide["text"]}

    return {"check_service_status": check_service_status, "lookup_solution": lookup_solution}
