"""One function, ask(): the model call every run goes through. Settings come from .env (OPENAI_BASE_URL,
OPENAI_API_KEY, MODEL); with PROMPTLAB_PRACTICE=1, or no key at all, the practice server answers instead."""
import os
import time

from dotenv import load_dotenv

load_dotenv()
_client = None
_practice = None


def practice_mode() -> bool:
    key = os.environ.get("OPENAI_API_KEY", "")
    return os.environ.get("PROMPTLAB_PRACTICE") == "1" or not key or "your_key" in key


def _ensure_practice():
    """Start the practice server once (practice/practice_models.py) and point the client at it."""
    global _practice
    if _practice is None:
        from practice import server
        _practice, url = server.start()
        os.environ["MODEL"] = os.environ.get("MODEL") or "practice-model"


def client():
    global _client
    if _client is None:
        if practice_mode():
            _ensure_practice()
        from openai import OpenAI
        _client = OpenAI()
    return _client


def model_name() -> str:
    return os.environ.get("MODEL", "practice-model")


def ask(messages: list[dict], temperature: float | None = None, max_tokens: int = 600) -> tuple[str, dict]:
    """Send the messages, return (answer text, info). info has model, prompt_tokens, completion_tokens, seconds."""
    c = client(); m = model_name()
    kw = dict(model=m, messages=messages, max_tokens=max_tokens)
    if temperature is not None:
        kw["temperature"] = temperature
    if "gpt-oss" in m:                      # a reasoning model: keep its thinking short so the answer fits max_tokens
        kw["reasoning_effort"] = "low"
    t0 = time.perf_counter()
    r = c.chat.completions.create(**kw)
    text = r.choices[0].message.content or ""
    u = r.usage
    return text, {"model": r.model, "prompt_tokens": u.prompt_tokens if u else None,
                  "completion_tokens": u.completion_tokens if u else None, "seconds": round(time.perf_counter() - t0, 2),
                  "finish_reason": r.choices[0].finish_reason}
