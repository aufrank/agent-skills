from providers.registry import build_provider_registry


def test_registry_includes_expected_providers():
    config = {
        "providers": {
            "jira": {
                "cloud_id": "cloud-xyz",
                "base_url": "https://example.atlassian.net",
            }
        }
    }
    registry = build_provider_registry(config)
    assert set(registry.keys()) == {"google", "notion", "jira"}
    assert registry["jira"].cloud_id == "cloud-xyz"
