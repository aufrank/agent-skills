from providers.base import run_mcpc
from datetime import datetime, timedelta

def main():
    dt = datetime.utcnow() - timedelta(days=7)
    date_str = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    email = "aufrank@riotgames.com"
    query = (
        f"(modifiedTime > '{date_str}' or createdTime > '{date_str}') and "
        f"('{email}' in writers or fullText contains '{email}')"
    )
    
    print(f"Query: {query}")
    resp = run_mcpc("@google", "drive.search", {"query": query, "pageSize": 1, "orderBy": "modifiedTime desc"})
    
    if resp:
        print("Response found.")
        if isinstance(resp, dict):
            files = resp.get("files", [])
            if files:
                print("First file keys:", files[0].keys())
                print("Last Modifying User:", files[0].get("lastModifyingUser"))
            else:
                print("No files in list.")
        else:
            print("Response is not dict:", type(resp))
    else:
        print("No response.")

if __name__ == "__main__":
    main()
