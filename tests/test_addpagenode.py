#!/usr/bin/env python3
"""
Test addPageNode mutation to properly add pages to the page tree
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
print(" Testing addPageNode Mutation")
print("="*70)

# Step 1: Introspect AddPageNodeInput
print("\n[1] Introspecting AddPageNodeInput schema...")

introspect_result = execute_query("""
    query {
      __type(name: "AddPageNodeInput") {
        name
        inputFields {
          name
          type {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
      }
    }
""")

print(json.dumps(introspect_result, indent=2))

# Step 2: Introspect addPageNode mutation
print("\n[2] Introspecting addPageNode mutation...")

mutation_introspect = execute_query("""
    query {
      __type(name: "Mutation") {
        fields {
          name
          args {
            name
            type {
              name
              kind
              ofType {
                name
                kind
              }
            }
          }
        }
      }
    }
""")

if "data" in mutation_introspect:
    fields = mutation_introspect["data"]["__type"]["fields"]
    page_node_mutations = [f for f in fields if "PageNode" in f["name"]]
    print(json.dumps(page_node_mutations, indent=2))

# Step 3: Introspect AddPageNodePayload
print("\n[3] Introspecting AddPageNodePayload...")

payload_introspect = execute_query("""
    query {
      __type(name: "AddPageNodePayload") {
        name
        fields {
          name
          type {
            name
            kind
            ofType {
              name
            }
          }
        }
      }
    }
""")

print(json.dumps(payload_introspect, indent=2))

# Step 4: Test creating a page WITH addPageNode
print("\n[4] Creating page WITH addPageNode...")

page_id = generate_nanoid()
print(f"Generated page ID: {page_id}")

# First create the page
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
        "title": "Test Page with addPageNode",
        "workspaceId": WORKSPACE_ID
    }
})

print("Page creation result:")
print(json.dumps(create_result, indent=2))

if "data" in create_result and create_result["data"]["createPageSync"]:
    # Now add to page tree
    print(f"\n[5] Adding page to tree with addPageNode...")

    add_node_result = execute_query("""
        mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
          addPageNode(workspaceId: $workspaceId, input: $input) {
            pageNode {
              id
              title
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

    # Check if addPageNodeSync exists
    print(f"\n[6] Checking for addPageNodeSync...")

    sync_fields = [f for f in fields if f["name"] == "addPageNodeSync"]
    if sync_fields:
        print("addPageNodeSync exists!")
        print(json.dumps(sync_fields, indent=2))
    else:
        print("addPageNodeSync does not exist yet")

print("\n" + "="*70)
print(" Complete")
print("="*70)
print(f"\nPage URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
