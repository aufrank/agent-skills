from providers.base import run_mcpc
import sys

def main():
    resources = run_mcpc("@jira", "getAccessibleAtlassianResources", {})
    if not resources: return
    cloud_id = resources[0]['id']
    
    # Resolving "Austin Frank" or similar to get a real accountId to test with would be ideal, 
    # but let's try with "currentUser()" first for safety.
    
    jql_candidates = [
        'lastCommentBy = currentUser()',
        'watcher = currentUser()'
    ]
    
    for jql in jql_candidates:
        print(f"Testing JQL: {jql}")
        resp = run_mcpc("@jira", "searchJiraIssuesUsingJql", {"cloudId": cloud_id, "jql": jql, "maxResults": 1})
        
        if resp and isinstance(resp, dict) and "issues" in resp:
            print(f"  -> Success! Found {len(resp['issues'])} issues.")
        else:
            print(f"  -> Failed. Response: {resp}")

if __name__ == "__main__":
    main()
