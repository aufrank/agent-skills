## Notion mcpc references (minimal)
- Sessions: default `'@notion'` (quote in PowerShell). Fallback: `mcpc https://mcp.notion.com/mcp ...`.
- Common tool names: `notion-search`, `notion-fetch`, `notion-get-comments`, `notion-create-comment`, `notion-create-page`, `notion-update-page`, `resources-list/read`, `prompts-list/get`.
- Search filters (JSON): `{"created_by_user_ids":["<uuid>"],"created_date_range":{"start_date":"YYYY-MM-DD","end_date":"YYYY-MM-DD"}}`.
- Scope search: `page_url:=<page or id>`, `data_source_url:=collection://...`, `teamspace_id:=<uuid>`, `content_search_mode:=workspace_search|ai_search`.
- Caching schemas: run `mcpc --json '@notion' tools-get <tool> | Out-File mcp_tools/<tool>.json`.
