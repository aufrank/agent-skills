#!/usr/bin/env python3
"""
Wrapper for running mcpc Notion searches with simple flags.
Outputs parsed payloads to file and supports ID-only/pretty printing.
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
    cmd: list[str] = [*get_mcpc_cmd(), "--json", "--profile", args.profile]
    cmd.extend(
        [
            args.session,
            "tools-call",
            "notion-search",
            f"query:={args.query}",
            f"query_type:={args.query_type}",
        ]
    )
    return cmd


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print("Executing:", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run notion-search via mcpc with convenient flags.")
    parser.add_argument("--query", required=True, help="Search text. For people lookup, set query_type to user.")
    parser.add_argument("--query-type", default="internal", choices=["internal", "user"], help="Search content in workspace (internal) or users.")
    parser.add_argument("--ids-only", action="store_true", help="Print id url title only.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print results.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL. Quote @notion in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile to use (default: from MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server (default: https://mcp.notion.com/mcp).")
    parser.add_argument("--output", default="results/query.search.json", help="Path to write parsed search payload.")
    parser.add_argument("--timestamp-output", action="store_true", help="Append UTC timestamp to output filename.")

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

    payload = parse_mcpc_payload(data)
    if not payload or not isinstance(payload, dict):
        sys.stderr.write("Could not find a results payload in the input.\n")
        sys.exit(1)

    results = payload.get("results") or []
    if args.output:
        out_path = timestamped_path(Path(args.output), args.timestamp_output)
        write_json(out_path, payload)

    if not isinstance(results, list) or not results:
        print("No results.")
        if args.output:
            print(f"Raw payload saved to {out_path}")
        sys.exit(0)

    if args.ids_only:
        _print_ids(results)
    else:
        _print_results(results, payload.get("type"))
        if args.output:
            print(f"\nRaw payload saved to {out_path}")


if __name__ == "__main__":
    main()
