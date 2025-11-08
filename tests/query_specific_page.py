#!/usr/bin/env python3
"""
Query the specific page to see what calculations exist
"""

import requests
import json

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"
PAGE_ID = "9Ui8lEJAc6rXv3dS0P-s0"

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
print(f" Querying Page: {PAGE_ID}")
print("="*70)

# Check if there's a way to query calculations by page
print("\n[1] Looking for queries that accept pageId...")

introspect = execute_query("""
    query {
      __schema {
        queryType {
          fields {
            name
            args {
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
      }
    }
""")

if "data" in introspect:
    fields = introspect["data"]["__schema"]["queryType"]["fields"]
    page_queries = [f for f in fields if any(arg["name"] == "pageId" for arg in f["args"])]
    print("Queries that accept pageId:")
    for q in page_queries:
        print(f"  - {q['name']}")
        for arg in q["args"]:
            print(f"    arg: {arg['name']} ({arg['type'].get('name', arg['type'].get('ofType', {}).get('name', 'complex'))})")

# Try the calculation we created
CALC_ID = "1NzN8Vkt1jXOZA8VZA_sx"

print(f"\n[2] Querying calculation we created: {CALC_ID}")

calc_result = execute_query("""
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
          value
          unit
          engine
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": CALC_ID,
    "revisionId": "ffffffff"
})

print(json.dumps(calc_result, indent=2))

# Try to find calculations on this workspace
print(f"\n[3] Checking workspace calculation stats...")

stats = execute_query("""
    query GetStats($workspaceId: ID!) {
      workspaceCalculationStats(workspaceId: $workspaceId) {
        totalCalculations
        totalStatements
      }
    }
""", {
    "workspaceId": WORKSPACE_ID
})

print(json.dumps(stats, indent=2))

# Check page itself
print(f"\n[4] Getting page details...")

page = execute_query("""
    query GetPage($workspaceId: ID!, $id: ID!) {
      page(workspaceId: $workspaceId, id: $id) {
        id
        title
        header
        cursor
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "id": PAGE_ID
})

print(json.dumps(page, indent=2))

print("\n" + "="*70)
print("Please tell me:")
print("  1. What is the calculation ID of the statement you manually added?")
print("  2. How did you add it (what UI steps)?")
print("  3. Can you see our created calculation in the RHS panel?")
print("="*70)
