import json
from pathlib import Path
from datetime import datetime, timezone

class Tracker:
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Default to a 'data' folder in the skill directory
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.tracker_file = self.data_dir / "tracker.json"
        self.data = self._load()

    def _load(self):
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._default_structure()
        return self._default_structure()

    def _default_structure(self):
        return {
            "items": {},  # unique_id -> metadata
            "mappings": {}, # entity_key -> { "service": "...", "resource_id": "..." }
            "last_run": None
        }

    def save(self):
        self.data["last_run"] = datetime.now(timezone.utc).isoformat()
        with open(self.tracker_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_item(self, unique_id):
        return self.data["items"].get(unique_id)

    def get_mapping(self, category, name):
        """
        Retrieves a cached mapping for an entity.
        e.g. category="team", name="Core Platform" -> returns {"jira_project": "PLAT"}
        """
        key = f"{category}:{name}"
        return self.data["mappings"].get(key)

    def set_mapping(self, category, name, mapping_data):
        """
        Caches a mapping.
        """
        key = f"{category}:{name}"
        self.data["mappings"][key] = mapping_data

    def update_item(self, unique_id, item_type, title, url, metadata=None):
        """
        Updates an item or creates it. Returns (is_new, item_dict).
        """
        now = datetime.now(timezone.utc).isoformat()
        is_new = False
        
        if unique_id not in self.data["items"]:
            is_new = True
            self.data["items"][unique_id] = {
                "type": item_type,
                "first_seen": now,
                "discovery_count": 0,
                "summary": None,
                "summary_updated": None,
                "discussion_summary": None,
                "discussion_updated": None,
                "last_content_fetch": None,
                "last_comment_fetch": None
            }
        
        item = self.data["items"][unique_id]
        item["title"] = title
        item["url"] = url
        item["last_seen"] = now
        item["discovery_count"] += 1
        
        if metadata:
            item["raw_metadata"] = metadata
            
        return is_new, item

    def update_summary(self, unique_id, summary_text):
        if unique_id in self.data["items"]:
            self.data["items"][unique_id]["summary"] = summary_text
            self.data["items"][unique_id]["summary_updated"] = datetime.now(timezone.utc).isoformat()

    def update_discussion_summary(self, unique_id, summary_text):
        if unique_id in self.data["items"]:
            self.data["items"][unique_id]["discussion_summary"] = summary_text
            self.data["items"][unique_id]["discussion_updated"] = datetime.now(timezone.utc).isoformat()
            
    def touch_content_fetch(self, unique_id):
        if unique_id in self.data["items"]:
            self.data["items"][unique_id]["last_content_fetch"] = datetime.now(timezone.utc).isoformat()

    def touch_comment_fetch(self, unique_id):
        if unique_id in self.data["items"]:
            self.data["items"][unique_id]["last_comment_fetch"] = datetime.now(timezone.utc).isoformat()

    def get_content_path(self, unique_id, timestamp=None):
        """
        Returns the path where content should be stored.
        Organizes by Week: data/content/2026-W05/google_123.md
        """
        if not timestamp:
            timestamp = datetime.now(timezone.utc)
        elif isinstance(timestamp, str):
            try:
                # Handle ISO format with potential timezone info
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.now(timezone.utc)
                
        # Get ISO calendar year and week
        iso_year, iso_week, _ = timestamp.isocalendar()
        week_str = f"{iso_year}-W{iso_week:02d}"
        
        safe_id = unique_id.replace(":", "_").replace("/", "_")
        folder = self.data_dir / "content" / week_str
        folder.mkdir(parents=True, exist_ok=True)
        
        return folder / f"{safe_id}.md"

    def save_content(self, unique_id, content, timestamp=None):
        path = self.get_content_path(unique_id, timestamp)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(path)

    def is_stale(self, unique_id, remote_modified_str):
        """
        Returns True if we should re-fetch content.
        Compares remote modification time (if available) with local fetch time.
        """
        item = self.get_item(unique_id)
        if not item:
            return True
            
        last_fetch_str = item.get("last_content_fetch")
        if not last_fetch_str:
            return True
            
        # If remote modification time is known
        if remote_modified_str:
            try:
                # 1. Parse Remote Time (Always treat as aware or assume UTC if Z is present)
                remote_dt = datetime.fromisoformat(remote_modified_str.replace("Z", "+00:00"))
                
                # 2. Parse Local Last-Fetch Time
                fetch_dt = datetime.fromisoformat(last_fetch_str)
                
                # 3. Normalize Timezones
                # If either is naive, we must standardize.
                # Logic: If remote is aware and fetch is naive, assume fetch was UTC (standard practice).
                # If remote is naive, treat it as UTC for safety.
                
                if remote_dt.tzinfo is None:
                    remote_dt = remote_dt.replace(tzinfo=timezone.utc)
                    
                if fetch_dt.tzinfo is None:
                    fetch_dt = fetch_dt.replace(tzinfo=timezone.utc)

                if remote_dt > fetch_dt:
                    return True
            except ValueError:
                pass # Fallback to time-based check if parsing fails
        
        # Default: Refresh if older than 24h
        return self.should_refresh_content(unique_id, hours=24)

    def should_refresh_content(self, unique_id, hours=24):
        item = self.get_item(unique_id)
        if not item:
            return True
        last_fetch_str = item.get("last_content_fetch")
        if not last_fetch_str:
            return True
        
        # Calculate diff
        try:
            last_dt = datetime.fromisoformat(last_fetch_str)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
                
            now_dt = datetime.now(timezone.utc)
            diff = now_dt - last_dt
            return (diff.total_seconds() / 3600) > hours
        except ValueError:
            return True
