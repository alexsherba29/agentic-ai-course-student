"""Check that your course workspace is ready.

Run it from the top folder of your course repository:

    python workspace/smoke_test.py              # everything, including the real model
    python workspace/smoke_test.py --fake-only  # skip Ollama (fake model only)

Each line shows ✅ (fine), ⚠️ (works, but read the hint) or ❌ (must fix).
The script ends with "READY" when nothing is ❌.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

OK, WARN, FAIL = "✅", "⚠️ ", "❌"


def check_python() -> tuple[str, str]:
    v = sys.version_info
    if v >= (3, 11):
        return OK, f"Python {v.major}.{v.minor}.{v.micro}"
    return FAIL, f"Python {v.major}.{v.minor} is too old — install Python 3.11 or newer (see SETUP.md step 4)"


def check_pytest() -> tuple[str, str]:
    try:
        import pytest
    except ImportError:
        return FAIL, "pytest is missing — run:  pip install -r workspace/requirements.txt"
    return OK, f"pytest {pytest.__version__}"


def check_course_code() -> tuple[str, str]:
    """Run a tiny agent turn with the fake model and a mock service."""
    try:
        from common.fake_llm import FakeLLM, call_tool, say
        from common.llm import assistant_message, tool_message
        from common.mocks import StatusAPI
    except ImportError as err:
        return FAIL, f"cannot import the course code ({err}) — run this script from the repository's top folder"

    llm = FakeLLM([call_tool("check_service_status", service="vpn"), say("The VPN is down.")])
    api = StatusAPI(statuses={"vpn": "outage"})
    messages = [{"role": "user", "content": "Is the VPN working?"}]
    first = llm.chat(messages)
    messages.append(assistant_message(first))
    result = api.check_status(**first.tool_calls[0].arguments)
    messages.append(tool_message("check_service_status", result))
    final = llm.chat(messages)
    if result["status"] == "outage" and final.text and llm.call_count == 2:
        return OK, "course code works with the fake model"
    return FAIL, "the fake-model round trip gave an unexpected result — email eran.beeri-bamani@biu.ac.il"


def check_git() -> tuple[str, str]:
    if not shutil.which("git"):
        return FAIL, "git is not installed (see SETUP.md step 2)"
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=REPO, capture_output=True, text=True)
    if inside.returncode != 0:
        return WARN, "this folder is not a git repository — clone your course repo instead of downloading a ZIP (step 6)"
    remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=REPO, capture_output=True, text=True)
    if remote.returncode != 0:
        return WARN, "no GitHub remote 'origin' — you won't be able to push or submit (step 6)"
    return OK, f"git repo, origin = {remote.stdout.strip()}"


def check_ollama() -> list[tuple[str, str]]:
    from common.llm import LLMUnavailable, OllamaLLM, tool_spec

    llm = OllamaLLM(timeout=300)
    try:
        models = llm.list_models()
    except LLMUnavailable as err:
        return [(FAIL, str(err))]
    results = [(OK, f"Ollama is running at {llm.host}")]
    if not any(m == llm.model or m == f"{llm.model}:latest" for m in models):
        return results + [(FAIL, f"model {llm.model!r} is not downloaded — run:  ollama pull {llm.model}")]
    results.append((OK, f"model {llm.model} is downloaded"))

    tools = [tool_spec("check_service_status", "Check whether an IT service is working.",
                       {"service": "service name, e.g. vpn or email"})]
    messages = [
        {"role": "system", "content": "You are an IT support assistant. Use the tools to check facts."},
        {"role": "user", "content": "Is the VPN working right now?"},
    ]
    print("   … asking the real model one question (the first call can take a minute)")
    try:
        reply = llm.chat(messages, tools=tools)
    except LLMUnavailable as err:
        return results + [(FAIL, str(err))]
    if reply.tool_calls and reply.tool_calls[0].name == "check_service_status":
        results.append((OK, f"the model chose a tool: {reply.tool_calls[0].name}({reply.tool_calls[0].arguments})"))
    else:
        results.append((WARN, "the model answered without using the tool — fine for now; "
                              "if it happens every time, try the other model in SETUP.md step 8"))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fake-only", action="store_true", help="skip the Ollama (real model) checks")
    args = parser.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # emoji on older Windows consoles
    except (AttributeError, ValueError):
        pass

    print("Checking your course workspace…\n")
    results = [check_python(), check_pytest(), check_course_code(), check_git()]
    for mark, text in results:
        print(f"{mark} {text}")
    if args.fake_only:
        print(f"{WARN} skipped the real-model checks (--fake-only)")
    else:
        for mark, text in check_ollama():
            results.append((mark, text))
            print(f"{mark} {text}")

    failures = sum(mark == FAIL for mark, _ in results)
    print()
    if failures:
        print(f"NOT READY — fix the {failures} ❌ item(s) above, then run this script again.")
        return 1
    print("READY — your workspace works. 🎉")
    return 0


if __name__ == "__main__":
    sys.exit(main())
