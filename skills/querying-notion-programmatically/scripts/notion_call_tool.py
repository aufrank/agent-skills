#!/usr/bin/env python3
"""
Generic Notion mcpc tool caller with cached tools-list/tools-get.
Writes tool outputs to results/ while keeping schemas in mcp_tools/.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from notion_common import (  # noqa: E402
    DEFAULT_PROFILE,
    DEFAULT_SERVER,
    ensure_auth,
    ensure_dir,
    get_mcpc_cmd,
    skill_cache_roots,
    timestamped_path,
    write_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call any Notion MCP tool with cached schemas.")
    parser.add_argument("--tool", required=True, help="Tool name to call (e.g., notion-search).")
    parser.add_argument(
        "--arg",
        action="append",
        default=[],
        help="Argument in key:=value form. Repeatable.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path (default: results/<tool>.json).",
    )
    parser.add_argument("--timestamp-output", action="store_true", help="Append UTC timestamp to output filename.")
    parser.add_argument("--refresh-cache", action="store_true", help="Force refresh of tools-list and tool schema.")
    parser.add_argument("--session", default="@notion", help="mcpc session or server URL. Quote @notion in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile (default: env MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Notion MCP server (default: https://mcp.notion.com/mcp).")
    return parser.parse_args()


def run_mcpc(cmd: List[str]) -> Dict[str, Any]:
    print("Executing:", " ".join(cmd))
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        sys.stderr.write(f"mcpc exited with status {completed.returncode}\n")
        sys.stderr.write(completed.stderr)
        sys.exit(completed.returncode)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to parse mcpc JSON output: {exc}\n")
        sys.exit(1)


def cache_tools_list(mcpc_cmd: List[str], profile: str, session: str, refresh: bool, path: Path) -> Dict[str, Any]:
    if path.exists() and not refresh:
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    data = run_mcpc([*mcpc_cmd, "--json", "--profile", profile, session, "tools-list"])
    ensure_dir(path.parent)
    write_json(path, data)
    return data


def cache_tool_schema(mcpc_cmd: List[str], profile: str, session: str, tool: str, refresh: bool, path: Path) -> Dict[str, Any]:
    if path.exists() and not refresh:
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    data = run_mcpc([*mcpc_cmd, "--json", "--profile", profile, session, "tools-get", tool])
    ensure_dir(path.parent)
    write_json(path, data)
    return data


def _extract_tools(tools_payload: Any) -> List[Dict[str, Any]]:
    if isinstance(tools_payload, dict):
        maybe_list = tools_payload.get("tools") or tools_payload.get("content") or []
    else:
        maybe_list = tools_payload
    if isinstance(maybe_list, list):
        return [t for t in maybe_list if isinstance(t, dict)]
    return []


def main() -> None:
    args = parse_args()
    ensure_auth(args.server, args.profile, args.session)

    mcpc_cmd = get_mcpc_cmd()
    roots = skill_cache_roots("querying-notion-programmatically")
    mcp_tools_dir = roots["mcp_tools_root"]
    tools_list_path = mcp_tools_dir / "tools-list.json"
    tool_schema_path = mcp_tools_dir / f"{args.tool}.json"

    tools_list = cache_tools_list(mcpc_cmd, args.profile, args.session, args.refresh_cache, tools_list_path)
    # Warn if tool not in list
    available = {t.get("name") for t in _extract_tools(tools_list)}
    if available and args.tool not in available:
        sys.stderr.write(f"Warning: tool '{args.tool}' not found in cached tools-list.\n")

    cache_tool_schema(mcpc_cmd, args.profile, args.session, args.tool, args.refresh_cache, tool_schema_path)

    output_path = Path(args.output) if args.output else roots["results_root"] / f"{args.tool}.json"
    output_path = timestamped_path(output_path, args.timestamp_output)
    ensure_dir(output_path.parent)

    tool_cmd: List[str] = [*mcpc_cmd, "--json", "--profile", args.profile, args.session, "tools-call", args.tool]
    for arg in args.arg:
        if ":=" not in arg:
            sys.stderr.write(f"Skipping arg without ':=': {arg}\n")
            continue
        tool_cmd.append(arg)

    result = run_mcpc(tool_cmd)
    write_json(output_path, result)
    print(f"Output saved to {output_path}")


if __name__ == "__main__":
    main()
