from datetime import datetime, timezone

from providers.google import GoogleProvider
from providers.notion import NotionProvider
from providers.jira import JiraProvider


def test_google_provider_includes_provider_field(monkeypatch):
    def fake_run_mcpc(session, tool, args):
        return {
            "files": [
                {
                    "id": "abc123",
                    "name": "Sample Doc",
                    "mimeType": "application/vnd.google-apps.document",
                    "webViewLink": "https://example.com/doc",
                    "modifiedTime": "2026-02-01T00:00:00Z",
                }
            ]
        }

    monkeypatch.setattr("providers.google.run_mcpc", fake_run_mcpc)
    provider = GoogleProvider()
    results = provider.search_topic_activity("ml", days=1)

    assert results
    assert results[0]["provider"] == "google"
    assert results[0]["id"].startswith("google:")


def test_notion_provider_filters_by_timestamp(monkeypatch):
    now = datetime.now(timezone.utc)
    recent = now.isoformat().replace("+00:00", "Z")

    def fake_run_mcpc(session, tool, args):
        return {
            "results": [
                {
                    "id": "page123",
                    "object": "page",
                    "title": "Recent",
                    "url": "https://notion.so/page123",
                    "timestamp": recent,
                }
            ]
        }

    monkeypatch.setattr("providers.notion.run_mcpc", fake_run_mcpc)
    provider = NotionProvider()
    results = provider.search_topic_activity("topic", days=7)

    assert results
    assert results[0]["provider"] == "notion"
    assert results[0]["id"].startswith("notion:")


def test_jira_provider_uses_cloud_id_from_config(monkeypatch):
    def fake_run_mcpc(session, tool, args):
        if tool == "searchJiraIssuesUsingJql":
            assert args["cloudId"] == "cloud-123"
            return {
                "issues": [
                    {
                        "key": "ABC-1",
                        "fields": {"summary": "Test", "updated": "2026-02-01T00:00:00Z"},
                    }
                ]
            }
        if tool == "getAccessibleAtlassianResources":
            return [{"id": "cloud-123"}]
        return None

    monkeypatch.setattr("providers.jira.run_mcpc", fake_run_mcpc)
    provider = JiraProvider(cloud_id="cloud-123", base_url="https://example.atlassian.net")
    results = provider.search_team_activity("ABC", days=3)

    assert results
    assert results[0]["provider"] == "jira"
    assert results[0]["url"].startswith("https://example.atlassian.net/browse/")
