from .base import run_mcpc
import sys

class JiraProvider:
    def __init__(self):
        self.session = "@jira"
        self.search_tool = "searchJiraIssuesUsingJql"
        self.cloud_id = "ae3605cc-2ea8-41ef-86e8-c7cda3a94bc0"
        self._user_cache = {} 

    def _ensure_cloud_id(self):
        if self.cloud_id:
            return True
        resources = run_mcpc(self.session, "getAccessibleAtlassianResources", {})
        if resources and isinstance(resources, list) and len(resources) > 0:
            self.cloud_id = resources[0].get("id")
            return True
        return False

    def _resolve_user(self, search_string):
        if search_string in self._user_cache:
            return self._user_cache[search_string]
        
        if not self._ensure_cloud_id():
            return None
            
        query = search_string.lstrip("@")
        users = run_mcpc(self.session, "lookupJiraAccountId", {
            "cloudId": self.cloud_id, 
            "searchString": query
        })
        
        if users and isinstance(users, list) and len(users) > 0:
            account_id = users[0].get("accountId")
            self._user_cache[search_string] = account_id
            return account_id
        
        return None

    def search_collab_activity(self, handle, days=7):
        account_id = self._resolve_user(handle)
        if not account_id:
            return []
            
        # Escape handle for text search security
        safe_handle = handle.replace('"', '\\"')
            
        jql = (
            f'updated >= -{days}d AND ('
            f'assignee = "{account_id}" OR '
            f'reporter = "{account_id}" OR '
            f'issuekey IN updatedBy("{account_id}", "-{days}d") OR '
            f'lastCommentBy = "{account_id}" OR '
            f'text ~ "{safe_handle}"'
            f') ORDER BY updated DESC'
        )
        return self._search(jql)

    def search_topic_activity(self, keywords, days=7):
        if isinstance(keywords, str):
            keywords = [keywords]
            
        if not keywords:
            return []
            
        # Escape single quotes in keywords to prevent JQL errors
        safe_keywords = [k.replace("'", "\\'") for k in keywords]
        
        # Construct OR clause: text ~ "k1" OR text ~ "k2"
        clauses = [f"text ~ '{k}'" for k in safe_keywords]
        joined_clauses = " OR ".join(clauses)
        
        jql = f"updated >= -{days}d AND ({joined_clauses}) ORDER BY updated DESC"
        return self._search(jql)

    def search_team_activity(self, project_key, days=7):
        jql = f"updated >= -{days}d AND project = '{project_key}' ORDER BY updated DESC"
        return self._search(jql)

    def _search(self, jql):
        if not self._ensure_cloud_id():
            return []
            
        results = []
        # Use maxResults=10 to avoid buffer overflow on large JSON responses
        resp = run_mcpc(self.session, self.search_tool, {
            "cloudId": self.cloud_id,
            "jql": jql,
            "maxResults": 10
        })
        
        issues = []
        if isinstance(resp, dict):
            issues = resp.get("issues", [])
        elif isinstance(resp, list):
            issues = resp
        
        for i in issues:
            key = i.get('key')
            summary = i.get('fields', {}).get('summary', 'No Summary')
            results.append({
                "id": f"jira:{key}",
                "type": "issue",
                "title": f"{key}: {summary}",
                "url": f"https://riotgames.atlassian.net/browse/{key}",
                "metadata": i
            })
        return results

    def get_content(self, issue_id):
        if not self._ensure_cloud_id():
            return None
        real_id = issue_id.split(":", 1)[1]
        resp = run_mcpc(self.session, "getJiraIssue", {
            "cloudId": self.cloud_id,
            "issueIdOrKey": real_id
        })
        if resp and "fields" in resp:
            desc = resp["fields"].get("description", "")
            return str(desc)
        return None

    def get_comments(self, issue_id):
        if not self._ensure_cloud_id():
            return []
        real_id = issue_id.split(":", 1)[1]
        resp = run_mcpc(self.session, "getJiraIssue", {
            "cloudId": self.cloud_id,
            "issueIdOrKey": real_id
        })
        comments = []
        if resp and "fields" in resp:
             c_block = resp["fields"].get("comment", {})
             raw_comments = c_block.get("comments", [])
             for c in raw_comments:
                 comments.append({
                     "author": c.get("author", {}).get("displayName", "Unknown"),
                     "content": c.get("body"),
                     "created": c.get("created"),
                     "resolved": False 
                 })
        return comments
