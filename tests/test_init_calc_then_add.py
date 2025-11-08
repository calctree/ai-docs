#!/usr/bin/env python3
"""
Test: Initialize calculation FIRST, then add statements
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
print(" TEST: Initialize Calculation First")
print("="*70)

# Create page
page_id = generate_nanoid()
print(f"\n[1] Creating page: {page_id}")

execute_query("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {
        "id": page_id,
        "title": "TEST: Init Calc First",
        "workspaceId": WORKSPACE_ID
    }
})

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

print("[SUCCESS]")

# STEP 1: Initialize the calculation using createOrUpdateCalculation
print(f"\n[2] Initializing calculation (pageId = calculationId)...")

stmt_id_1 = generate_nanoid()

init_result = execute_query("""
    mutation InitCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) {
        calculationId
        revisionId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,  # Use page_id as calc_id
    "withStatements": [
        {
            "statementId": stmt_id_1,
            "title": "length",
            "engine": "mathjs",
            "formula": "length = 10 m"
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate_nanoid(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

print(json.dumps(init_result, indent=2))

# Now query it back
print(f"\n[3] Querying calculation...")

if "data" in init_result:
    query_result = execute_query("""
        query GetCalc($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
          calculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            revisionId: $revisionId
          ) {
            calculationId
            revisionId
            statements {
              statementId
              title
              formula
            }
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "revisionId": "ffffffff"
    })

    print(json.dumps(query_result, indent=2))

    # If that worked, try adding more statements
    if "data" in query_result and query_result["data"]["calculation"]:
        print("\n[4] Adding more statements...")

        revision = query_result["data"]["calculation"]["revisionId"]
        stmt_id_2 = generate_nanoid()

        add_result = execute_query("""
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
            "revisionId": revision,
            "withStatement": {
                "statementId": stmt_id_2,
                "title": "width",
                "engine": "mathjs",
                "formula": "width = 5 m"
            },
            "data": {
                "pageId": page_id,
                "id": generate_nanoid(),
                "cursor": revision,
                "timestamp": int(time.time() * 1000)
            }
        })

        print(json.dumps(add_result, indent=2))

        # Query again
        print("\n[5] Final query...")
        final_query = execute_query("""
            query GetCalc($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
              calculation(
                workspaceId: $workspaceId
                calculationId: $calculationId
                revisionId: $revisionId
              ) {
                statements {
                  statementId
                  title
                  formula
                }
              }
            }
        """, {
            "workspaceId": WORKSPACE_ID,
            "calculationId": page_id,
            "revisionId": "ffffffff"
        })

        print(json.dumps(final_query, indent=2))

print("\n" + "="*70)
print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("Check if statements appear in RHS panel!")
print("="*70)
