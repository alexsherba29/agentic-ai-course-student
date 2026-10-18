"""A scripted, deterministic stand-in for a language model.

Tests use it so that grading never depends on a real model's mood. It works in
one of two ways:

- **script**: a list of replies returned in order, e.g.
  ``FakeLLM([call_tool("check_service_status", service="vpn"), say("VPN is down.")])``
- **responder**: a function ``(messages, tools) -> LLMResponse`` that decides
  each reply by looking at the conversation. Demos use it to react to tool results.

Every call is recorded in ``calls``, so tests can check exactly what the agent
sent the model, and ``call_count`` counts model calls (exercise 05 compares them).
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable

from common.llm import LLMResponse, ToolCall

Responder = Callable[[list[dict], list[dict] | None], LLMResponse]


class ScriptExhausted(AssertionError):
    """The agent asked the model more times than the test scripted."""


def say(text: str) -> LLMResponse:
    """A reply with text and no tool calls, i.e. a final answer."""
    return LLMResponse(text=text, tool_calls=[])


def call_tool(name: str, **arguments) -> LLMResponse:
    """A reply asking the agent to run one tool."""
    return LLMResponse(text="", tool_calls=[ToolCall(name, dict(arguments))])


@dataclass
class RecordedCall:
    """What the agent sent the model on one call."""

    messages: list[dict]
    tools: list[dict] | None


class FakeLLM:
    def __init__(self, script: list[LLMResponse] | None = None, responder: Responder | None = None):
        if (script is None) == (responder is None):
            raise ValueError("Give FakeLLM exactly one of: a script (list of replies) or a responder function.")
        self._script = list(script or [])
        self._responder = responder
        self.calls: list[RecordedCall] = []

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        self.calls.append(RecordedCall(copy.deepcopy(messages), copy.deepcopy(tools)))
        if self._responder is not None:
            return self._responder(copy.deepcopy(messages), tools)
        index = self.call_count - 1
        if index >= len(self._script):
            raise ScriptExhausted(
                f"The agent called the model {self.call_count} times, but this test only scripted "
                f"{len(self._script)} replies. Does your loop stop when the model gives a final "
                "answer, and does it respect max_steps?"
            )
        return copy.deepcopy(self._script[index])
