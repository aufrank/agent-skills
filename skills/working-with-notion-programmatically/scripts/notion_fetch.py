#!/usr/bin/env python3
"""
Wrapper for running mcpc Notion fetches with readable arguments.
Writes raw JSON to file for reuse.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

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


def build_command(args: argparse.Namespace) -> list[str]:
    return [
        get_mcpc_bin(),
        "--json",
        "--profile",
        args.profile,
        args.session,
        "tools-call",
        "notion-fetch",
        f"id:={args.id}",
    ]


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print("Executing:", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run notion-fetch via mcpc with convenient flags.")
    parser.add_argument("--id", required=True, help="Notion page or database URL/ID.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL. Quote @notion in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile to use (default: from MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server (default: https://mcp.notion.com/mcp).")
    parser.add_argument("--output", default="results/fetch.json", help="Path to write fetched JSON payload.")

    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)
    cmd = build_command(args)
    completed = run_command(cmd)

    if completed.returncode != 0:
        sys.stderr.write(f"mcpc exited with status {completed.returncode}\n")
        sys.stderr.write(completed.stderr)
        sys.exit(completed.returncode)

    try:
        data: Any = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to parse mcpc JSON output: {exc}\n")
        sys.exit(1)

    if args.output:
        write_json(Path(args.output), data)
        print(f"Payload saved to {args.output}")
    else:
        print(completed.stdout)


if __name__ == "__main__":
    main()
