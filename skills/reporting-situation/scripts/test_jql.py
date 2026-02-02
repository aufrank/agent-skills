from providers.base import run_mcpc
import sys

def main():
    resources = run_mcpc("@jira", "getAccessibleAtlassianResources", {})
    if not resources: return
    cloud_id = resources[0]['id']
    
    # Try updatedBy syntax
    jql = 'issuekey IN updatedBy("currentUser()", "-1d")'
    print(f"Testing JQL: {jql}")
    resp = run_mcpc("@jira", "searchJiraIssuesUsingJql", {"cloudId": cloud_id, "jql": jql})
    
    if resp and isinstance(resp, dict) and "issues" in resp:
        print("Success! 'updatedBy' is supported.")
    else:
        print("Failed. 'updatedBy' probably not supported or syntax error.")
        # print(resp)

if __name__ == "__main__":
    main()
