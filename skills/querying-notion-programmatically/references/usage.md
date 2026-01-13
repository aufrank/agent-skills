# Querying Notion Programmatically - quick use

- **Search**:  
  `python scripts/notion_query.py --query "design system" --pretty`  
  Outputs `results/query.search.json`; use `--ids-only` for compact ID list.

- **Comments**:  
  `python scripts/notion_comments.py --page-id <page-id-or-url>`  
  Outputs `results/comments.json` and prints concise lines.

- **Any tool with caching**:  
  `python scripts/notion_call_tool.py --tool notion-search --arg query:="AI" --arg query_type:=internal --refresh-cache`  
  Caches `mcp_tools/tools-list.json` and `mcp_tools/notion-search.json`, writes output to `results/notion-search.json`.

- **Auth**: Scripts fail fast if `mcpc` login is missing. User must run:  
  `mcpc https://mcp.notion.com/mcp login --profile <name>`
- **WSL keyring tip**: reuse Windows mcpc by exporting  
  `MCPC_BIN="C:\\Users\\<user>\\AppData\\Roaming\\npm\\mcpc.cmd"` (uses cmd.exe bridge). Set `POWERSHELL_EXE` if you prefer a specific PowerShell.

- **Outputs**: Keep payloads on disk; cite file paths instead of pasting JSON into chat. Reuse existing `results/` before re-running.

- **Next step**: Add filters/date/creator handling in a follow-up iteration.
