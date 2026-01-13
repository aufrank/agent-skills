#!/usr/bin/env python3
"""
Rovo/Jira search via mcpc `search` tool. Minimal parsing; writes payload to file.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from jira_common import DEFAULT_PROFILE, DEFAULT_SERVER, ensure_auth, get_mcpc_cmd, skill_cache_roots, write_json  # noqa: E402


def _print_summary(payload: Dict[str, Any]) -> None:
    results = payload.get("results")
    if not isinstance(results, list):
        print(f"Results: {type(results).__name__}")
        return
    print(f"Results count: {len(results)}")
    for r in results[:20]:
        if not isinstance(r, dict):
            continue
        title = r.get("title") or r.get("summary") or ""
        url = r.get("url") or ""
        key = r.get("id") or r.get("key") or ""
        print(f"- {key} {title} {url}".strip())
    if len(results) > 20:
        print(f"... {len(results) - 20} more")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Jira Rovo search via mcpc.")
    parser.add_argument("--query", required=True, help="Search text.")
    parser.add_argument("--session", default="@jira", help="mcpc session or server URL. Quote @jira in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile (default: env MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Jira MCP server (default: https://mcp.atlassian.com/v1/mcp).")
    parser.add_argument("--output", default=None, help="Path to write parsed search payload (default results/jira.search.json).")
    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)
    mcpc_cmd = get_mcpc_cmd()
    roots = skill_cache_roots()
    output_path = Path(args.output) if args.output else roots["results_root"] / "jira.search.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        *mcpc_cmd,
        "--json",
        "--profile",
        args.profile,
        args.session,
        "tools-call",
        "search",
        f"query:={args.query}",
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

    write_json(output_path, data)
    print(f"Raw payload saved to {output_path}")
    if isinstance(data, dict):
        _print_summary(data)


if __name__ == "__main__":
    main()
