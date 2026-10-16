"""Every prompt in prompts/ against every case in cases/. One command runs the whole library:  python -m pytest
Each case is one test named <prompt>-<id>, so a failure names the prompt, the input and the check that failed."""
from pathlib import Path

import pytest

from promptlab import load_prompt, load_cases, check_case
from promptlab.client import ask

ROOT = Path(__file__).resolve().parent.parent
NAMES = sorted(p.stem for p in (ROOT / "cases").glob("*.json"))
ALL = [(name, case) for name in NAMES for case in load_cases(name)]


@pytest.mark.parametrize("name,case", ALL, ids=[f"{n}-{c['id']}" for n, c in ALL])
def test_case(name, case):
    answer, _ = ask(load_prompt(name).messages(**case["input"]))
    failures = check_case(answer, case["expect"])
    assert not failures, "\n".join(failures) + f"\n--- answer was:\n{answer}"
