"""Run the support agent on one question and watch every step.

From the top folder of the repository:

    python exercises/01-first-agent/starter/demo.py                      # VPN working
    python exercises/01-first-agent/starter/demo.py --vpn-status outage  # VPN down
    python exercises/01-first-agent/starter/demo.py --max-steps 1
    python exercises/01-first-agent/starter/demo.py --backend ollama     # real model

With ``--backend fake`` (the default), the "model" is ``demo_policy`` below: a few
if-statements that behave like a sensible model, so you can see the loop work
without Ollama. With ``--backend ollama``, a real model makes the decisions.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # so `import common` works

from common.fake_llm import FakeLLM, call_tool, say  # noqa: E402
from common.llm import LLMResponse, get_llm  # noqa: E402
from common.mocks import StatusAPI  # noqa: E402
from common.mocks.status_api import DEFAULT_STATUSES, STATUSES  # noqa: E402

DEFAULT_QUESTION = "I can't connect to the VPN from home. What should I do?"


def demo_policy(messages: list[dict], tools: list[dict] | None) -> LLMResponse:
    """A pretend model: decides the next action from the question and the newest tool result."""
    question = next(m["content"] for m in messages if m["role"] == "user")
    last = messages[-1]

    if last["role"] != "tool":  # nothing checked yet: start with the service status
        words = re.findall(r"[a-z0-9]+", question.lower().replace("-", ""))
        service = next((s for s in DEFAULT_STATUSES if s in words), None)
        if service is None:
            return say(f"Which service is the problem with? I can check: {', '.join(DEFAULT_STATUSES)}.")
        return call_tool("check_service_status", service=service)

    tool, result = last["tool_name"], json.loads(last["content"])
    if "error" in result:
        return say(f"Sorry, I couldn't check that right now ({result['error']}). Please try again later.")
    if tool == "check_service_status":
        if result["status"] == "operational":
            return call_tool("lookup_solution", problem=question)
        if result["status"] == "unknown":
            return say(f"I couldn't find that service. {result['message']}")
        return say(f"{result['message']} You don't need to change anything on your computer.")
    if tool == "lookup_solution" and result["found"]:
        return say(f"The service is working, so the problem is probably on your side. "
                   f"Please follow the steps in the guide '{result['guide']}'.")
    return say("I couldn't find a guide for this. Please contact the IT help desk.")


def main(argv: list[str] | None = None) -> int:
    from agent import run_agent  # this folder's agent.py
    from tools import TOOL_SPECS, make_tools

    parser = argparse.ArgumentParser(description="Run the exercise 01 support agent.")
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--vpn-status", default="operational", choices=STATUSES)
    parser.add_argument("--max-steps", type=int, default=5)
    parser.add_argument("--backend", default="fake", choices=["fake", "ollama"])
    args = parser.parse_args(argv)

    llm = get_llm(args.backend, fake=FakeLLM(responder=demo_policy))
    tools = make_tools(StatusAPI(statuses={"vpn": args.vpn_status}))
    print(f"Question: {args.question}\n(VPN status: {args.vpn_status}, backend: {args.backend})\n")
    result = run_agent(args.question, llm, tools, TOOL_SPECS, max_steps=args.max_steps)
    print(f"\nFinal answer : {result.answer}")
    print(f"Stopped      : {result.stopped_reason} after {result.model_calls} model call(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
