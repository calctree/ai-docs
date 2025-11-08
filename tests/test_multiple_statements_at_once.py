#!/usr/bin/env python3
"""
Test: Use createOrUpdateCalculation with MULTIPLE statements
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
print(" TEST: Multiple Statements with createOrUpdateCalculation")
print("="*70)

# Create page
page_id = generate_nanoid()
print(f"\n[1] Creating page: {page_id}")

execute_query("""
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
        "title": "TEST: Multiple Statements at Once",
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

print("[SUCCESS] Page created and added to tree")

# Create calculation with MULTIPLE statements
print(f"\n[2] Creating calculation with 5 statements at once...")

stmt_ids = [generate_nanoid() for _ in range(5)]

calc_result = execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
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
    "calculationId": page_id,  # page_id = calc_id
    "withStatements": [
        {
            "statementId": stmt_ids[0],
            "title": "beam_length",
            "engine": "mathjs",
            "formula": "beam_length = 10 m"
        },
        {
            "statementId": stmt_ids[1],
            "title": "load",
            "engine": "mathjs",
            "formula": "load = 5000 N"
        },
        {
            "statementId": stmt_ids[2],
            "title": "moment",
            "engine": "mathjs",
            "formula": "moment = load * beam_length"
        },
        {
            "statementId": stmt_ids[3],
            "title": "safety_factor",
            "engine": "mathjs",
            "formula": "safety_factor = 1.5"
        },
        {
            "statementId": stmt_ids[4],
            "title": "design_moment",
            "engine": "mathjs",
            "formula": "design_moment = moment * safety_factor"
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate_nanoid(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

print(json.dumps(calc_result, indent=2))

# Query it back
print(f"\n[3] Querying calculation...")

query_result = execute_query("""
    query GetCalc($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
      calculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
      ) {
        calculationId
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

if "data" in query_result and query_result["data"]["calculation"]:
    statement_count = len(query_result["data"]["calculation"]["statements"])
    print(f"\n[SUCCESS] Found {statement_count} statements")

print("\n" + "="*70)
print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("\nExpected 5 statements:")
print("  1. beam_length = 10 m")
print("  2. load = 5000 N")
print("  3. moment = load * beam_length")
print("  4. safety_factor = 1.5")
print("  5. design_moment = moment * safety_factor")
print("\nCheck if all 5 appear in the RHS panel!")
print("="*70)
