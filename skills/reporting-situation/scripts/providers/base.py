import subprocess
import json
import sys
import re
import tempfile
import os

def run_mcpc(session, tool, args):
    cmd = ["mcpc", "--json", session, "tools-call", tool]
    for k, v in args.items():
        if isinstance(v, (dict, list, bool, int, float)):
             val = json.dumps(v)
        else:
             val = str(v)
        cmd.append(f"{k}:={val}")
    
    # Create a temp file to capture output, avoiding pipe buffer limits
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp_out:
        tmp_path = tmp_out.name
        
    try:
        # Redirect stdout to file, allow stderr to flow or capture if needed
        # We capture stderr to print it on error
        with open(tmp_path, 'w') as f_out:
            result = subprocess.run(cmd, stdout=f_out, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            
        if result.returncode != 0:
            print(f"[WARN] {session} {tool} error: {result.stderr.strip()}", file=sys.stderr)
            return None
            
        # Read back from file
        with open(tmp_path, 'r', encoding='utf-8') as f_in:
            output = f_in.read().strip()
            
        # Robustness: Find start of JSON
        match = re.search(r'(\[|\{)', output)
        if match:
            output = output[match.start():]
        
        if not output:
            return None

        try:
            data = json.loads(output)
            
            # 1. Check for 'structuredContent' (some tools)
            if isinstance(data, dict) and "structuredContent" in data:
                return data["structuredContent"]

            # 2. Check for 'structuredData' (some versions)
            if isinstance(data, dict) and "structuredData" in data:
                return data["structuredData"]
            
            # 3. Check for 'content' blocks (standard MCP)
            if isinstance(data, dict) and "content" in data and isinstance(data["content"], list):
                if len(data["content"]) == 1 and data["content"][0].get("type") == "text":
                    text_content = data["content"][0]["text"]
                    try:
                        inner = json.loads(text_content)
                        return inner
                    except json.JSONDecodeError:
                        return text_content
                return data["content"]
            
            return data
            
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse JSON from {session} {tool}", file=sys.stderr)
            # print(f"RAW START: {output[:200]}...", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"[ERROR] Exception {session} {tool}: {e}", file=sys.stderr)
        return None
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
