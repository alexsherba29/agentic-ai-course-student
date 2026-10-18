"""Public tests for exercise 01 — one test per task in the README.

Run them with:  python -m pytest exercises/01-first-agent/tests
"""
from common.fake_llm import FakeLLM, call_tool, say
from common.llm import ToolCall
from common.mocks import DocumentStore, StatusAPI


def test_stops_when_model_gives_final_answer(agent_module, tools_module, quiet):
    """Task 1: no tool calls means the model has answered — stop and return it."""
    llm = FakeLLM([say("Hello! How can I help?")])
    result = agent_module.run_agent("hi", llm, tools_module.make_tools(), tools_module.TOOL_SPECS, log=quiet)
    assert result.stopped_reason == "answered", (
        f"stopped_reason is {result.stopped_reason!r}. When the model's reply has no tool calls, "
        "run_agent should return an AgentResult with stopped_reason 'answered' (Task 1)."
    )
    assert result.answer == "Hello! How can I help?", (
        f"answer is {result.answer!r} — it should be the model's text, response.text (Task 1)."
    )
    assert llm.call_count == 1, f"The model was called {llm.call_count} times; one call was enough here (Task 1)."


def test_run_tool_calls_the_chosen_tool_with_its_arguments(agent_module):
    """Task 2: find the tool by the name the model chose and call it with its arguments."""
    seen = []
    tools = {"check_service_status": lambda service: seen.append(service) or {"status": "outage"}}
    result = agent_module.run_tool(tools, ToolCall("check_service_status", {"service": "vpn"}))
    assert seen == ["vpn"], (
        f"The tool received {seen} — run_tool must call tools[call.name] with the model's arguments, "
        "e.g. tool(**call.arguments) (Task 2)."
    )
    assert result == {"status": "outage"}, f"run_tool returned {result!r}; it should return what the tool returned (Task 2)."


def test_tool_result_is_fed_back_to_the_model(agent_module, tools_module, quiet):
    """Task 3: the tool's result must be in the messages for the model's next call."""
    llm = FakeLLM([call_tool("check_service_status", service="vpn"), say("The VPN is down.")])
    tools = tools_module.make_tools(StatusAPI(statuses={"vpn": "outage"}), DocumentStore())
    result = agent_module.run_agent("Is the VPN ok?", llm, tools, tools_module.TOOL_SPECS, log=quiet)

    assert llm.call_count == 2, f"Expected 2 model calls (tool, then answer) but got {llm.call_count} (Task 3)."
    second_call = llm.calls[1].messages
    tool_messages = [m for m in second_call if m["role"] == "tool"]
    assert tool_messages and '"outage"' in tool_messages[-1]["content"], (
        "On its second call the model never saw the status result. After running a tool, append "
        "tool_message(call.name, result) to messages so the model can use it (Task 3)."
    )
    assert [(s.tool, s.arguments) for s in result.steps] == [("check_service_status", {"service": "vpn"})], (
        f"result.steps is {result.steps!r} — record a Step for every tool you run (Task 3)."
    )
    assert result.answer == "The VPN is down."


def test_stops_at_max_steps(agent_module, tools_module, quiet):
    """Task 4: never call the model more than max_steps times."""
    llm = FakeLLM([call_tool("check_service_status", service="vpn")] * 3 + [say("too late")])
    result = agent_module.run_agent("Is the VPN ok?", llm, tools_module.make_tools(),
                                    tools_module.TOOL_SPECS, max_steps=3, log=quiet)
    assert llm.call_count == 3, (
        f"The model was called {llm.call_count} times with max_steps=3. Check the step count "
        "before each model call and stop when the limit is reached (Task 4)."
    )
    assert result.stopped_reason == "max_steps", (
        f"stopped_reason is {result.stopped_reason!r}; it should be 'max_steps' when the limit stops the agent (Task 4)."
    )
    assert result.answer == agent_module.FALLBACK_ANSWER, "When stopped by the limit, answer with FALLBACK_ANSWER (Task 4)."


def test_new_information_changes_the_next_action(agent_module, tools_module, demo_module, quiet):
    """Task 5: same question, different service status → different second action."""
    def run(vpn_status):
        llm = FakeLLM(responder=demo_module.demo_policy)
        tools = tools_module.make_tools(StatusAPI(statuses={"vpn": vpn_status}), DocumentStore())
        return agent_module.run_agent(demo_module.DEFAULT_QUESTION, llm, tools, tools_module.TOOL_SPECS, log=quiet)

    outage, working = run("outage"), run("operational")
    assert [s.tool for s in outage.steps] == ["check_service_status"], (
        f"With a VPN outage the agent ran {[s.tool for s in outage.steps]}; after seeing the outage it "
        "should answer straight away."
    )
    assert [s.tool for s in working.steps] == ["check_service_status", "lookup_solution"], (
        f"With the VPN working the agent ran {[s.tool for s in working.steps]}; after seeing it's "
        "operational it should look up the guide."
    )
    assert outage.stopped_reason == working.stopped_reason == "answered"
