import subprocess
import sys
import tempfile
import os
from pathlib import Path

from config import load_config


def main():
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"[WARN] {e}. Continuing with defaults.")
        config = {}
    insights = config.get("insights", {})
    default_runner = Path.home() / ".gemini" / "skills" / "slicing-long-contexts" / "scripts" / "slice_runner.py"
    runner = Path(insights.get("slice_runner_path", default_runner)).expanduser()
    if not runner.exists():
        print(f"[FAIL] Runner not found at {runner}")
        return

    print(f"Runner found at {runner}")

    # Create dummy content
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
        tmp.write("This is a test document. " * 100)
        tmp_path = tmp.name

    try:
        out_dir = Path("./test_slicing_output")
        cmd = [
            sys.executable,
            str(runner),
            "--prompt",
            tmp_path,
            "--question",
            "Summarize this.",
            "--provider",
            insights.get("provider", "openai"),
            "--greedy-first",
            "--out-dir",
            str(out_dir),
            "--run-id",
            "test-run",
        ]

        print("Running command:", " ".join(cmd))
        res = subprocess.run(cmd, capture_output=True, text=True)

        print("Return Code:", res.returncode)
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    main()
