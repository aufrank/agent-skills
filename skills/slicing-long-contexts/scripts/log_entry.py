#!/usr/bin/env python
"""
CLI helper to append structured entries to a JSONL log (e.g., progress.log or results.json).
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from log_utils import append_log


def parse_kv(values) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for item in values or []:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        data[k] = v
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Append a JSON entry to a log file.")
    parser.add_argument("--log", required=True, help="Path to log file (JSONL).")
    parser.add_argument("--id", dest="run_id", help="Run identifier (optional).")
    parser.add_argument("--step", help="Step name (optional).")
    parser.add_argument("--status", help="Status value (optional).")
    parser.add_argument("--data", help="Additional JSON data to merge (string).")
    parser.add_argument("--kv", action="append", help="Extra key=value pairs to merge.", default=[])
    parser.add_argument("--timestamp", action="store_true", help="Add UTC ISO8601 timestamp field 'ts'.")
    args = parser.parse_args()

    entry: Dict[str, Any] = {}
    if args.timestamp:
        entry["ts"] = datetime.now(timezone.utc).isoformat()
    if args.run_id:
        entry["id"] = args.run_id
    if args.step:
        entry["step"] = args.step
    if args.status:
        entry["status"] = args.status
    if args.kv:
        entry.update(parse_kv(args.kv))
    if args.data:
        try:
            extra = json.loads(args.data)
            if isinstance(extra, dict):
                entry.update(extra)
        except json.JSONDecodeError:
            entry["data_parse_error"] = "invalid JSON in --data"
            entry["data_raw"] = args.data

    append_log(Path(args.log), entry)
    print(f"Appended entry to {args.log}")


if __name__ == "__main__":
    main()
