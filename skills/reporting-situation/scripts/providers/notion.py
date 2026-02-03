from .base import run_mcpc, ProviderBase
import sys
import re
from datetime import datetime, timedelta, timezone

class NotionProvider(ProviderBase):
    def __init__(self):
        self.session = "@notion"
        self._user_cache = {} # email/name -> id
        self.name = "notion"
        self.id_prefix = "notion"

    def _resolve_user(self, email_or_name):
        if email_or_name in self._user_cache:
            return self._user_cache[email_or_name]

        resp = run_mcpc(self.session, "notion-get-users", {
            "query": email_or_name
        })
        
        results = []
        if isinstance(resp, dict):
            results = resp.get("results", [])
        elif isinstance(resp, list):
            results = resp
        
        for u in results:
            u_email = u.get("email")
            u_id = u.get("id")
            if u_email and u_email.lower() == email_or_name.lower():
                self._user_cache[email_or_name] = u_id
                return u_id
            if u.get("name") and u.get("name").lower() == email_or_name.lower():
                self._user_cache[email_or_name] = u_id
                return u_id

        if results:
            u_id = results[0].get("id")
            self._user_cache[email_or_name] = u_id
            return u_id
        
        return None

    def search_collab_activity(self, name_or_email, days=7):
        user_id = self._resolve_user(name_or_email)
        if not user_id:
            print(f"[WARN] Could not resolve Notion user '{name_or_email}', searching as text.", file=sys.stderr)
            return self._search(name_or_email, days=days)

        filters = {
            "created_by_user_ids": [user_id]
        }
        return self._search(" ", filters=filters, days=days)

    def search_topic_activity(self, keyword, days=7):
        return self._search(keyword, days=days)

    def search_team_activity(self, team_name, days=7):
        return self._search(team_name, days=days)

    def _search(self, query, filters=None, days=7):
        results = []
        args = {"query": query}
        if filters:
            args["filters"] = filters
            args["query_type"] = "internal"
            
        resp = run_mcpc(self.session, "notion-search", args)
        
        items = []
        if isinstance(resp, dict):
            items = resp.get("results", [])
        elif isinstance(resp, list):
            items = resp
            
        # Calculate cutoff time (UTC)
        cutoff_dt = datetime.now(timezone.utc) - timedelta(days=days)
        
        for item in items:
            if isinstance(item, str):
                continue

            obj_id = item.get("id")
            if not obj_id:
                continue
            
            # Client-side Date Filtering
            # Use 'timestamp' (ISO format) from Notion MCP search results
            ts_str = item.get("timestamp")
            if ts_str:
                try:
                    ts_str = ts_str.replace("Z", "+00:00")
                    ts_dt = datetime.fromisoformat(ts_str)
                    
                    if ts_dt < cutoff_dt:
                        continue # Skip old items
                except ValueError:
                    pass

            title = item.get("title", "Untitled")
            url = item.get("url")
            
            # If standard properties exist (fallback for other object types)
            props = item.get("properties", {})
            if title == "Untitled":
                if "title" in props:
                    t_block = props["title"].get("title", [])
                    if t_block:
                        title = t_block[0].get("plain_text", "Untitled")
                elif "Name" in props:
                    t_block = props["Name"].get("title", [])
                    if t_block:
                        title = t_block[0].get("plain_text", "Untitled")
            
            if not url:
                url = f"https://notion.so/{obj_id.replace('-', '')}"

            results.append({
                "id": self.build_id(obj_id),
                "provider": self.name,
                "type": item.get("object", "page"),
                "title": title,
                "url": url,
                "metadata": item
            })
        return results

    def get_content(self, page_id):
        real_id = self.parse_id(page_id)
        resp = run_mcpc(self.session, "notion-fetch", {"id": real_id})
        
        content_text = ""
        if isinstance(resp, dict):
            content_text = resp.get("text", "")
        elif isinstance(resp, str):
            content_text = resp
            
        if content_text:
            match = re.search(r'<content>(.*?)</content>', content_text, re.DOTALL)
            if match:
                return match.group(1).strip()
            return content_text.strip()
        
        return None

    def get_comments(self, page_id):
        real_id = self.parse_id(page_id)
        resp = run_mcpc(self.session, "notion-get-comments", {"page_id": real_id})
        
        results = []
        if isinstance(resp, dict):
            results = resp.get("results", [])
        elif isinstance(resp, list):
            results = resp
            
        comments = []
        for c in results:
            content_list = c.get("rich_text", [])
            text_content = ""
            if content_list:
                text_content = "".join([t.get("plain_text", "") for t in content_list])
                
            comments.append({
                "author": c.get("created_by", {}).get("name", "Unknown"),
                "content": text_content,
                "created": c.get("created_time"),
                "resolved": False
            })
        return comments

    def get_modified_time(self, metadata):
        if not metadata:
            return None
        return metadata.get("last_edited_time") or metadata.get("timestamp")
