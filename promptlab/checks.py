"""Checks: the small, mechanical questions you can ask of an answer. Each check is a function
(answer_fields, value) -> None, raising AssertionError with a plain sentence when the answer fails.

The answer is first parsed into fields: for the "Category: ...\nSummary: ..." format the fields are
category and summary; the whole text is always available as "text"."""
import json
import re

WORD = re.compile(r"\S+")


def parse_answer(text: str) -> dict:
    """Fields of an answer. Lines like "Category: Billing" become {"category": "Billing"}; the whole text is "text".
    A JSON answer (an object) contributes its keys too."""
    fields = {"text": text.strip()}
    for line in text.splitlines():
        m = re.match(r"\s*\**\s*([A-Za-z][A-Za-z _]{0,30}?)\s*\**\s*:\s*\**\s*(.+?)\s*\**\s*$", line)
        if m:
            key = m.group(1).strip().lower().replace(" ", "_")
            fields.setdefault(key, m.group(2).strip())
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            for k, v in obj.items():
                fields.setdefault(str(k).lower(), v if isinstance(v, str) else json.dumps(v))
    except (json.JSONDecodeError, TypeError):
        pass
    return fields


def _field(fields, name):
    if name not in fields:
        raise AssertionError(f"the answer has no '{name.capitalize()}:' line; got: {fields['text'][:80]!r}")
    return fields[name]


def c_category(fields, want):
    got = _field(fields, "category").strip(" .*")
    if got.lower() != str(want).lower():
        raise AssertionError(f"category is {got!r}, expected {want!r}")


def c_category_in(fields, want):
    got = _field(fields, "category").strip(" .*")
    if got.lower() not in [w.lower() for w in want]:
        raise AssertionError(f"category is {got!r}, expected one of {want}")


def c_mentions(fields, words):
    low = _field(fields, "summary").lower() if "summary" in fields else fields["text"].lower()
    missing = [w for w in ([words] if isinstance(words, str) else words) if w.lower() not in low]
    if missing:
        raise AssertionError(f"{'summary' if 'summary' in fields else 'answer'} does not mention {missing}")


def c_not_mentions(fields, words):
    low = fields["text"].lower()
    found = [w for w in ([words] if isinstance(words, str) else words) if w.lower() in low]
    if found:
        raise AssertionError(f"answer mentions {found}, which it must not")


def c_max_words(fields, n):
    """On a Category/Summary answer, the summary's length; on a free-text answer (a reply, a paragraph), the whole answer's."""
    s = fields["summary"] if "summary" in fields else fields["text"]
    k = len(WORD.findall(s))
    if k > int(n):
        raise AssertionError(f"{'summary' if 'summary' in fields else 'answer'} is {k} words, limit {n}")


def c_one_sentence(fields, _flag=True):
    s = _field(fields, "summary").strip()
    parts = [p for p in re.split(r"(?<=[.!?])\s+", s) if p.strip()]
    if len(parts) > 1:
        raise AssertionError(f"summary is {len(parts)} sentences, expected one")


def c_format(fields, keys):
    missing = [k for k in keys if k.lower() not in fields]
    if missing:
        raise AssertionError(f"answer is missing the line(s) {missing}; got: {fields['text'][:80]!r}")


def c_is_json(fields, _flag=True):
    try:
        json.loads(fields["text"])
    except json.JSONDecodeError as e:
        raise AssertionError(f"answer is not valid JSON ({e.msg})")


def c_regex(fields, pattern):
    if not re.search(pattern, fields["text"]):
        raise AssertionError(f"answer does not match /{pattern}/")


def c_equals(fields, want: dict):
    """{"field": "value", ...}: each named line must equal the value (case-insensitive). Works for any prompt's fields."""
    for name, value in want.items():
        got = _field(fields, name.lower()).strip(" .*")
        if got.lower() != str(value).lower():
            raise AssertionError(f"{name} is {got!r}, expected {value!r}")


CHECKS = {"equals": c_equals, "category": c_category, "category_in": c_category_in, "mentions": c_mentions, "not_mentions": c_not_mentions,
          "max_words": c_max_words, "one_sentence": c_one_sentence, "format": c_format, "is_json": c_is_json, "regex": c_regex}


def check_case(answer: str, expect: dict) -> list[str]:
    """Run every check in expect against the answer. Returns the list of failure messages (empty means pass)."""
    fields = parse_answer(answer)
    failures = []
    for name, value in expect.items():
        if name not in CHECKS:
            raise KeyError(f"unknown check {name!r}; known: {sorted(CHECKS)}")
        try:
            CHECKS[name](fields, value)
        except AssertionError as e:
            failures.append(f"{name}: {e}")
    return failures
