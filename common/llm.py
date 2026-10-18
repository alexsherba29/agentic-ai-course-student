"""One interface for talking to a language model.

Every agent in the course calls the model through ``LLM.chat(messages, tools)``.
That is the only thing an agent needs to know about the model, so switching
between the scripted fake (tests) and a real model (Ollama) never changes
agent code.

Messages use the common chat format::

    {"role": "system" | "user" | "assistant" | "tool", "content": "..."}

Use ``assistant_message`` and ``tool_message`` to build the last two kinds.
"""
from __future__ import annotations

import json
import os
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.request import Request, urlopen

DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"


@dataclass
class ToolCall:
    """The model asking us to run one tool with some arguments."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """One reply from the model: some text, and zero or more tool calls.

    No tool calls means the model is giving its final answer in ``text``.
    """

    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLM(Protocol):
    """Anything with this ``chat`` method can drive an agent."""

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse: ...


class LLMUnavailable(RuntimeError):
    """The real model can't be reached. The message says how to fix it."""


def tool_spec(name: str, description: str, params: dict[str, str]) -> dict:
    """Describe a tool to the model. Every parameter is a required string.

    ``params`` maps a parameter name to a short description. The model reads the
    descriptions to decide when and how to call the tool, so write them for the model.
    """
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": {p: {"type": "string", "description": d} for p, d in params.items()},
            "required": list(params),
        },
    }


def assistant_message(response: LLMResponse) -> dict:
    """Turn a model reply into a message we append to the conversation."""
    message: dict[str, Any] = {"role": "assistant", "content": response.text}
    if response.tool_calls:
        message["tool_calls"] = [
            {"function": {"name": c.name, "arguments": c.arguments}} for c in response.tool_calls
        ]
    return message


def tool_message(tool_name: str, result: Any) -> dict:
    """Wrap a tool's result so the model sees it on its next turn."""
    return {"role": "tool", "tool_name": tool_name, "content": json.dumps(result)}


class OllamaLLM:
    """A real open model running locally in Ollama (https://ollama.com).

    Configure with the environment variables ``OLLAMA_MODEL`` (default
    ``llama3.2:3b``) and ``OLLAMA_HOST`` (default ``http://localhost:11434``).
    Temperature 0 and a fixed seed keep runs as repeatable as a real model allows.
    """

    def __init__(self, model: str | None = None, host: str | None = None, timeout: float = 120.0):
        self.model = model or os.environ.get("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
        self.host = (host or os.environ.get("OLLAMA_HOST", DEFAULT_OLLAMA_HOST)).rstrip("/")
        self.timeout = timeout

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0, "seed": 0},
        }
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]
        reply = self._post("/api/chat", payload)
        message = reply.get("message", {})
        calls = []
        for raw in message.get("tool_calls") or []:
            fn = raw.get("function", {})
            args = fn.get("arguments") or {}
            if isinstance(args, str):
                args = json.loads(args or "{}")
            calls.append(ToolCall(fn.get("name", ""), args))
        return LLMResponse(text=message.get("content") or "", tool_calls=calls)

    def list_models(self) -> list[str]:
        """Names of the models already downloaded (``ollama pull``) on this machine."""
        return [m["name"] for m in self._request(Request(f"{self.host}/api/tags")).get("models", [])]

    def _post(self, path: str, payload: dict) -> dict:
        data = json.dumps(payload).encode()
        request = Request(f"{self.host}{path}", data=data, headers={"Content-Type": "application/json"})
        return self._request(request)

    def _request(self, request: Request) -> dict:
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as err:
            if err.code == 404:
                raise LLMUnavailable(
                    f"Ollama does not have the model {self.model!r}. Download it with:  ollama pull {self.model}"
                ) from err
            raise LLMUnavailable(f"Ollama returned HTTP {err.code}: {err.read().decode(errors='replace')}") from err
        except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
            raise LLMUnavailable(
                f"Could not reach Ollama at {self.host}. Is it running? Open the Ollama app, "
                f"or run `ollama serve` in a terminal. ({err})"
            ) from err


def get_llm(backend: str | None = None, *, fake: LLM | None = None) -> LLM:
    """Pick the model backend: ``"fake"`` (default) or ``"ollama"``.

    The choice comes from ``backend``, else the ``AGENT_LLM_BACKEND`` environment
    variable. The fake backend needs the scripted ``FakeLLM`` you want to use.
    """
    choice = (backend or os.environ.get("AGENT_LLM_BACKEND", "fake")).lower()
    if choice == "ollama":
        return OllamaLLM()
    if choice == "fake":
        if fake is None:
            raise ValueError("The fake backend needs a FakeLLM: get_llm('fake', fake=FakeLLM(...))")
        return fake
    raise ValueError(f"Unknown LLM backend {choice!r}. Use 'fake' or 'ollama'.")
