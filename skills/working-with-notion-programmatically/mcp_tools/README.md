## MCP tool cache
Use this directory to store `mcpc --json tools-get` outputs for the specific Notion tools you need. Keep files small and only fetch what you use.

Example (PowerShell):
```powershell
mcpc --json '@notion' tools-get notion-search | Out-File -Encoding utf8 mcp_tools/notion-search.json
mcpc --json '@notion' tools-get notion-fetch | Out-File -Encoding utf8 mcp_tools/notion-fetch.json
```
Then read only the needed fields (e.g., arguments) instead of pasting full schemas into chat.
