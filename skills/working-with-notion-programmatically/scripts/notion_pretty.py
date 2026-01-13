#!/usr/bin/env python3
"""Pretty-print mcpc --json output from notion-search (and similar tools).

Usage:
  mcpc --json '@notion' tools-call notion-search query:="foo" query_type:="internal" | python scripts/notion_pretty.py
"""

import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


def _parse_payload(data: Any) -> Optional[Dict[str, Any]]:
    """Extract the nested JSON payload from mcpc --json output."""
    if isinstance(data, dict) and "results" in data:
        return data

    if isinstance(data, dict):
        content = data.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict):
                text = first.get("text")
                if isinstance(text, str):
                    try:
                        nested = json.loads(text)
                        if isinstance(nested, dict):
                            return nested
                    except json.JSONDecodeError:
                        return None
    return None


def _fmt_ts(ts: Optional[str]) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return ts


def _print_results(results: List[Dict[str, Any]], payload_type: Optional[str]) -> None:
    for r in results:
        title = r.get("title", "(untitled)")
        rtype = r.get("type", "")
        ts = _fmt_ts(r.get("timestamp"))
        url = r.get("url", "")
        highlight = r.get("highlight", "")
        print(f"- {title} | {rtype} | {ts} | {url} | highlight: {highlight}")
    print(f"\nType: {payload_type or 'unknown'} • Count: {len(results)}")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"Failed to read JSON from stdin: {exc}\n")
        return 1

    payload = _parse_payload(data)
    if not payload:
        sys.stderr.write("Could not find a results payload in the input.\n")
        return 1

    results = payload.get("results") or []
    if not isinstance(results, list) or not results:
        print("No results.")
        return 0

    _print_results(results, payload.get("type"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
