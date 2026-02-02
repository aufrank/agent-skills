#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Paths relative to this script
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
OUTPUT_FILE = Path(__file__).parent.parent / "references" / "tool_cheat_sheet.md"

def load_tools(json_path):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            # Handle list or dict wrapper
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "tools" in data:
                return data["tools"]
            return []
    except Exception as e:
        print(f"[WARN] Could not parse {json_path}: {e}", file=sys.stderr)
        return []

def format_tool(session, tool):
    name = tool.get("name")
    desc = tool.get("description", "").replace("\n", " ")[:200] + "..."
    schema = tool.get("inputSchema", {})
    props = schema.get("properties", {})
    required = schema.get("required", [])
    
    lines = []
    lines.append(f"### `{name}`")
    lines.append(f"> {desc}")
    lines.append("")
    
    # Construct example call
    req_args = [f'{k}:="<val>"' for k in required]
    call_str = f"mcpc {session} tools-call {name} {' '.join(req_args)}"
    lines.append(f"```bash\n{call_str}\n```")
    
    if props:
        lines.append("**Arguments:**")
        for prop_name, prop_def in props.items():
            is_req = "**(Required)**" if prop_name in required else "(Optional)"
            p_type = prop_def.get("type", "any")
            p_desc = prop_def.get("description", "").replace("\n", " ")
            lines.append(f"- `{prop_name}` {is_req} `{p_type}`: {p_desc}")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)

def main():
    if not CACHE_DIR.exists():
        print(f"Cache directory not found at {CACHE_DIR}.")
        print("Please run 'scripts/verify_tools.py' first to populate the cache.")
        sys.exit(1)
        
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, "w") as out:
        out.write("# MCP Tool Cheat Sheet\n\n")
        out.write("Generated from cached tool definitions. Use these examples to call tools via `mcpc`.\n\n")
        
        # Look for json files
        files = sorted(CACHE_DIR.glob("*_tools.json"))
        if not files:
             print("No tool definitions found in cache. Run 'scripts/verify_tools.py'.")
             sys.exit(1)

        for json_file in files:
            # Infer session name from filename (e.g. google_tools.json -> @google)
            session_name = "@" + json_file.name.replace("_tools.json", "")
            out.write(f"## {session_name}\n\n")
            
            tools = load_tools(json_file)
            if not tools:
                out.write("*No tools found or parse error.*\n\n")
                continue
                
            for tool in tools:
                out.write(format_tool(session_name, tool))
    
    print(f"Generated reference at: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
