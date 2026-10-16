"""promptlab: run a prompt over many inputs and check each answer against what it must contain.

    python -m promptlab run triage          every case in cases/triage.json, one line per case
    python -m promptlab show triage 3       the full answer for input 3
    python -m pytest                        the same checks as a test suite (one command, exit code 0 or 1)
"""
from .prompts import load_prompt, Prompt
from .checks import check_case, parse_answer, CHECKS
from .runner import run_cases, load_cases, load_inputs

__all__ = ["load_prompt", "Prompt", "check_case", "parse_answer", "CHECKS", "run_cases", "load_cases", "load_inputs"]
