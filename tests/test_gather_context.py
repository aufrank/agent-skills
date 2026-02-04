import json

import gather_context


def test_gather_context_skips_jira_without_cloud_id(monkeypatch, capsys):
    calls = []

    def fake_run_mcpc(session, tool, args):
        calls.append((session, tool, args))
        if tool == "getAccessibleAtlassianResources":
            return []
        return None

    monkeypatch.setattr(gather_context, "run_mcpc", fake_run_mcpc)
    monkeypatch.setattr(
        gather_context,
        "load_config",
        lambda _: {
            "google_calendar": False,
            "google_gmail_query": "",
            "jira_projects": ["ABC"],
        },
    )

    monkeypatch.setattr("sys.argv", ["gather_context"])
    gather_context.main()
    captured = capsys.readouterr()

    assert "Jira cloudId missing" in captured.err
    assert not any(tool == "searchJiraIssuesUsingJql" for _, tool, _ in calls)


def test_gather_context_maps_topics_and_teams(monkeypatch, capsys):
    calls = []

    def fake_run_mcpc(session, tool, args):
        calls.append((session, tool, args))
        if tool == "notion-search":
            return {"results": [{"id": "page-1"}]}
        if tool == "searchJiraIssuesUsingJql":
            return {"issues": [{"key": "ABC-1", "fields": {"summary": "Test"}}]}
        return None

    monkeypatch.setattr(gather_context, "run_mcpc", fake_run_mcpc)
    monkeypatch.setattr(
        gather_context,
        "load_config",
        lambda _: {
            "google_calendar": False,
            "google_gmail_query": "",
            "topics": [{"keywords": ["alpha", "beta"]}],
            "teams": [{"jira_project": "ABC"}],
            "providers": {"jira": {"cloud_id": "cloud-1"}},
        },
    )

    monkeypatch.setattr("sys.argv", ["gather_context"])
    gather_context.main()
    captured = capsys.readouterr()

    output = json.loads(captured.out)
    assert "notion" in output
    assert "jira" in output
    assert any(
        tool == "notion-search" and args["query"] == "alpha"
        for _, tool, args in calls
    )
    assert any(
        tool == "searchJiraIssuesUsingJql" and args["cloudId"] == "cloud-1"
        for _, tool, args in calls
    )
