#!/usr/bin/env python3
import sys
from pathlib import Path
import argparse
import json

from config import load_config
from providers.base import run_mcpc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--interests", help="Deprecated: Path to interests.json")
    args = parser.parse_args()

    config = {}
    if args.interests:
        print("[WARN] --interests is deprecated. Use templates/config.json instead.", file=sys.stderr)
        interests_path = Path(args.interests)
        if interests_path.exists():
            with open(interests_path) as f:
                config = json.load(f)
        else:
            print(f"Config file not found: {interests_path}", file=sys.stderr)
    else:
        try:
            config = load_config(args.config)
        except FileNotFoundError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            config = {}
    
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
    if not keywords and config.get("topics"):
        keywords = [kw for t in config.get("topics", []) for kw in t.get("keywords", [])]
    if keywords:
        print(f"Searching Notion for {keywords[0] if keywords else '...'}...", file=sys.stderr)
        # We only search for the first keyword to avoid spamming in this MVP
        if len(keywords) > 0:
            kw = keywords[0]
            notion_results = run_mcpc("@notion", "notion-search", {"query": kw})
            if notion_results:
                 report_data["notion"] = notion_results

    # 4. Jira
    projects = config.get("jira_projects", [])
    if not projects and config.get("teams"):
        projects = [t.get("jira_project") for t in config.get("teams", []) if t.get("jira_project")]
    if projects:
        jira_cloud_id = (
            config.get("providers", {})
            .get("jira", {})
            .get("cloud_id")
        )
        if not jira_cloud_id:
            resources = run_mcpc("@jira", "getAccessibleAtlassianResources", {})
            if isinstance(resources, list) and resources:
                jira_cloud_id = resources[0].get("id")

        # Construct JQL
        jql = f"project in ({','.join(projects)}) AND status not in (Closed, Done) ORDER BY updated DESC"
        print(f"Searching Jira: {jql}...", file=sys.stderr)
        jira_args = {"jql": jql}
        if jira_cloud_id:
            jira_args["cloudId"] = jira_cloud_id
        jira_results = run_mcpc("@jira", "searchJiraIssuesUsingJql", jira_args)
        if jira_results:
             report_data["jira"] = jira_results

    # Output aggregated data
    print(json.dumps(report_data, indent=2))

if __name__ == "__main__":
    main()
