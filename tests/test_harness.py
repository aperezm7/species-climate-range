import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reveal_prints_the_background_solution():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    completed = subprocess.run(
        [sys.executable, "-m", "challenges", "reveal", "03"],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "def sample_background" in completed.stdout
    assert "--- explanation ---" in completed.stdout
    assert "Presence-only" in completed.stdout


def test_starters_raise_until_implemented():
    env = os.environ.copy()
    env.pop("CHALLENGE_SOLUTIONS", None)
    env["PYTHONPATH"] = str(ROOT)
    script = """
from challenges.loader import load_challenge
mod = load_challenge("04_roc_auc")
try:
    mod.roc_auc([0.2, 0.8], [0, 1])
except NotImplementedError:
    raise SystemExit(0)
raise SystemExit(1)
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr


def test_starters_do_not_import_hidden_solutions():
    for path in (ROOT / "challenges").glob("*/starter.py"):
        text = path.read_text(encoding="utf-8")
        assert "hidden" not in text
        assert "NotImplementedError" in text
