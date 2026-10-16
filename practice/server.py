"""Starts the practice server in the background on a free port and points the openai library at it."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path


def start():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
    proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name("practice_models.py")), str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close(); break
        except OSError:
            time.sleep(0.1)
    else:
        proc.kill(); raise RuntimeError("the practice model server did not start")
    url = f"http://127.0.0.1:{port}/v1"
    os.environ.update(OPENAI_BASE_URL=url, OPENAI_API_KEY="practice-key")
    os.environ.setdefault("MODEL", "practice-model")
    import atexit; atexit.register(proc.kill)
    return proc, url
