#!/usr/bin/env python3
import json
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tracker import Tracker
from providers.google import GoogleProvider
from providers.notion import NotionProvider
from providers.jira import JiraProvider

def load_config(config_path):
    if not config_path:
        config_path = Path(__file__).parent.parent / "templates" / "config.json"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        print(f"[ERROR] Config not found: {config_path}")
        sys.exit(1)
        
    with open(config_path) as f:
        return json.load(f)

def restart_session(session_name):
    print(f"Restarting {session_name}...", end=" ", flush=True)
    try:
        # mcpc @session restart
        res = subprocess.run(["mcpc", session_name, "restart"], capture_output=True, text=True)
        if res.returncode == 0:
            print("OK")
            return True
        else:
            print("FAIL")
            print(f"[ERROR] Could not restart {session_name}: {res.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("FAIL (mcpc not found)")
        return False

def generate_simple_summary(text):
    if not text:
        return "No content found."
    text = text.replace("\n", " ").strip()
    preview = text[:300] + "..."
    return f"[AUTO-PREVIEW] {preview}"

def generate_discussion_summary(comments, target_emails=None):
    if not comments:
        return "No comments."
    
    authors = set(c['author'] for c in comments)
    summary = f"{len(comments)} comments by {', '.join(authors)}. Last update: {comments[-1]['created']}"
    
    if target_emails:
        highlights = []
        for c in comments:
            c_email = c.get("email", "")
            c_author = c.get("author", "")
            
            is_target = False
            if c_email and c_email in target_emails:
                is_target = True
            
            if is_target and c.get("content"):
                clean_content = c["content"].replace("\n", " ")[:150]
                highlights.append(f"  > {c_author}: \"{clean_content}\"")
        
        if highlights:
            # Show the most recent 3 comments from targets
            summary += "\n" + "\n".join(highlights[-3:]) 
            
    return summary

def process_item(unique_id, provider, tracker, item_tags, target_emails):
    print(f"Processing {unique_id}...", flush=True) 
    try:
        # Cleanup legacy attendance tags from cached summaries
        item = tracker.get_item(unique_id)
        current_summary = item.get("summary", "")
        if current_summary and "[Attendance:" in current_summary:
            import re
            new_summary = re.sub(r'\[Attendance:.*?\]\s*', '', current_summary)
            tracker.update_summary(unique_id, new_summary)

        # Only fetch content if we don't have a summary or it's stale
        # We ALWAYS fetch comments to check for target user activity
        
        content = None
        # Check if we should refresh content
        if tracker.should_refresh_content(unique_id):
                content = provider.get_content(unique_id)
                if content:
                    # Extract timestamp for folder organization
                    mod_time = None
                    if "raw_metadata" in item:
                        meta = item["raw_metadata"]
                        mod_time = meta.get("modifiedTime") or meta.get("last_edited_time")
                        if not mod_time and "fields" in meta:
                             mod_time = meta["fields"].get("updated")
                    
                    tracker.save_content(unique_id, content, mod_time)
                    
                    summary = generate_simple_summary(content)
                    tracker.update_summary(unique_id, summary)
                    tracker.touch_content_fetch(unique_id)
        
        if hasattr(provider, "get_comments"):
            # Always fetch comments to catch new activity from our targets
            comments = provider.get_comments(unique_id)
            if comments:
                disc_summary = generate_discussion_summary(comments, target_emails)
                tracker.update_discussion_summary(unique_id, disc_summary)
                tracker.touch_comment_fetch(unique_id)
    except Exception as e:
        print(f"  [ERROR] Failed to process {unique_id}: {e}")

def run_search_task(search_func, args, tag, lock, handle_results_callback):
    """Executes a search and safely handles results."""
    try:
        # print(f"DEBUG: Running search for {tag}...", flush=True)
        results = search_func(*args)
        if results:
            with lock:
                handle_results_callback(results, tag)
    except Exception as e:
        print(f"[ERROR] Search failed for {tag}: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to config.json")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    args = parser.parse_args()

    # 0. Fail-fast Session Check
    sessions = ["@google", "@notion", "@jira"]
    for s in sessions:
        if not restart_session(s):
            print("Aborting due to provider failure.")
            sys.exit(1)

    config = load_config(args.config)
    
    # Extract target emails for highlighting
    target_emails = set()
    for c in config.get("collaborators", []):
        if c.get("email"):
            target_emails.add(c["email"])
            
    tracker = Tracker()
    
    providers = {
        "google": GoogleProvider(),
        "notion": NotionProvider(),
        "jira": JiraProvider()
    }
    
    item_tags = {}
    items_to_process = [] 

    # 'items_to_process' is populated by 'handle_results' during the search sweep.

    def handle_results(results, tag):
        count = 0
        for res in results:
            is_new, item = tracker.update_item(res["id"], res["type"], res["title"], res["url"], res["metadata"])
            
            if res["id"] not in item_tags:
                item_tags[res["id"]] = set()
            item_tags[res["id"]].add(tag)
            
            prefix = res["id"].split(":")[0]
            if prefix in providers:
                # Dedupe in list
                item_tuple = (res["id"], providers[prefix])
                # Check if tuple is already in items_to_process
                if item_tuple not in items_to_process:
                     items_to_process.append(item_tuple)
                
                count += 1
        return count

    print("\n>>> Starting Situation Report Sweep (Parallel)...")
    
    search_tasks = []

    # 1. Collaborators
    for collab in config.get("collaborators", []):
        tag = f"Person: {collab.get('name')}"
        email = collab.get("email")
        handle = collab.get("handle")
        
        if email:
            search_tasks.append((providers["google"].search_collab_activity, (email, args.days), tag))
            search_tasks.append((providers["notion"].search_collab_activity, (email, args.days), tag))
        if handle:
            search_tasks.append((providers["jira"].search_collab_activity, (handle, args.days), tag))

    # 2. Topics
    for topic in config.get("topics", []):
        tag = f"Topic: {topic.get('name')}"
        keywords = topic.get("keywords", [])
        
        # Google and Notion: Loop per keyword
        for kw in keywords:
            search_tasks.append((providers["google"].search_topic_activity, (kw, args.days), tag))
            search_tasks.append((providers["notion"].search_topic_activity, (kw, args.days), tag))
            
        # Jira: Batch search
        if keywords:
            search_tasks.append((providers["jira"].search_topic_activity, (keywords, args.days), tag))

    # 3. Teams
    for team in config.get("teams", []):
        tag = f"Team: {team.get('name')}"
        search_tasks.append((providers["google"].search_team_activity, (team["name"], args.days), tag))
        search_tasks.append((providers["notion"].search_team_activity, (team["name"], args.days), tag))
        if team.get("jira_project"):
            search_tasks.append((providers["jira"].search_team_activity, (team["jira_project"], args.days), tag))

    # 4. Meeting Notes
    search_tasks.append((providers["google"].search_meeting_notes, (args.days,), "Meeting Notes"))

    # Execute Search Sweep in Parallel
    print(f"Queued {len(search_tasks)} search tasks. Executing...")
    
    sweep_lock = Lock()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for func, f_args, tag in search_tasks:
            futures.append(executor.submit(run_search_task, func, f_args, tag, sweep_lock, handle_results))
        
        completed_count = 0
        total_tasks = len(futures)
        for _ in as_completed(futures):
            completed_count += 1
            print(f"\rSearch Progress: {completed_count}/{total_tasks}...", end="", flush=True)
    
    print(f"\n>>> Sweep Complete. Found {len(items_to_process)} items to process/summarize.")
    
    # Process items in parallel
    print("Starting content processing (max_workers=10)...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for unique_id, provider in items_to_process:
            futures.append(executor.submit(
                process_item, 
                unique_id, 
                provider, 
                tracker, 
                item_tags, 
                target_emails
            ))
        
        for future in as_completed(futures):
            pass

    tracker.save()
    
    # 3. Assemble Corpus
    corpus_data = [] # List of (title, content_text, discussion_text)
    print("Building corpus...")
    
    # Expand window: if days=7, lookback 49 days for comments
    comment_lookback_days = args.days * 7
    cutoff = datetime.now(timezone.utc) - timedelta(days=comment_lookback_days)

    for unique_id, provider in items_to_process:
        item = tracker.get_item(unique_id)
        if not item: continue
        
        # 1. Content
        mod_time = None
        if "raw_metadata" in item:
            meta = item["raw_metadata"]
            mod_time = meta.get("modifiedTime") or meta.get("last_edited_time")
            if not mod_time and "fields" in meta:
                    mod_time = meta["fields"].get("updated")
        
        content_path = tracker.get_content_path(unique_id, mod_time)
        content_text = ""
        if content_path and content_path.exists():
            try:
                content_text = content_path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"[WARN] Could not read content for {unique_id}: {e}")

        # 2. Discussion
        discussion_text = ""
        if item.get("discussion_summary"):
             discussion_text = f"\n\n### Discussion Summary\n{item['discussion_summary']}\n"

        if content_text or discussion_text:
            corpus_data.append({
                "title": item.get("title", "Untitled"),
                "id": unique_id,
                "content": content_text,
                "discussion": discussion_text
            })

    # Write Corpus
    if corpus_data:
        corpus_out = Path("situation_corpus.md")
        print(f"Writing {len(corpus_data)} items to {corpus_out}...")
        with open(corpus_out, "w", encoding="utf-8") as outfile:
            outfile.write(f"# Situation Report Corpus - {datetime.now().isoformat()}\n")
            outfile.write(f"Scope: {args.days} days history.\n\n")
            
            for entry in corpus_data:
                outfile.write(f"\n\n--- DOCUMENT: {entry['title']} ({entry['id']}) ---\n\n")
                outfile.write(entry['content'])
                outfile.write(entry['discussion'])
                
        print(f"Corpus ready: {corpus_out.absolute()}")
    
    print("\n" + "="*60)
    print("SITUATION REPORT".center(60))
    print("="*60)
    
    # Group by Topic
    topics = [f"Topic: {t['name']}" for t in config.get("topics", [])]
    people = [f"Person: {p['name']}" for p in config.get("collaborators", [])]
    
    all_tags = topics + people + ["Meeting Notes"]
    
    for tag in all_tags:
        relevant_ids = [uid for uid, tags in item_tags.items() if tag in tags]
        if not relevant_ids:
            continue
            
        print(f"\n### [{tag}]")
        
        tag_items = []
        for uid in relevant_ids:
            it = tracker.get_item(uid)
            if it: tag_items.append(it)
        
        tag_items.sort(key=lambda x: x["last_seen"], reverse=True)
        
        for item in tag_items[:5]:
            title = item.get('title', 'Untitled')
            print(f"- {title}")
            if item.get("summary"):
                print(f"  Summary: {item['summary']}")
            if item.get("discussion_summary"):
                print(f"  Discussion: {item['discussion_summary']}")
            print(f"  Link: {item['url']}")
            print()

if __name__ == "__main__":
    main()
