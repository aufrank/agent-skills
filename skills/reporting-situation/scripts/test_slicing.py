import subprocess
import sys
import tempfile
import os
from pathlib import Path

SLICING_SKILL_DIR = Path("/Users/aufrank/.gemini/skills/slicing-long-contexts")
RUNNER = SLICING_SKILL_DIR / "scripts/slice_runner.py"

def main():
    if not RUNNER.exists():
        print(f"[FAIL] Runner not found at {RUNNER}")
        return

    print(f"Runner found at {RUNNER}")
    
    # Create dummy content
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp.write("This is a test document. " * 100)
        tmp_path = tmp.name
        
    try:
        # Construct a 'greedy' run (no slicing needed) to test the mechanism
        # We need to specify a provider. 'gemini' is a good guess.
        # We also need an output dir
        out_dir = Path("./test_slicing_output")
        
        cmd = [
            sys.executable, str(RUNNER),
            "--prompt", tmp_path,
            "--question", "Summarize this.",
            "--provider", "gemini",
            "--greedy-first", # Should skip slicing for small doc
            "--out-dir", str(out_dir),
            "--run-id", "test-run"
        ]
        
        print("Running command:", " ".join(cmd))
        
    # Run with network + headings
    # This expects 'gemini' CLI to be available.
    subprocess.run([
        "python", str(skill_dir / "scripts" / "slice_runner.py"),

        res = subprocess.run(cmd, capture_output=True, text=True)
        
        print("Return Code:", res.returncode)
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == "__main__":
    main()
