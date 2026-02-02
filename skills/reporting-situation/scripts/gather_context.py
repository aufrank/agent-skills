#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

def run_mcpc(session, tool, args):
    """
    Runs a tool via 'mcpc' CLI.
    """
    cmd = ["mcpc", session, "tools-call", tool]
    for k, v in args.items():
        if isinstance(v, (dict, list, bool, int, float)):
             val = json.dumps(v)
        else:
             val = str(v)
        cmd.append(f"{k}:={val}")
    
    try:
        # We don't use check=True immediately to handle errors gracefully
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[WARN] Failed call to {session} {tool}: {result.stderr.strip()}", file=sys.stderr)
            return None
        return json.loads(result.stdout)
    except Exception as e:
        print(f"[ERROR] Exception calling {session} {tool}: {e}", file=sys.stderr)
        return None

def main():
    # Load config
    # Default location relative to script: ../templates/interests.json
    base_dir = Path(__file__).parent.parent
    config_path = base_dir / "templates" / "interests.json"
    
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    
    if not config_path.exists():
        print(f"Config file not found: {config_path}", file=sys.stderr)
        # Fallback to empty config to allow partial runs
        config = {}
    else:
        with open(config_path) as f:
            config = json.load(f)
    
    report_data = {}

    # 1. Google Calendar
    if config.get("google_calendar", True):
        print("Fetching Calendar events...", file=sys.stderr)
        # Using @google-workspace as a likely session name if @google isn't found, 
        # but sticking to user request of "google". I'll try @google.
        events = run_mcpc("@google", "calendar.listEvents", {"calendarId": "primary"})
        if events:
            report_data["calendar"] = events

    # 2. Gmail
    q = config.get("google_gmail_query", "is:unread")
    if q:
        print(f"Searching Gmail: {q}...", file=sys.stderr)
        emails = run_mcpc("@google", "gmail.search", {"query": q, "maxResults": 5})
        if emails:
            report_data["gmail"] = emails

    # 3. Notion
    keywords = config.get("keywords", [])
    if keywords:
        print(f"Searching Notion for {keywords[0] if keywords else '...'}...", file=sys.stderr)
        # We only search for the first keyword to avoid spamming in this MVP
        if len(keywords) > 0:
            kw = keywords[0]
            # Assuming standard notion server has a 'search' tool
            notion_results = run_mcpc("@notion", "search", {"query": kw})
            if notion_results:
                 report_data["notion"] = notion_results

    # 4. Jira
    projects = config.get("jira_projects", [])
    if projects:
        # Construct JQL
        jql = f"project in ({','.join(projects)}) AND status not in (Closed, Done) ORDER BY updated DESC"
        print(f"Searching Jira: {jql}...", file=sys.stderr)
        # tool name usually 'search' or 'jql'
        jira_results = run_mcpc("@jira", "search", {"jql": jql})
        if jira_results:
             report_data["jira"] = jira_results

    # Output aggregated data
    print(json.dumps(report_data, indent=2))

if __name__ == "__main__":
    main()
