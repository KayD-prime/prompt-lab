"""python -m promptlab run <prompt> [id ...]   ·   python -m promptlab show <prompt> <id>"""
import sys

from .runner import run_cases, load_inputs
from .prompts import load_prompt
from .client import ask


def main(argv):
    if len(argv) >= 2 and argv[0] == "run":
        results = run_cases(argv[1], only=set(argv[2:]) or None)
        sys.exit(0 if all(r["pass"] for r in results) else 1)
    if len(argv) == 3 and argv[0] == "show":
        prompt = load_prompt(argv[1]); inputs = load_inputs()
        if argv[2] not in inputs:
            sys.exit(f"no row {argv[2]} in inputs/emails.csv")
        messages = prompt.messages(**inputs[argv[2]])
        for m in messages:
            print(f"--- {m['role']}\n{m['content']}")
        print("--- answer"); answer, info = ask(messages)
        print(answer); print(f"\n[{info['model']} · {info['prompt_tokens']} in / {info['completion_tokens']} out · {info['seconds']} s]")
        return
    print(__doc__); sys.exit(2)


main(sys.argv[1:])
