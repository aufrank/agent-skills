#!/usr/bin/env python3
"""
Fetch and pretty-print comments for a Notion page via mcpc.
Writes parsed comments to file for reuse.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from notion_common import DEFAULT_PROFILE, DEFAULT_SERVER, ensure_auth, get_mcpc_cmd, parse_mcpc_payload, timestamped_path, write_json  # noqa: E402


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


def _rich_text_to_plain(rich_text: Any) -> str:
    if not isinstance(rich_text, list):
        return ""
    parts: List[str] = []
    for item in rich_text:
        if isinstance(item, dict):
            text = item.get("plain_text") or item.get("text", {}).get("content")
            if text:
                parts.append(text)
    return "".join(parts)


def _print_comments(results: List[Dict[str, Any]]) -> None:
    for r in results:
        author = ""
        created_by = r.get("created_by") or {}
        if isinstance(created_by, dict):
            author = created_by.get("name") or created_by.get("id") or ""
        ts = _fmt_ts(r.get("created_time") or r.get("last_edited_time"))
        text = _rich_text_to_plain(r.get("rich_text"))
        print(f"- {ts} | {author} | {text}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch comments for a Notion page and pretty-print them.")
    parser.add_argument("--page-id", required=True, help="Notion page ID or URL.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL. Quote @notion in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile to use (default: from MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server (default: https://mcp.notion.com/mcp).")
    parser.add_argument("--output", default="results/comments.json", help="Path to write parsed comments JSON.")
    parser.add_argument("--timestamp-output", action="store_true", help="Append UTC timestamp to output filename.")
    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)

    cmd = [
        *get_mcpc_cmd(),
        "--json",
        "--profile",
        args.profile,
        args.session,
        "tools-call",
        "notion-get-comments",
        f"page_id:={args.page_id}",
    ]
    print("Executing:", " ".join(cmd))
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        sys.stderr.write(f"mcpc exited with status {completed.returncode}\n")
        sys.stderr.write(completed.stderr)
        sys.exit(completed.returncode)

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to parse mcpc JSON output: {exc}\n")
        sys.exit(1)

    payload = parse_mcpc_payload(data)
    if not payload or not isinstance(payload, dict):
        sys.stderr.write("Could not find a results payload in the input.\n")
        sys.exit(1)

    results = payload.get("results") or []
    if args.output:
        out_path = timestamped_path(Path(args.output), args.timestamp_output)
        write_json(out_path, payload)
        print(f"Comments saved to {out_path}")

    if not isinstance(results, list) or not results:
        print("No comments.")
        sys.exit(0)

    _print_comments(results)


if __name__ == "__main__":
    main()
