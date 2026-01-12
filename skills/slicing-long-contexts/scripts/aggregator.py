#!/usr/bin/env python
"""
Aggregation helpers for RLM runs.
"""

import argparse
from pathlib import Path
from typing import List, Tuple

from slice_utils import Slice, load_manifest


def aggregate(sub_responses: List[Tuple[Slice, str]], dedup_lines: bool = False) -> str:
    lines: list[str] = []
    seen: set[str] = set()
    for sl, resp in sub_responses:
        line = f"[{sl.tag} {sl.start}:{sl.end}] {resp.strip()}"
        if dedup_lines:
            if line in seen:
                continue
            seen.add(line)
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate sub-responses based on manifest order.")
    parser.add_argument("--manifest", required=True, help="Path to manifest.json produced by slice_utils.")
    parser.add_argument("--subresp-dir", required=True, help="Directory containing rlm_subresp_<tag>.txt files.")
    parser.add_argument("--out", required=True, help="Output path for aggregated final.")
    parser.add_argument("--dedup-lines", action="store_true", help="Deduplicate identical lines in aggregation.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    subresp_dir = Path(args.subresp_dir)
    slices = load_manifest(manifest_path)
    sub_resps: List[Tuple[Slice, str]] = []
    for sl in slices:
        sub_path = subresp_dir / f"rlm_subresp_{sl.tag}.txt"
        if not sub_path.is_file():
            continue
        sub_resps.append((sl, sub_path.read_text(encoding="utf-8")))
    final = aggregate(sub_resps, dedup_lines=args.dedup_lines)
    Path(args.out).write_text(final, encoding="utf-8")
    print(f"Wrote aggregated final to {args.out}")


if __name__ == "__main__":
    main()
