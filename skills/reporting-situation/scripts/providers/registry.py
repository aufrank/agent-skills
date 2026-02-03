from .google import GoogleProvider
from .notion import NotionProvider
from .jira import JiraProvider


def build_provider_registry(config):
    providers_config = config.get("providers", {}) if config else {}
    jira_config = providers_config.get("jira", {})

    return {
        "google": GoogleProvider(),
        "notion": NotionProvider(),
        "jira": JiraProvider(
            cloud_id=jira_config.get("cloud_id"),
            base_url=jira_config.get("base_url"),
        ),
    }
