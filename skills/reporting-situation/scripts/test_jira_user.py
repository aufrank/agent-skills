from providers.base import run_mcpc

def main():
    print("Getting Cloud ID...")
    resources = run_mcpc("@jira", "getAccessibleAtlassianResources", {})
    if not resources:
        print("Failed to get resources.")
        return

    cloud_id = resources[0]['id']
    print(f"Cloud ID: {cloud_id}")
    
    handle = "Israel Knight" # Try name search
    print(f"Looking up: {handle}")
    
    users = run_mcpc("@jira", "lookupJiraAccountId", {"cloudId": cloud_id, "searchString": handle})
    if users:
        print("Found users:")
        for u in users:
            print(f"- {u.get('displayName')} ({u.get('accountId')})")
    else:
        print("No users found.")

if __name__ == "__main__":
    main()
