"""Run one prompt over the cases in cases/<prompt>.json and check every answer.

cases/<prompt>.json is a list: {"id": <input id or any name>, "input": {...} (optional, else the row of inputs/emails.csv
with that id), "expect": {<check>: <value>, ...}, "note": "why this case exists" (optional)}."""
import csv
import json
import sys
import time
from pathlib import Path

from .checks import check_case
from .client import ask, model_name
from .prompts import load_prompt, ROOT

CASES, INPUTS, RUNS = ROOT / "cases", ROOT / "inputs", ROOT / "runs"


def load_inputs(name="emails.csv") -> dict:
    """{id: {"email": text}} from inputs/<name>. The first column is the id; every other column is an input field."""
    rows = {}
    with open(INPUTS / name, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row.pop("input_id", None) or next(iter(row.values()))
            rows[str(key)] = {("email" if k == "email_text" else k): v for k, v in row.items()}
    return rows


def load_cases(prompt_name: str) -> list[dict]:
    cases = json.loads((CASES / f"{prompt_name}.json").read_text(encoding="utf-8"))
    inputs = load_inputs()
    for c in cases:
        c["id"] = str(c["id"])
        if "input" not in c:
            if c["id"] not in inputs:
                raise KeyError(f"case {c['id']}: no input given and no row {c['id']} in inputs/emails.csv")
            c["input"] = inputs[c["id"]]
    return cases


def run_case(prompt, case: dict, temperature=None) -> dict:
    answer, info = ask(prompt.messages(**case["input"]), temperature=temperature)
    failures = check_case(answer, case["expect"])
    return {"id": case["id"], "answer": answer, "failures": failures, "pass": not failures, **info}


def run_cases(prompt_name: str, only=None, temperature=None, save=True, out=sys.stdout) -> list[dict]:
    prompt = load_prompt(prompt_name)
    cases = [c for c in load_cases(prompt_name) if only is None or c["id"] in only]
    print(f"{prompt_name} v{prompt.version} · {len(cases)} cases · model {model_name()}", file=out)
    results = []
    for c in cases:
        r = run_case(prompt, c, temperature); results.append(r)
        mark = "PASS" if r["pass"] else "FAIL"
        head = f"{mark}  {c['id']:<4} {r['answer'].splitlines()[0][:70] if r['answer'].strip() else '(empty answer)'}"
        print(head, file=out)
        for fmsg in r["failures"]:
            print(f"      {fmsg}", file=out)
    n = sum(r["pass"] for r in results)
    print(f"\n{n} of {len(results)} passed.", file=out)
    if save:
        RUNS.mkdir(exist_ok=True)
        path = RUNS / f"{time.strftime('%Y-%m-%d_%H%M%S')}_{prompt_name}_v{prompt.version}.json"
        path.write_text(json.dumps({"prompt": prompt_name, "version": prompt.version, "model": model_name(), "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"saved {path.relative_to(ROOT)}", file=out)
    return results
