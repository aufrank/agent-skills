#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_results(path: Path) -> dict[str, bool]:
    results = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        key = f"{record['task_id']}#t{record['trial']}"
        results[key] = bool(record.get("passed"))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two eval result JSONL files.")
    parser.add_argument("--base", required=True, help="Base results.jsonl")
    parser.add_argument("--head", required=True, help="Head results.jsonl")
    parser.add_argument("--out", default="comparison.json", help="Output JSON path.")
    args = parser.parse_args()

    base = load_results(Path(args.base))
    head = load_results(Path(args.head))

    all_keys = sorted(set(base.keys()) | set(head.keys()))
    regressions = []
    improvements = []
    unchanged = []
    for key in all_keys:
        base_pass = base.get(key)
        head_pass = head.get(key)
        if base_pass is True and head_pass is False:
            regressions.append(key)
        elif base_pass is False and head_pass is True:
            improvements.append(key)
        else:
            unchanged.append(key)

    summary = {
        "base": args.base,
        "head": args.head,
        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,
    }

    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
