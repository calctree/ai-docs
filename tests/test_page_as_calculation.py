#!/usr/bin/env python3
"""
Test using pageId as calculationId based on network inspection
"""

import requests
import json
import time

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
    from nanoid import generate
    return generate()

print("="*70)
print(" CRITICAL TEST: Using PageId as CalculationId")
print("="*70)

# Create a new test page
page_id = generate_nanoid()
print(f"\n[1] Creating page: {page_id}")

create_page = execute_query("""
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
        "title": "TEST: Page=Calc ID",
        "workspaceId": WORKSPACE_ID
    }
})

print(json.dumps(create_page, indent=2))

# Add to tree
execute_query("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) {
        newPageId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {"pageId": page_id}
})

print("[SUCCESS] Page created and added to tree")

# NOW: Use the PAGE_ID as the CALCULATION_ID!
print(f"\n[2] Adding statement to calculation (using pageId as calculationId)...")

stmt_id_1 = generate_nanoid()
cursor_id = generate_nanoid()  # Generate a cursor/id for data field
timestamp = int(time.time() * 1000)  # Current timestamp in milliseconds

# Based on the network trace, use addStatementToCalculation with pageId as calculationId
result = execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        revisionId
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,  # KEY CHANGE: Use page_id as calculation_id!
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id_1,
        "title": "length",
        "engine": "mathjs",
        "formula": "length = 10 m"
    },
    "data": {
        "id": cursor_id,
        "cursor": "ffffffff",
        "timestamp": timestamp
    }
})

print(json.dumps(result, indent=2))

# Add more statements
if "data" in result and not "errors" in result:
    print("\n[3] Adding more statements...")

    returned_revision = result["data"]["addStatementToCalculation"]["revisionId"]

    # Statement 2
    stmt_id_2 = generate_nanoid()
    cursor_id_2 = generate_nanoid()

    result2 = execute_query("""
        mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
          addStatementToCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            revisionId: $revisionId
            withStatement: $withStatement
            data: $data
          ) {
            revisionId
            calculationId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "revisionId": returned_revision if returned_revision else "ffffffff",
        "withStatement": {
            "statementId": stmt_id_2,
            "title": "width",
            "engine": "mathjs",
            "formula": "width = 5 m"
        },
        "data": {
            "id": cursor_id_2,
            "cursor": returned_revision if returned_revision else "ffffffff",
            "timestamp": int(time.time() * 1000)
        }
    })

    print(json.dumps(result2, indent=2))

    # Statement 3 - calculated value
    if "data" in result2:
        stmt_id_3 = generate_nanoid()
        cursor_id_3 = generate_nanoid()
        revision_3 = result2["data"]["addStatementToCalculation"]["revisionId"]

        result3 = execute_query("""
            mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
              addStatementToCalculation(
                workspaceId: $workspaceId
                calculationId: $calculationId
                revisionId: $revisionId
                withStatement: $withStatement
                data: $data
              ) {
                revisionId
                calculationId
              }
            }
        """, {
            "workspaceId": WORKSPACE_ID,
            "calculationId": page_id,
            "revisionId": revision_3 if revision_3 else "ffffffff",
            "withStatement": {
                "statementId": stmt_id_3,
                "title": "area",
                "engine": "mathjs",
                "formula": "area = length * width"
            },
            "data": {
                "id": cursor_id_3,
                "cursor": revision_3 if revision_3 else "ffffffff",
                "timestamp": int(time.time() * 1000)
            }
        })

        print(json.dumps(result3, indent=2))

print("\n" + "="*70)
print(" TEST COMPLETE")
print("="*70)
print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print(f"\nCalculation ID = Page ID = {page_id}")
print("\nPlease check if statements appear in the RHS panel!")
print("="*70)
