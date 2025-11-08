#!/usr/bin/env python3
"""
Simple query to check our created calculation
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

# Our created calculation
CALC_ID = "1NzN8Vkt1jXOZA8VZA_sx"
PAGE_ID = "9Ui8lEJAc6rXv3dS0P-s0"

print("="*70)
print(" Checking Our API-Created Calculation")
print("="*70)

print(f"\nCalculation ID: {CALC_ID}")
print(f"Page ID: {PAGE_ID}")

# Query the calculation
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

print("\n[Calculation Query Result]:")
print(json.dumps(result, indent=2))

# Check the calculation stats to get the actual revision ID
print("\n[Getting calculation stats]:")
stats = execute_query("""
    query GetStats($workspaceId: ID!, $calculationId: ID!) {
      calculationStats(workspaceId: $workspaceId, calculationId: $calculationId) {
        latestRevisionId
        statementCount
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": CALC_ID
})

print(json.dumps(stats, indent=2))

print("\n" + "="*70)
print("QUESTION: Does calculation", CALC_ID)
print("appear in the RHS panel when you view the page?")
print("="*70)
print("\nPage URL:", f"https://app.calctree.com/edit/{WORKSPACE_ID}/{PAGE_ID}")
