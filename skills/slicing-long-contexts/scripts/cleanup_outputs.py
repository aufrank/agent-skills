#!/usr/bin/env python
"""
Cleanup helper for RLM runs.
Removes generated slices, prompts, subresponses, summaries, finals, or entire runs under rlm_outputs.
"""

import argparse
import shutil
from pathlib import Path


def collect_targets(target: str) -> list[Path]:
    out_dir = Path("rlm_outputs")
    targets = {
        "runs": [out_dir],
        "slices": list(out_dir.glob("**/rlm_slice_*")),
        "prompts": list(out_dir.glob("**/rlm_prompt_*")),
        "responses": list(out_dir.glob("**/rlm_subresp_*")),
        "summary": list(out_dir.glob("**/rlm_summary.txt")),
        "final": list(out_dir.glob("**/rlm_final.txt")),
        "manifest": list(out_dir.glob("**/manifest.json")),
    }
    if target == "all":
        merged = []
        for paths in targets.values():
            merged.extend(paths)
        return merged
    if target not in targets:
        raise SystemExit(f"Unknown cleanup target: {target}")
    return targets[target]


def cleanup(target: str, dry_run: bool = False) -> None:
    paths = collect_targets(target)
    for p in paths:
        if not p.exists():
            continue
        if p.is_file():
            if dry_run:
                print(f"[dry-run] would remove file {p}")
            else:
                p.unlink()
        elif p.is_dir():
            if dry_run:
                print(f"[dry-run] would remove dir {p}")
            else:
                shutil.rmtree(p, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cleanup generated RLM artifacts under rlm_outputs.")
    parser.add_argument(
        "--target",
        choices=["runs", "slices", "prompts", "responses", "summary", "final", "manifest", "all"],
        required=True,
        help="What to delete.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be deleted without removing.")
    args = parser.parse_args()
    cleanup(args.target, dry_run=args.dry_run)
    msg = "Dry-run complete." if args.dry_run else f"Cleanup '{args.target}' completed."
    print(msg)


if __name__ == "__main__":
    main()
