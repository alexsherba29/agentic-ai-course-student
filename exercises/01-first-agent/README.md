# Exercise 01 — My first agent

You'll finish a small IT-support agent. It can check whether a service (like the VPN) is working and look up a support guide. You'll write the **loop** that makes it an agent: the model chooses a tool, the agent runs it, the model sees the result, and the agent either continues or stops, never taking more than a fixed number of steps.

## 1. Learning goals

- **Explain** what makes a program an *agent*: a loop in which a model chooses actions and sees their results.
- **Implement** the loop: run the tool the model chose, give it the result, and stop when it answers.
- **Enforce** a hard step limit so an agent can never run forever.
- **Show** how new information (a tool result) changes the agent's next action.

## 2. Before you start (downloads)

Nothing new — the workspace from `workspace/SETUP.md` is enough.

- Required: your course repository with `.venv` activated, where `python workspace/smoke_test.py --fake-only` prints READY.
- **Optional:** Ollama with `llama3.2:3b` (SETUP.md step 8), only for the last "try a real model" run. Every task and test works without it.

## 3. Concepts

A **tool** is a normal Python function the agent may use, such as `check_service_status("vpn")`. The model can't run code. It can only *ask* for a tool by name, with arguments. Your code runs the tool and shows the model the result.

The **conversation** (`messages`) is the agent's memory. It's a list of messages: the system instructions, the user's question, the model's replies and the tool results. Every model call sees the whole list. That's why adding a tool result to `messages` lets new information change the next action.

An **agent** is a loop around the model:

```
             ┌──────────────────────────────────────────────────────┐
question ──► │ ask the model (with messages + tool descriptions)    │ ◄─────┐
             └───────────────┬──────────────────────────────────────┘       │
                             │                                              │
          no tool calls? ────┴──── tool calls?                              │
               │                       │                                    │
        STOP: final answer      run each tool → add result to messages ─────┘
                                (but STOP if max_steps model calls are used up)
```

One **step** is one model call plus the tools it asked for. `max_steps` caps the number of model calls. Real models sometimes loop, for example by checking the same thing again and again, and every call costs time and money.

The code lives in [`starter/agent.py`](starter/agent.py). The tools are in [`starter/tools.py`](starter/tools.py) and are already finished; read their descriptions in `TOOL_SPECS`, because that's what the model reads. `Step` and `AgentResult` are *dataclasses*: small classes that just hold values. You create one like a function call with keyword arguments, for example `Step(step=1, tool="lookup_solution", arguments={...}, result={...})`.

## 4. What you're starting from

This is the first exercise, so you start from the provided code. Exercises 02–05 build on **your own** solution to this one, so keep it tidy.

| File | Status |
|---|---|
| `starter/tools.py` | ✅ done: `check_service_status` and `lookup_solution`, connected to mock systems |
| `starter/demo.py` | ✅ done: runs the agent and prints every step. Its "fake model" (`demo_policy`) is a few if-statements that act like a sensible model |
| `starter/agent.py` | ✏️ **you complete four `TODO(student)` blocks** |
| `starter/answers.md` | ✏️ **you answer two short questions** |
| `common/` | ✅ shared course code (model interface, fake model, mocks). Read it, but don't edit it |

Right now `python exercises/01-first-agent/starter/demo.py` runs one step and then stops with `NotImplementedError: TODO(student) 3 …`, and all public tests fail. That's expected.

## 5. Your tasks

Work through the tasks in order; each one builds on the previous. After each task, run its check.

- [ ] **Task 1 — Stop when the model answers.** File `starter/agent.py`, function `run_agent`, block `TODO(student) 1`.
  If the model's reply has no tool calls, it's the final answer. Return an `AgentResult` with the model's text and `stopped_reason="answered"`.
  Check: `python -m pytest exercises/01-first-agent/tests -k final_answer` → **1 passed**.

- [ ] **Task 2 — Run the tool the model chose.** File `starter/agent.py`, function `run_tool`, block `TODO(student) 2`.
  Call the tool the model chose (looked up by its name) with the model's arguments, and return what it returns. Unknown tool names are already handled for you, and show the pattern: a tool that raises an exception must **not** crash the agent either. Return a dict with an `"error"` key that explains what went wrong, so the model can read it and try something else.
  Check: `python -m pytest exercises/01-first-agent/tests -k run_tool` → **1 passed**.

- [ ] **Task 3 — Use the result and continue.** File `starter/agent.py`, function `run_agent`, block `TODO(student) 3`.
  For each tool call in the reply: run it with `run_tool`, add the result to `messages` with `tool_message(...)`, record a `Step`, and print it with `log_tool_result(...)`. Then remove the `raise` line, so the loop goes round and asks the model again.
  Check: `python exercises/01-first-agent/starter/demo.py` now runs to a final answer, and `python -m pytest exercises/01-first-agent/tests -k fed_back` → **1 passed**.

