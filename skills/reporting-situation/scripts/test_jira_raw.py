from providers.base import run_mcpc
import json

def main():
    print("Getting Cloud ID...")
    resources = run_mcpc("@jira", "getAccessibleAtlassianResources", {})
    print(f"RAW: {json.dumps(resources, indent=2)}")

if __name__ == "__main__":
    main()
