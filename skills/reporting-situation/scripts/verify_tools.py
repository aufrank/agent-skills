#!/usr/bin/env python3
"""
Utility to verify tool availability and names for the Situation Report skill.
Run this to confirm that @jira and @notion expose the tools we expect.
"""
import subprocess
import json
import re
from pathlib import Path

EXPECTED_TOOLS = {
    "@jira": ["searchJiraIssuesUsingJql", "getJiraIssue"], 
    "@notion": ["notion-search", "notion-fetch"],
    "@google": ["drive.search", "docs.getText", "calendar.listEvents", "gmail.search"]
}

CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"

def check_server(session, expected_tools):
    print(f"Checking {session}...")
    
    clean_session = session.replace("@", "")
    cache_file = CACHE_DIR / f"{clean_session}_tools.json"
    
    # Ensure cache dir exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Stream output to file (Safe buffering)
    # We use --json to try and get structured data, but we stream it to disk.
    cmd_json = ["mcpc", "--json", session, "tools-list"]
    
    with open(cache_file, "w") as f:
        # Popen allows us to pipe stdout directly to the file handle
        process = subprocess.Popen(cmd_json, stdout=f, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"  [X] Failed to retrieve tools (Exit {process.returncode}): {stderr.strip().splitlines()[0] if stderr else 'Unknown error'}")
        return False

    # 2. Read and Parse Cache
    available_tools = set()
    json_success = False
    
    try:
        with open(cache_file, "r") as f:
            # We read the file content. If it's huge, json.load can still handle it better than subprocess pipe buffer.
            # If it's truly massive (GBs), we'd need streaming JSON parser, but for tool lists (MBs) it's fine.
            content = f.read()
            
            # Robustness: Find start of JSON container
            match = re.search(r'^\s*(\[|\{{)', content, re.MULTILINE)
            if match:
                json_str = content[match.start():]
                tools_data = json.loads(json_str)
                
                if isinstance(tools_data, list):
                    available_tools = {t.get("name") for t in tools_data}
                    json_success = True
                elif isinstance(tools_data, dict) and "tools" in tools_data:
                    available_tools = {t.get("name") for t in tools_data["tools"]}
                    json_success = True
            else:
                 # Fallback: raw text saved despite --json flag.
                 pass
                 
    except Exception:
        # JSON parsing failed
        pass

    # 3. Fallback: Text approach (Robustness for large schemas or bad JSON)
    if not json_success:
        # Fallback: attempt to read valid tools from raw text output if JSON parsing failed.
        # Let's try reading the *existing* file as text first if it failed JSON parse
        try:
            with open(cache_file, "r") as f:
                for line in f:
                    # Look for lines starting with "* `toolname`" in typical text output
                    # Attempt to extract tools from error text or non-JSON output.
                    pass
        except Exception:
            pass
            
        # Retry with text mode if JSON mode failed hard (empty file or garbage)
        txt_cache_file = CACHE_DIR / f"{clean_session}_tools.txt"
        cmd_text = ["mcpc", session, "tools-list"]
        with open(txt_cache_file, "w") as f:
             process = subprocess.Popen(cmd_text, stdout=f, stderr=subprocess.PIPE, text=True)
             _, stderr = process.communicate()
        
        if process.returncode == 0:
             with open(txt_cache_file, "r") as f:
                for line in f:
                    m = re.search(r'\*\s*`([^`]+)`', line)
                    if m:
                        available_tools.add(m.group(1))

    # 4. Validation
    if not available_tools:
        print(f"  [X] Failed to parse tool list from {session}.")
        return False

    all_good = True
    for tool in expected_tools:
        if tool in available_tools:
            print(f"  [✓] Found tool: {tool}")
        else:
            print(f"  [!] MISSING tool: {tool}")
            matches = [t for t in available_tools if tool.lower() in t.lower() or tool.split('.')[-1].lower() in t.lower()]
            if matches:
                print(f"      Did you mean? {', '.join(matches)}")
            else:
                print(f"      Available tools sample: {', '.join(list(available_tools)[:5])}...")
            all_good = False
    return all_good

def main():
    print("Verifying MCP Tool Interfaces...\n")
    print(f"Caching definitions to: {CACHE_DIR}\n")
    
    results = {}
    for session, tools in EXPECTED_TOOLS.items():
        results[session] = check_server(session, tools)
        print("-" * 40)

    if all(results.values()):
        print("\nAll systems go! The skill is ready to run.")
    else:
        print("\n[WARNING] Some tools were missing or servers unreachable.")
        print("Please update the provider scripts in 'scripts/providers/' if tool names differ.")

if __name__ == "__main__":
    main()
