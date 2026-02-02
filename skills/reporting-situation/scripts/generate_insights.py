#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Generate insights from Situation Report Corpus")
    parser.add_argument("--corpus", default="situation_corpus.md", help="Path to corpus file")
    parser.add_argument("--out-dir", default="reports/insights", help="Output directory")
    args = parser.parse_args()

    skill_root = Path(__file__).parent.parent
    corpus_path = Path(args.corpus).resolve()
    
    if not corpus_path.exists():
        # Try looking in skill root
        corpus_path = skill_root / args.corpus
        if not corpus_path.exists():
            print(f"[ERROR] Corpus not found at {args.corpus} or {corpus_path}")
            sys.exit(1)

    print(f"Using corpus: {corpus_path}")

    # Locate Slicing Skill
    # We assume standard installation structure or explicit path
    slicing_skill_path = Path.home() / ".gemini" / "skills" / "slicing-long-contexts" / "scripts" / "slice_runner.py"
    if not slicing_skill_path.exists():
        print(f"[ERROR] Slicing skill not found at {slicing_skill_path}")
        sys.exit(1)

    # Read Templates
    worker_tmpl = (skill_root / "templates" / "insight_worker.txt").read_text()
    reducer_tmpl = (skill_root / "templates" / "insight_reducer.txt").read_text()

    # Wrapper script path
    wrapper_path = skill_root / "scripts" / "run_gemini.sh"

    # Generate unique run ID
    run_id = f"sitrep_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Construct Command
    # We pass the prompt content via CLI args. 
    # Note: slice_runner expects --sub-system-prompt and --summary-system-prompt
    
    cmd = [
        "python", str(slicing_skill_path),
        "--prompt", str(corpus_path),
        "--question", "Extract key insights, decisions, and action items.",
        "--provider", "openai",  # Use 'openai' to avoid runner defaults
        "--chunk-size", "40000",
        "--prefer-headings",
        "--max-slices", "10",
        "--out-dir", f"{args.out_dir}/{run_id}", # Output to unique dir
        "--run-id", run_id,
        "--cmd-template", f"cat {{prompt_path}} | {wrapper_path} --approval-mode plan",
        "--summary-cmd-template", f"cat {{prompt_path}} | {wrapper_path} --approval-mode plan",
        "--sub-system-prompt", worker_tmpl,
        "--summary-system-prompt", reducer_tmpl,
        "--summary-out", f"{args.out_dir}/Executive_Summary.md" # Keep final summary in fixed location
    ]

    print(f">>> Launching Slice Runner (Run ID: {run_id})...")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n>>> Success! Report generated at: {args.out_dir}/Executive_Summary.md")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Slice Runner failed with code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
