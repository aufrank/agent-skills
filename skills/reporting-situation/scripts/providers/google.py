from .base import run_mcpc, ProviderBase
from datetime import datetime, timedelta, timezone

class GoogleProvider(ProviderBase):
    def __init__(self):
        self.session = "@google"
        self.name = "google"
        self.id_prefix = "google"

    def _get_date_filter(self, days):
        dt = datetime.now(timezone.utc) - timedelta(days=days)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    def search_collab_activity(self, email, days=7):
        date_str = self._get_date_filter(days)
        # Check for files modified OR created by the user, or where they are a writer
        # Note: Google Drive API query 'writers' check includes the owner.
        # We also check fullText for email mentions.
        query = (
            f"(modifiedTime > '{date_str}' or createdTime > '{date_str}') and "
            f"('{email}' in writers or fullText contains '{email}')"
        )
        return self._search_drive(query)

    def search_topic_activity(self, keyword, days=7):
        date_str = self._get_date_filter(days)
        # Escape single quotes in keyword
        safe_kw = keyword.replace("'", "\\'")
        query = f"(modifiedTime > '{date_str}' or createdTime > '{date_str}') and fullText contains '{safe_kw}'"
        return self._search_drive(query)

    def search_team_activity(self, team_name, days=7):
        date_str = self._get_date_filter(days)
        safe_team = team_name.replace("'", "\\'")
        query = f"(modifiedTime > '{date_str}' or createdTime > '{date_str}') and fullText contains '{safe_team}'"
        return self._search_drive(query)

    def search_meeting_notes(self, days=7):
        date_str = self._get_date_filter(days)
        query = f"(modifiedTime > '{date_str}' or createdTime > '{date_str}') and name contains 'Notes by Gemini'"
        return self._search_drive(query)

    def _search_drive(self, query):
        results = []
        # Explicitly order by modifiedTime desc to get freshest content
        resp = run_mcpc(self.session, "drive.search", {
            "query": query, 
            "pageSize": 10,
            "orderBy": "modifiedTime desc"
        })
        
        files = []
        if isinstance(resp, dict):
             files = resp.get("files", [])
        elif isinstance(resp, list):
             files = resp
            
        for f in files:
            mime = f.get("mimeType", "")
            if "google-apps" in mime or "pdf" in mime:
                url = f.get("webViewLink")
                if not url:
                    url = f"https://drive.google.com/open?id={f.get('id')}"
                
                results.append({
                    "id": self.build_id(f.get("id")),
                    "provider": self.name,
                    "type": mime,
                    "title": f.get("name"),
                    "url": url,
                    "metadata": f
                })
        return results

    def get_content(self, file_id, mime_type=None):
        real_id = self.parse_id(file_id)
        
        # Dispatch based on MIME type if known
        if mime_type:
            if "document" in mime_type:
                return self._get_doc_text(real_id)
            elif "presentation" in mime_type:
                return self._get_slides_text(real_id)
            elif "spreadsheet" in mime_type:
                return self._get_sheets_text(real_id)
        
        # Fallback: Try them in sequence (most likely first)
        text = self._get_doc_text(real_id)
        if text:
            return text
        
        text = self._get_slides_text(real_id)
        if text:
            return text
        
        text = self._get_sheets_text(real_id)
        if text:
            return text

        return None

    def _get_doc_text(self, real_id):
        resp = run_mcpc(self.session, "docs.getText", {"documentId": real_id, "format": "markdown"})
        if resp and isinstance(resp, str) and "error" not in resp:
            return resp
        return None

    def _get_slides_text(self, real_id):
        resp = run_mcpc(self.session, "slides.getText", {"presentationId": real_id})
        if resp and "error" not in str(resp):
            return str(resp)
        return None

    def _get_sheets_text(self, real_id):
        resp = run_mcpc(self.session, "sheets.getText", {"spreadsheetId": real_id})
        if resp and "error" not in str(resp):
            return str(resp)
        return None

    def get_comments(self, file_id):
        real_id = self.parse_id(file_id)
        
        # Try all 3 comment tools
        resp = run_mcpc(self.session, "docs.listComments", {"documentId": real_id})
        if not resp or "error" in str(resp):
             resp = run_mcpc(self.session, "slides.listComments", {"presentationId": real_id})
        if not resp or "error" in str(resp):
             resp = run_mcpc(self.session, "sheets.listComments", {"spreadsheetId": real_id})

        if not resp or "error" in str(resp):
             return []
        
        comments = []
        raw_comments = resp if isinstance(resp, list) else resp.get("comments", [])
        for c in raw_comments:
             comments.append({
                 "author": c.get("author", {}).get("displayName", "Unknown"),
                 "email": c.get("author", {}).get("emailAddress"),
                 "content": c.get("content"),
                 "created": c.get("createdTime"),
                 "resolved": c.get("resolved", False)
             })
        return comments

    def get_modified_time(self, metadata):
        if not metadata:
            return None
        return metadata.get("modifiedTime") or metadata.get("createdTime")
