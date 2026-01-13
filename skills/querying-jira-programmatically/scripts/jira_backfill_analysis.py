#!/usr/bin/env python3
"""
Fetch backfill/backlog items via JQL and emit a small analysis (counts by status/type/priority).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

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
    write_text,
)


def build_jql(args: argparse.Namespace) -> str:
    if args.jql:
        return args.jql
    if not args.project:
        sys.stderr.write("Provide --project or --jql\n")
        sys.exit(1)
    clauses = [f"project = {args.project}"]
    if args.label:
        clauses.append(f'labels = "{args.label}"')
    else:
        clauses.append('text ~ "backfill"')
    if not args.include_done:
        clauses.append("statusCategory != Done")
    return " AND ".join(clauses)


def analyze(issues: List[Dict[str, Any]]) -> str:
    status_ct = Counter()
    type_ct = Counter()
    priority_ct = Counter()
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        fields = issue.get("fields", {}) if isinstance(issue.get("fields"), dict) else {}
        status = fields.get("status", {}).get("name", "") if isinstance(fields.get("status"), dict) else ""
        itype = fields.get("issuetype", {}).get("name", "") if isinstance(fields.get("issuetype"), dict) else ""
        priority = fields.get("priority", {}).get("name", "") if isinstance(fields.get("priority"), dict) else ""
        status_ct[status] += 1
        type_ct[itype] += 1
        priority_ct[priority] += 1

    lines: List[str] = []
    lines.append(f"Issues analyzed: {len(issues)}")
    lines.append("By status:")
    for k, v in status_ct.most_common():
        lines.append(f"  - {k or '(none)'}: {v}")
    lines.append("By type:")
    for k, v in type_ct.most_common():
        lines.append(f"  - {k or '(none)'}: {v}")
    lines.append("By priority:")
    for k, v in priority_ct.most_common():
        lines.append(f"  - {k or '(none)'}: {v}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch backfill/backlog issues and summarize patterns.")
    parser.add_argument("--project", help="Project key (e.g., MLPLAT). Required unless --jql provided.")
    parser.add_argument("--jql", help="Custom JQL override.")
    parser.add_argument("--label", help='Label to filter (defaults to searching text for "backfill").')
    parser.add_argument("--include-done", action="store_true", help="Include Done issues.")
    parser.add_argument("--cloud-id", default=DEFAULT_CLOUD_ID, help="Jira cloudId (default: ae3605cc-2ea8-41ef-86e8-c7cda3a94bc0).")
    parser.add_argument("--max-results", type=int, default=100, help="Max results (default 100).")
    parser.add_argument("--session", default="@jira", help="mcpc session or server URL. Quote @jira in PowerShell.")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="mcpc profile.")
    parser.add_argument("--server", default=DEFAULT_SERVER, help="Jira MCP server.")
    parser.add_argument("--output", default=None, help="Path to write parsed payload (default results/jira.backfill.json).")
    parser.add_argument("--raw-output", default=None, help="Optional path to write raw mcpc response.")
    parser.add_argument("--summary-output", default=None, help="Path to write analysis summary (default results/jira.backfill.summary.txt).")
    parser.add_argument("--no-output", action="store_true", help="Skip writing parsed payload.")
    parser.add_argument("--no-summary", action="store_true", help="Skip writing summary file.")
    parser.add_argument("--timestamp-output", action="store_true", help="Append UTC timestamp to output/summary filenames.")
    args = parser.parse_args()

    ensure_auth(args.server, args.profile, args.session)
    mcpc_cmd = get_mcpc_cmd()
    roots = skill_cache_roots()
    output_path = Path(args.output) if args.output else roots["results_root"] / "jira.backfill.json"
    summary_path = Path(args.summary_output) if args.summary_output else roots["results_root"] / "jira.backfill.summary.txt"
    raw_output_path = Path(args.raw_output) if args.raw_output else None
    output_path = timestamped_path(output_path, args.timestamp_output)
    summary_path = timestamped_path(summary_path, args.timestamp_output)
    if raw_output_path:
        raw_output_path = timestamped_path(raw_output_path, args.timestamp_output)
    for path in [output_path, summary_path, raw_output_path]:
        if path and path.parent:
            path.parent.mkdir(parents=True, exist_ok=True)

    jql = build_jql(args)
    cmd = [
        *mcpc_cmd,
        "--json",
        "--profile",
        args.profile,
        args.session,
        "tools-call",
        "searchJiraIssuesUsingJql",
        f"cloudId:={args.cloud_id}",
        f"jql:={jql}",
        f"maxResults:={args.max_results}",
    ]
    print("Executing:", " ".join(cmd))
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        sys.stderr.write(f"mcpc exited with status {completed.returncode}\n")
        sys.stderr.write(completed.stderr)
        sys.exit(completed.returncode)

    try:
        raw_data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to parse mcpc JSON output: {exc}\n")
        sys.exit(1)

    if raw_output_path:
        write_json(raw_output_path, raw_data)
        print(f"Raw payload saved to {raw_output_path}")

    parsed = parse_mcpc_payload(raw_data)
    if isinstance(parsed, list):
        issues = parsed
    elif isinstance(parsed, dict):
        issues = parsed.get("issues") or []
    else:
        issues = []

    if not args.no_output:
        write_json(output_path, parsed)
        print(f"Parsed payload saved to {output_path}")

    summary_text = analyze(issues)
    print(summary_text)
    if not args.no_summary:
        write_text(summary_path, summary_text)
        print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
