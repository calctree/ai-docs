#!/usr/bin/env python3
"""
Query the calculation you manually created
"""

import requests
import json

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"

# From your network trace:
# calculationId: "9Ui8lEJAc6rXv3dS0P-s0" (same as pageId)
# revisionId: "35BCWQN6Yf1zLTwBmEe2RzQUp2R"

PAGE_ID = "9Ui8lEJAc6rXv3dS0P-s0"
CALC_ID = PAGE_ID
REVISION_ID = "35BCWQN6Yf1zLTwBmEe2RzQUp2R"

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
print(" Querying YOUR Manually Created Calculation")
print("="*70)
print(f"Page/Calc ID: {CALC_ID}")
print(f"Revision ID: {REVISION_ID}")

# Query with the exact revisionId from your manual creation
print("\n[1] Querying with your revisionId...")

result = execute_query("""
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
          engine
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": CALC_ID,
    "revisionId": REVISION_ID
})

print(json.dumps(result, indent=2))

# Try with ffffffff
print("\n[2] Trying with ffffffff...")

result2 = execute_query("""
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
          engine
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": CALC_ID,
    "revisionId": "ffffffff"
})

print(json.dumps(result2, indent=2))

# Check calculation history
print("\n[3] Checking calculation history...")

history = execute_query("""
    query GetHistory($workspaceId: ID!, $calculationId: ID!, $first: Int) {
      calculationHistory(
        workspaceId: $workspaceId
        calculationId: $calculationId
        first: $first
      ) {
        edges {
          cursor
          node {
            revisionId
            statements {
              statementId
              title
              formula
            }
          }
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": CALC_ID,
    "first": 10
})

print(json.dumps(history, indent=2))

print("\n" + "="*70)
