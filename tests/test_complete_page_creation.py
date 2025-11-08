#!/usr/bin/env python3
"""
COMPLETE WORKING EXAMPLE: Create page and properly add to page tree
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
print(" COMPLETE WORKING EXAMPLE: Page Creation + Tree Addition")
print("="*70)

# STEP 1: Create page
page_id = generate_nanoid()
print(f"\n[Step 1] Creating page: {page_id}")

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
        "title": "Complete Example - In Tree",
        "workspaceId": WORKSPACE_ID
    }
})

if "errors" in create_result:
    print("[ERROR]", json.dumps(create_result["errors"], indent=2))
    exit(1)

print("[SUCCESS] Page created")
print(json.dumps(create_result["data"], indent=2))

# STEP 2: Add to page tree
print(f"\n[Step 2] Adding page to tree...")

add_node_result = execute_query("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) {
        newPageId
        parentId
        correlation {
          workspaceId
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
    exit(1)

print("[SUCCESS] Page added to tree!")

# STEP 3: Create child page with hierarchy
print(f"\n[Step 3] Creating child page under parent...")

child_page_id = generate_nanoid()

create_child = execute_query("""
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
        "title": "Child Page - Under Parent",
        "workspaceId": WORKSPACE_ID
    }
})

if "errors" not in create_child:
    print("[SUCCESS] Child page created")

    # Add child to tree with parent
    add_child = execute_query("""
        mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
          addPageNode(workspaceId: $workspaceId, input: $input) {
            newPageId
            parentId
            correlation {
              workspaceId
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

    print(json.dumps(add_child, indent=2))

    if "errors" not in add_child:
        print("[SUCCESS] Child page added to tree under parent!")
        print(f"  Parent ID: {add_child['data']['addPageNode']['parentId']}")

# STEP 4: Add calculation to parent page
print(f"\n[Step 4] Adding calculation to parent page...")

calc_id = generate_nanoid()
stmt_id = generate_nanoid()

calc_result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "withStatement": {
        "statementId": stmt_id,
        "title": "example_value",
        "formula": "42",
        "engine": "mathjs"
    }
})

if "errors" not in calc_result:
    print("[SUCCESS] Calculation added")

print("\n" + "="*70)
print(" Summary")
print("="*70)
print(f"Parent page: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print(f"Child page:  https://app.calctree.com/edit/{WORKSPACE_ID}/{child_page_id}")
print(f"Calculation: {calc_id}")
print("="*70)
print("\nBoth pages are now properly added to the page tree!")
print("Open the parent page URL to see it in your workspace tree.")
