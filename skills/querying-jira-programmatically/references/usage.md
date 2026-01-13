# Querying Jira Programmatically - quick use

- **Rovo search**:  
  `python scripts/jira_search.py --query "incident backlog"`  
  Output: `results/jira.search.json`

- **JQL search** (cloudId auto-defaults to riotgames instance):  
  `python scripts/jira_search_jql.py --jql "project = ABC ORDER BY updated DESC" --max-results 25 --output results/jira.jql.json --raw-output results/jira.jql.raw.json`  
  Parses `content[0].text` when present; overwrite-by-default. Use `--no-output` to skip writing parsed output.

- **Any tool with caching**:  
  `python scripts/jira_call_tool.py --tool search --arg query:="AI" --refresh-cache`  
  Caches tools-list + schema to `.mcpc-skill-caches/querying-jira-programmatically/mcp_tools/`, output to `results/search.json`.

- **Auth**: Scripts fail fast if `mcpc` login is missing. User must run:  
  `mcpc https://mcp.atlassian.com/v1/mcp login --profile <name>`
- **WSL keyring tip**: reuse Windows mcpc by exporting  
  `MCPC_BIN="C:\\Users\\<user>\\AppData\\Roaming\\npm\\mcpc.cmd"` (cmd.exe bridge). Set `POWERSHELL_EXE` if you prefer a specific PowerShell.

- **Caches**: runtime-only; live under `.mcpc-skill-caches/querying-jira-programmatically/mcp_tools/`. Safe to delete/regenerate; keep out of git.

- **Team workload**:  
  `python scripts/jira_team_workload.py --project MLPLAT --team mlplat-engineering --output results/jira.team_workload.json --summary-output results/jira.team_workload.txt`

- **Unassigned open issues**:  
  `python scripts/jira_unassigned.py --project MLPLAT --output results/jira.unassigned.json`

- **Backfill/backlog analysis**:  
  `python scripts/jira_backfill_analysis.py --project MLPLAT --label backfill --output results/jira.backfill.json --summary-output results/jira.backfill.summary.txt`
