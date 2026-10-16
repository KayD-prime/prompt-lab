"""pytest finds this file first: it makes the repository root importable and prints which model the run used."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv()


def pytest_report_header(config):
    from promptlab.client import practice_mode
    if practice_mode():
        return "promptlab: no OPENAI_API_KEY (or PROMPTLAB_PRACTICE=1), so the practice server answers. Free, offline, canned."
    return f"promptlab: model {os.environ.get('MODEL')} at {os.environ.get('OPENAI_BASE_URL', 'api.openai.com')}"