- [ ] **Task 4 — Never take more than `max_steps` steps.** File `starter/agent.py`, function `run_agent`, block `TODO(student) 4`.
  Before each model call, stop if `model_calls` has reached `max_steps`. Return `FALLBACK_ANSWER` with `stopped_reason="max_steps"`.
  Check: `python exercises/01-first-agent/starter/demo.py --max-steps 1` stops after one model call, and `python -m pytest exercises/01-first-agent/tests -k max_steps` → **1 passed**.

- [ ] **Task 5 — See new information change the next action.** Run the demo twice:
  ```
  python exercises/01-first-agent/starter/demo.py --vpn-status operational
  python exercises/01-first-agent/starter/demo.py --vpn-status outage
  ```
  Compare **step 2** in the two runs. Then answer Q1 and Q2 in `starter/answers.md`, 2–3 sentences each. Your answers are read and graded by hand; no test checks them.
  Check: `python -m pytest exercises/01-first-agent/tests` → **5 passed** (this already passes after Task 4).

## 6. Time budget

| Step | Minutes |
|---|---|
| Read sections 1–4, run the demo and the tests once | 6 |
| Task 1 — stop on a final answer | 3 |
| Task 2 — `run_tool` | 5 |
| Task 3 — feed results back | 6 |
| Task 4 — step limit | 3 |
| Task 5 — compare runs, write `answers.md` | 5 |
| **Total** | **28** |

Stuck on one task for more than 10 minutes? Re-read the `TODO(student)` comment and the failing test's message (it says what's wrong), then ask.

## 7. How to run and test

Run everything from the **top folder of your repository**, with `.venv` active. The commands are the same on Windows, macOS and Linux.

```
# the demo, with the fake model (no Ollama needed)
python exercises/01-first-agent/starter/demo.py
python exercises/01-first-agent/starter/demo.py --vpn-status outage
python exercises/01-first-agent/starter/demo.py --max-steps 1
python exercises/01-first-agent/starter/demo.py --question "My email is not arriving"

# the public tests: all of them, or just one task's (-k matches part of a test name)
python -m pytest exercises/01-first-agent/tests
python -m pytest exercises/01-first-agent/tests -k run_tool
```

**Optional: try a real model** (needs Ollama running, SETUP.md step 8):

```
python exercises/01-first-agent/starter/demo.py --backend ollama
python exercises/01-first-agent/starter/demo.py --backend ollama --vpn-status outage
```

A real model doesn't always follow the system prompt. Watch whether it checks the status first, and whether it stops. That's exactly why `max_steps` exists.

## 8. What success looks like

`python -m pytest exercises/01-first-agent/tests` shows **5 passed**. With the VPN working, the demo prints something like:

```
[step 1] model chose tool → check_service_status({'service': 'vpn'})
           tool result → {'service': 'vpn', 'status': 'operational', 'message': 'VPN is working normally.'}
[step 2] model chose tool → lookup_solution({'problem': "I can't connect to the VPN from home. What should I do?"})
           tool result → {'found': True, 'guide': 'VPN connection troubleshooting', 'text': ...
[step 3] model answered → The service is working, so the problem is probably on your side. Please follow the steps in the guide 'VPN connection troubleshooting'.

Final answer : The service is working, so the problem is probably on your side. Please follow the steps in the guide 'VPN connection troubleshooting'.
Stopped      : answered after 3 model call(s)
```

With `--vpn-status outage`, step 2 is an answer instead of a guide lookup, and the run stops after **2** model calls. With `--max-steps 1`, step 1 runs, then your Task 4 message appears (any wording, for example `Stopped: reached max_steps=1 without a final answer.`), and the run ends with `max_steps after 1 model call(s)`.

Grading also runs extra tests on edge cases of the same four tasks, so make sure your code follows each `TODO(student)` description completely, not just enough to pass the public tests.

## 9. How to submit

The full guide is `workspace/SETUP.md`, step 11. In short:

```
git add -A
git commit -m "Exercise 01 done"
git push
git tag ex01-submit
git push origin ex01-submit
```

Then submit this link in the course form, with your username and repository name filled in:

```
https://github.com/<you>/<repo>/tree/ex01-submit/exercises/01-first-agent
```

## 10. Stretch goals

Optional and not graded:

- Ask about something that isn't one of the services (`--question "Is the teleporter down?"`). The fake model asks you back instead of guessing. Why is that better? What does a real model do with the same question?
- Add a third tool to `starter/tools.py`, for example `list_services()`, and its `tool_spec` to `TOOL_SPECS`. Does the real model ever use it?
- Run the same question 3 times with `--backend ollama`. Are the steps always the same? Why might they differ?
