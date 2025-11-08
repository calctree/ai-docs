#!/usr/bin/env python3
"""
Examine existing pages to understand how calculations are linked
"""

import requests
import json

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def execute_query(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=payload)
    return response.json()

print("="*70)
print(" Examining Existing Pages")
print("="*70)

# Get all pages
print("\n[1] Getting all pages...")

pages_result = execute_query("""
    query GetPages($workspaceId: ID!) {
      pages(workspaceId: $workspaceId) {
        id
        title
        deletedAt
      }
    }
""", {
    "workspaceId": WORKSPACE_ID
})

if "data" in pages_result and pages_result["data"]["pages"]:
    active_pages = [p for p in pages_result["data"]["pages"] if p["deletedAt"] is None or p["deletedAt"] == "null"]
    print(f"Found {len(active_pages)} active pages")

    # Show first 10
    for page in active_pages[:10]:
        print(f"  - {page['id']}: {page['title']}")

    # Check content of first page
    if active_pages:
        first_page = active_pages[0]
        print(f"\n[2] Checking content of page: {first_page['title']}")

        content = execute_query("""
            query GetPageContent($workspaceId: ID!, $pageId: ID!) {
              pageContent(workspaceId: $workspaceId, pageId: $pageId) {
                pageId
                content
                version
              }
            }
        """, {
            "workspaceId": WORKSPACE_ID,
            "pageId": first_page["id"]
        })

        print(json.dumps(content, indent=2))

print("\n" + "="*70)
print("Analysis complete")
print("="*70)
