"""Exercise 01: a first support agent — complete the four TODO(student) tasks.

An agent is a loop around a model:

    ask the model → it either answers (stop) or asks for tools →
    run the tools → show it the results → ask again … (at most max_steps times)

Everything the agent "knows" between steps is in ``messages``, the conversation
so far. Adding a tool's result to ``messages`` is what lets new information
change the model's next action.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from common.llm import LLM, LLMResponse, ToolCall, assistant_message, tool_message

SYSTEM_PROMPT = (
    "You are a helpful IT support assistant for a university. "
    "When a user reports a problem with a service, first check that service's status. "
    "If the service has an outage, maintenance or degraded status, tell the user and do not suggest fixes. "
    "If the service is operational, look up the support guide and give the user the first steps. "
    "Answer in at most four short sentences."
)

FALLBACK_ANSWER = (
    "Sorry, I couldn't finish working on this within my step limit. "
    "Please contact the IT help desk."
)


@dataclass
class Step:
    """One tool the agent ran, and what it returned."""

    step: int  # which model call asked for it (1 = the first)
    tool: str
    arguments: dict[str, Any]
    result: Any


@dataclass
class AgentResult:
    answer: str
    stopped_reason: str  # "answered" or "max_steps"
    steps: list[Step]
    model_calls: int


def run_tool(tools: dict[str, Callable[..., Any]], call: ToolCall) -> Any:
    """Run the tool the model chose, with the arguments it chose.

    Mistakes become results the model can read (``{"error": ...}``) instead of
    crashing the agent, so the model gets a chance to correct itself.
    """
    if call.name not in tools:  # the model asked for a tool we don't have
        return {"error": f"Unknown tool {call.name!r}. Available tools: {', '.join(tools)}"}

    # TODO(student) 2: run the tool the model chose — and never crash.
    #   - Call the function tools[call.name] with the model's arguments and return its result.
    #     call.arguments is a dict like {"service": "vpn"}; `**call.arguments` passes it
    #     as keyword arguments, i.e. function(service="vpn").
    #   - If the call raises any exception (wrong arguments, a broken tool, ...), return
    #     a dict like the one above instead: {"error": "<tool name> failed: <exception>"}.
    #   Check:  python -m pytest exercises/01-first-agent/tests -k run_tool
    raise NotImplementedError("TODO(student) 2: implement run_tool")


def run_agent(
    question: str,
    llm: LLM,
    tools: dict[str, Callable[..., Any]],
    tool_specs: list[dict],
    *,
    system_prompt: str = SYSTEM_PROMPT,
    max_steps: int = 5,
    log: Callable[[str], None] = print,
) -> AgentResult:
    """Answer ``question`` using the model and tools, calling the model at most ``max_steps`` times."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    steps: list[Step] = []
    model_calls = 0

    while True:
        # TODO(student) 4: enforce the step limit.
        #   Before asking the model, check whether model_calls has reached max_steps.
        #   If so, log a short message and return an AgentResult with FALLBACK_ANSWER,
        #   stopped_reason "max_steps", the steps so far and model_calls.
        #   Check:  python exercises/01-first-agent/starter/demo.py --max-steps 1

        response = llm.chat(messages, tools=tool_specs)
        model_calls += 1
        messages.append(assistant_message(response))
        log_model_reply(model_calls, response, log)

        # TODO(student) 1: stop when the model has answered.
        #   A reply with no tool calls (response.tool_calls is an empty list) is the final
        #   answer. Return an AgentResult with the model's text (response.text),
        #   stopped_reason "answered", the steps so far and model_calls.
        #   (Build a dataclass like a function call with keyword arguments:
        #    AgentResult(answer=..., stopped_reason=..., steps=..., model_calls=...).)

        # TODO(student) 3: use the tools the model chose, then let the loop continue.
        #   For each call in response.tool_calls:
        #     - run it:  result = run_tool(tools, call)   (Task 2)
        #     - add the result to `messages` with tool_message(call.name, result), so the
        #       model sees it on the next turn — this is how new information changes the
        #       next action,
        #     - record it in `steps` as Step(step=model_calls, tool=..., arguments=..., result=...)
        #       (every tool asked for in the same reply gets the same step number),
        #     - print it with log_tool_result(result, log).
        #   Delete the `raise` line below when you're done.
        #   Check:  python exercises/01-first-agent/starter/demo.py
        raise NotImplementedError("TODO(student) 3: run each tool call and add its result to messages")


def log_model_reply(step: int, response: LLMResponse, log: Callable[[str], None]) -> None:
    """Print what the model decided at this step."""
    if response.tool_calls:
        for call in response.tool_calls:
            log(f"[step {step}] model chose tool → {call.name}({call.arguments})")
    else:
        log(f"[step {step}] model answered → {response.text}")


def log_tool_result(result: Any, log: Callable[[str], None]) -> None:
    """Print what a tool returned (shortened)."""
    text = str(result)
    if len(text) > 160:
        text = text[:157] + "..."
    log(f"           tool result → {text}")
