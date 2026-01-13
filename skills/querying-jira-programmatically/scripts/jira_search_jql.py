#!/usr/bin/env python3
"""
JQL search via mcpc `searchJiraIssuesUsingJql`.
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

from jira_common import (  # noqa: E402
    DEFAULT_CLOUD_ID,
    DEFAULT_PROFILE,
    DEFAULT_SERVER,
    ensure_auth,
    get_mcpc_cmd,
    parse_mcpc_payload,
    skill_cache_roots,
    timestamped_path,
    write_json,
)


def _print_issues(payload: Dict[str, Any]) -> None:
    issues = payload.get("issues") or []
    if not isinstance(issues, list):
        print(f"Issues: {type(issues).__name__}")
        return
    print(f"Issues count: {len(issues)}")
    for issue in issues[:20]:
        if not isinstance(issue, dict):
            continue
        key = issue.get("key", "")
        fields = issue.get("fields", {}) if isinstance(issue.get("fields"), dict) else {}
        summary = fields.get("summary", "")
        status = fields.get("status", {}).get("name", "") if isinstance(fields.get("status"), dict) else ""
        print(f"- {key} [{status}] {summary}")
    if len(issues) > 20:
        print(f"... {len(issues) - 20} more")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run JQL search via mcpc searchJiraIssuesUsingJql.")
    parser.add_argument("--jql", required=True, help="JQL string.")
    parser.add_argument("--max-results", type=int, default=50, help="Max results (default 50).")
    parser.add_argument("--cloud-id", default=DEFAULT_CLOUD_ID, help="Jira cloudId (default: ae3605cc-2ea8-41ef-86e8-c7cda3a94bc0).")
    parser.add_argument("--fields", help="Comma-separated field names to return (default: tool schema defaults).")
    parser.add_argument("--session", default="@jira", help="mcpc session or server URL. Quote @jira in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile (default: env MCP_PROFILE or 'default').")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Jira MCP server (default: https://mcp.atlassian.com/v1/mcp).")
    parser.add_argument("--output", default=None, help="Path to write parsed search payload (default results/jira.jql.json).")
    parser.add_argument("--raw-output", default=None, help="Optional path to write raw mcpc response.")
    parser.add_argument("--no-output", action="store_true", help="Skip writing parsed output to disk.")
    parser.add_argument("--timestamp-output", action="store_true", help="Append UTC timestamp to output filenames.")
    parser.add_argument("--pages", type=int, default=1, help="Fetch up to this many pages when nextPageToken is present (default 1).")
    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)
    mcpc_cmd = get_mcpc_cmd()
    roots = skill_cache_roots()
    output_path = Path(args.output) if args.output else roots["results_root"] / "jira.jql.json"
    output_path = timestamped_path(output_path, args.timestamp_output)
    if not args.no_output:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    raw_output_path = Path(args.raw_output) if args.raw_output else None
    if raw_output_path:
        raw_output_path = timestamped_path(raw_output_path, args.timestamp_output)
    if raw_output_path:
        raw_output_path.parent.mkdir(parents=True, exist_ok=True)

    merged_issues: list[dict[str, Any]] = []
    fields_arg = None
    if args.fields:
        fields_list = [f.strip() for f in args.fields.split(",") if f.strip()]
        if fields_list:
            fields_arg = json.dumps(fields_list)
    next_token = None
    raw_collected: list[Any] = []

    for page in range(max(args.pages, 1)):
        call_args = [
            *mcpc_cmd,
            "--json",
            "--profile",
            args.profile,
            args.session,
            "tools-call",
            "searchJiraIssuesUsingJql",
            f"cloudId:={args.cloud_id}",
            f"jql:={args.jql}",
            f"maxResults:={args.max_results}",
        ]
        if fields_arg:
            call_args.append(f"fields:={fields_arg}")
        if next_token:
            call_args.append(f"nextPageToken:={next_token}")

        print("Executing:", " ".join(call_args))
        completed = subprocess.run(call_args, capture_output=True, text=True)
        if completed.returncode != 0:
            sys.stderr.write(f"mcpc exited with status {completed.returncode}\n")
            sys.stderr.write(completed.stderr)
            sys.exit(completed.returncode)

        try:
            raw_data = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"Failed to parse mcpc JSON output: {exc}\n")
            sys.exit(1)
        raw_collected.append(raw_data)

        parsed = parse_mcpc_payload(raw_data)
        if isinstance(parsed, list):
            issues = parsed
        elif isinstance(parsed, dict):
            issues = parsed.get("issues") or []
        else:
            issues = []
        merged_issues.extend([i for i in issues if isinstance(i, dict)])

        # gather next token
        nt = None
        if isinstance(parsed, dict):
            nt = parsed.get("nextPageToken")
        if not nt and isinstance(raw_data, dict):
            nt = raw_data.get("nextPageToken")
        next_token = nt
        if not next_token:
            break

    output_payload: dict[str, Any] = {"issues": merged_issues}
    if next_token:
        output_payload["nextPageToken"] = next_token

    if raw_output_path:
        write_json(raw_output_path, raw_collected if len(raw_collected) > 1 else raw_collected[0])
        print(f"Raw payload saved to {raw_output_path}")

    if not args.no_output:
        write_json(output_path, output_payload)
        print(f"Parsed payload saved to {output_path}")

    _print_issues({"issues": merged_issues})


if __name__ == "__main__":
    main()
