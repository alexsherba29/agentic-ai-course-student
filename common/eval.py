"""Compare agent runs on the same cases: how often they're right, and what it cost.

Exercise 05 uses this to compare a single agent with an investigator plus verifier
pair. "Cost" here is the number of model calls, which is what you pay for (in
time or money) with any real model.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunResult:
    """One agent run on one test case."""

    case_id: str
    answer: str
    correct: bool
    model_calls: int
    tool_calls: int = 0
    steps: int = 0
    notes: str = ""


@dataclass
class Summary:
    name: str
    cases: int
    accuracy: float
    total_model_calls: int
    mean_model_calls: float
    total_tool_calls: int


def check_answer(answer: str, must_include: list[str] = (), must_not_include: list[str] = ()) -> bool:
    """A simple, case-insensitive correctness check on an answer's text."""
    text = answer.lower()
    return all(p.lower() in text for p in must_include) and not any(p.lower() in text for p in must_not_include)


def summarize(results: list[RunResult], name: str) -> Summary:
    if not results:
        raise ValueError("No results to summarize.")
    calls = sum(r.model_calls for r in results)
    return Summary(
        name=name,
        cases=len(results),
        accuracy=sum(r.correct for r in results) / len(results),
        total_model_calls=calls,
        mean_model_calls=calls / len(results),
        total_tool_calls=sum(r.tool_calls for r in results),
    )


def compare_table(a: Summary, b: Summary) -> str:
    """A Markdown table comparing two summaries."""
    rows = [
        ("Cases", a.cases, b.cases),
        ("Accuracy", f"{a.accuracy:.0%}", f"{b.accuracy:.0%}"),
        ("Model calls (total)", a.total_model_calls, b.total_model_calls),
        ("Model calls (mean per case)", f"{a.mean_model_calls:.1f}", f"{b.mean_model_calls:.1f}"),
        ("Tool calls (total)", a.total_tool_calls, b.total_tool_calls),
    ]
    lines = [f"| Metric | {a.name} | {b.name} |", "|---|---|---|"]
    lines += [f"| {label} | {x} | {y} |" for label, x, y in rows]
    return "\n".join(lines)


def compare_cases(name_a: str, a: list[RunResult], name_b: str, b: list[RunResult]) -> str:
    """A Markdown table showing each case's correctness and model calls side by side."""
    by_id_b = {r.case_id: r for r in b}
    if [r.case_id for r in a] != [r.case_id for r in b]:
        raise ValueError("Both runs must cover the same cases in the same order.")
    lines = [
        f"| Case | {name_a} correct | {name_a} calls | {name_b} correct | {name_b} calls |",
        "|---|---|---|---|---|",
    ]
    for ra in a:
        rb = by_id_b[ra.case_id]
        mark = lambda ok: "✅" if ok else "❌"  # noqa: E731
        lines.append(f"| {ra.case_id} | {mark(ra.correct)} | {ra.model_calls} | {mark(rb.correct)} | {rb.model_calls} |")
    return "\n".join(lines)
