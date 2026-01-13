#!/usr/bin/env python3
"""
Wrapper for running mcpc Notion searches with readable arguments.
Adds built-in pretty/ID-only output and writes parsed results to file.
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

from notion_common import (
    DEFAULT_PROFILE,
    DEFAULT_SERVER,
    ensure_auth,
    get_mcpc_bin,
    write_json,
)


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


def _print_ids(results: List[Dict[str, Any]]) -> None:
    for r in results:
        print(f"{r.get('id','')} {r.get('url','')} {r.get('title','(untitled)')}")


def build_command(args: argparse.Namespace) -> list[str]:
    cmd: list[str] = [get_mcpc_bin(), "--json", "--profile", args.profile]
    cmd.extend(
        [
            args.session,
            "tools-call",
            "notion-search",
            f"query:={args.query}",
            f"query_type:={args.query_type}",
        ]
    )

    if args.content_search_mode:
        cmd.append(f"content_search_mode:={args.content_search_mode}")
    if args.page_url:
        cmd.append(f"page_url:={args.page_url}")
    if args.data_source_url:
        cmd.append(f"data_source_url:={args.data_source_url}")
    if args.teamspace_id:
        cmd.append(f"teamspace_id:={args.teamspace_id}")

    filters = args.filters
    if args.created_by:
        filters = filters or json.dumps({"created_by_user_ids": [args.created_by]})
    if filters:
        cmd.append(f"filters:={filters}")

    return cmd


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print("Executing:", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run notion-search via mcpc with convenient flags.")
    parser.add_argument("--query", required=True, help="Search text. For people lookup, set query_type to user.")
    parser.add_argument("--query-type", default="internal", choices=["internal", "user"], help="Search content in workspace (internal) or users.")
    parser.add_argument("--content-search-mode", choices=["workspace_search", "ai_search"], help="Override Notion search mode.")
    parser.add_argument("--page-url", help="Restrict search to a page/tree (URL or ID).")
    parser.add_argument("--data-source-url", help="Restrict search to a database data source (collection://...).")
    parser.add_argument("--teamspace-id", help="Restrict search to a teamspace ID.")
    parser.add_argument(
        "--filters",
        help="JSON object for filters (created_by_user_ids, created_date_range, etc.). Pass as a JSON string.",
    )
    parser.add_argument("--created-by", help="Creator user ID (UUID) to filter results. Shorthand for filters.created_by_user_ids=[id].")
    parser.add_argument("--ids-only", action="store_true", help="Print id url title only.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print results.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL. Quote @notion in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile to use (default: from MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server (default: https://mcp.notion.com/mcp).")
    parser.add_argument("--output", default="results/search.json", help="Path to write parsed search payload.")

    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)
    cmd = build_command(args)
    completed = run_command(cmd)

    if completed.returncode != 0:
        sys.stderr.write(f"mcpc exited with status {completed.returncode}\n")
        sys.stderr.write(completed.stderr)
        sys.exit(completed.returncode)

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to parse mcpc JSON output: {exc}\n")
        sys.exit(1)

    payload = _parse_payload(data)
    if not payload:
        sys.stderr.write("Could not find a results payload in the input.\n")
        sys.exit(1)

    results = payload.get("results") or []
    if not isinstance(results, list) or not results:
        print("No results.")
        if args.output:
            write_json(Path(args.output), payload)
        sys.exit(0)

    if args.output:
        write_json(Path(args.output), payload)

    if args.ids_only:
        _print_ids(results)
    else:
        _print_results(results, payload.get("type"))
        print(f"\nRaw payload saved to {args.output}")


if __name__ == "__main__":
    main()
