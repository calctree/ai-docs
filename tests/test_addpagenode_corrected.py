#!/usr/bin/env python3
"""
Test addPageNode mutation with correct return fields
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

def generate_nanoid():
    try:
        from nanoid import generate
        return generate()
    except ImportError:
        import random
        import string
        alphabet = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choices(alphabet, k=21))

print("="*70)
print(" CORRECT: Create Page + Add to Tree")
print("="*70)

# Step 1: Create page
page_id = generate_nanoid()
print(f"\n[1] Creating page: {page_id}")

create_result = execute_query("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
        title
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {
        "id": page_id,
        "title": "Correctly Added to Tree",
        "workspaceId": WORKSPACE_ID
    }
})

if "errors" in create_result:
    print("[ERROR]", json.dumps(create_result["errors"], indent=2))
    exit(1)

print("[SUCCESS] Page created")

# Step 2: Add to page tree with correct fields
print(f"\n[2] Adding page to tree...")

add_node_result = execute_query("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) {
        newPageId
        parentId
        correlation {
          correlationId
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {
        "pageId": page_id
    }
})

print(json.dumps(add_node_result, indent=2))

if "errors" in add_node_result:
    print("[ERROR] Failed to add to tree")
else:
    print("[SUCCESS] Page added to tree!")

# Step 3: Test with parentId
print(f"\n[3] Creating child page with parentId...")

child_page_id = generate_nanoid()

create_child_result = execute_query("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
        title
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {
        "id": child_page_id,
        "title": "Child Page",
        "workspaceId": WORKSPACE_ID
    }
})

if "data" in create_child_result:
    print("[SUCCESS] Child page created")

    # Add to tree with parent
    add_child_result = execute_query("""
        mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
          addPageNode(workspaceId: $workspaceId, input: $input) {
            newPageId
            parentId
            correlation {
              correlationId
            }
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "input": {
            "pageId": child_page_id,
            "parentId": page_id
        }
    })

    print(json.dumps(add_child_result, indent=2))

    if "errors" not in add_child_result:
        print("[SUCCESS] Child page added to tree under parent!")

print("\n" + "="*70)
print(" Summary")
print("="*70)
print(f"Parent page: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print(f"Child page:  https://app.calctree.com/edit/{WORKSPACE_ID}/{child_page_id}")
print("="*70)
