#!/usr/bin/env python3
"""
Extract user mentions (user://...) from Notion fetch payloads and write ID lists/counts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

from notion_common import resolve_path

USER_RE = re.compile(r"user://[0-9a-fA-F-]+")


def _load_payload(path: Path) -> Dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to load {path}: {exc}")


def _extract_users_from_payload(payload: Dict) -> List[str]:
    # Look at text field primarily; fall back to JSON dump
    text = payload.get("text", "")
    matches = USER_RE.findall(text)
    if matches:
        return matches
    # fallback: scan entire JSON string
    blob = json.dumps(payload)
    return USER_RE.findall(blob)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract user mentions from Notion payload JSON files.")
    parser.add_argument("--payload-dir", default="results/payloads", help="Directory containing payload JSON files.")
    parser.add_argument("--payload", help="Single payload JSON file to parse (overrides --payload-dir).")
    parser.add_argument("--ids-output", default="results/mentions.ids.txt", help="Path to write unique user IDs.")
    parser.add_argument("--counts-output", default="results/mentions.json", help="Path to write counts per user and per file.")
    args = parser.parse_args()

    files: List[Path] = []
    if args.payload:
        files = [resolve_path(args.payload)]
    else:
        payload_dir = Path(args.payload_dir)
        if not payload_dir.exists():
            sys.stderr.write(f"Payload dir not found: {payload_dir}\n")
            sys.exit(1)
        files = sorted(resolve_path(payload_dir).glob("*.json"))
        if not files:
            sys.stderr.write(f"No payload JSON files found in {payload_dir}\n")
            sys.exit(1)

    per_file: Dict[str, List[str]] = {}
    total_counter: Counter[str] = Counter()
    for path in files:
        payload = _load_payload(path)
        users = _extract_users_from_payload(payload)
        per_file[str(path)] = users
        total_counter.update(users)

    uniq_ids = list(dict.fromkeys(total_counter.keys()))  # preserve order
    ids_path = resolve_path(args.ids_output)
    counts_path = resolve_path(args.counts_output)
    ids_path.parent.mkdir(parents=True, exist_ok=True)
    counts_path.parent.mkdir(parents=True, exist_ok=True)
    ids_path.write_text("\n".join(uniq_ids), encoding="utf-8")

    counts_payload = {
        "total": total_counter,
        "per_file": per_file,
    }
    counts_path.write_text(json.dumps(counts_payload, indent=2), encoding="utf-8")
    print(f"Wrote user IDs to {args.ids_output}")
    print(f"Wrote counts to {args.counts_output}")


if __name__ == "__main__":
    main()