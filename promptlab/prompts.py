"""A prompt is a Markdown file in prompts/ with a front matter block and up to two parts, System and User.

    ---
    name: triage
    version: 1
    ---
    ## System
    You are ...          (optional: if there is no System part, everything goes in the user message)
    ## User
    Classify ... {{email}}

{{email}} is filled in from the input. Keep the fixed wording first and the input last: the model reads it in order."""
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"


@dataclass
class Prompt:
    name: str
    version: str
    system: str | None
    user: str
    meta: dict = field(default_factory=dict)

    def messages(self, **inputs) -> list[dict]:
        """The messages list for one input: a system message (when there is one) and the filled-in user message."""
        msgs = []
        if self.system:
            msgs.append({"role": "system", "content": self.system})
        msgs.append({"role": "user", "content": fill(self.user, inputs)})
        return msgs


def fill(template: str, inputs: dict) -> str:
    def sub(m):
        key = m.group(1).strip()
        if key not in inputs:
            raise KeyError(f"the prompt needs {{{{{key}}}}} but the input has no '{key}'")
        return str(inputs[key])
    return re.sub(r"\{\{(.*?)\}\}", sub, template)


def parse(text: str, name: str = "") -> Prompt:
    meta, body = {}, text
    m = re.match(r"\s*---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip()
        body = text[m.end():]
    parts = {}
    for sec in re.split(r"^## +", body, flags=re.M):
        if not sec.strip():
            continue
        head, _, content = sec.partition("\n")
        parts[head.strip().lower()] = content.strip("\n")
    if "user" not in parts:
        parts = {"user": body.strip("\n")}
    return Prompt(meta.get("name", name), str(meta.get("version", "1")), parts.get("system"), parts["user"], meta)


def load_prompt(name: str) -> Prompt:
    """prompts/<name>.md, parsed. The file is the prompt: edit it, commit it, diff it like code."""
    path = Path(name) if name.endswith(".md") else PROMPTS / f"{name}.md"
    return parse(path.read_text(encoding="utf-8"), path.stem)
