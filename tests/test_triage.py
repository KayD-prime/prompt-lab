"""The triage prompt against its cases. One command runs them all:  python -m pytest
Each case is one test, so a failure names the input and the check that failed."""
import pytest

from promptlab import load_prompt, load_cases, check_case
from promptlab.client import ask

PROMPT = load_prompt("triage")
CASES = load_cases("triage")


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_triage(case):
    answer, _ = ask(PROMPT.messages(**case["input"]))
    failures = check_case(answer, case["expect"])
    assert not failures, "\n".join(failures) + f"\n--- answer was:\n{answer}"
