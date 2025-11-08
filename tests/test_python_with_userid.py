#!/usr/bin/env python3
"""
Create python statement with userId in data (from network trace)
"""

import requests
import json
import time

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"
USER_ID = "4d83c852-69a7-4744-8b7c-92d0335386c3"  # From network trace

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
print(" TEST: Python with userId in data")
print("="*70)

# Use existing page from previous test
page_id = "q2WPMwb7KPFfVNLHgBfMs"
print(f"\nUsing existing page: {page_id}")

# Add python statement with userId (matching network trace format exactly)
stmt_id = generate_nanoid()
print(f"\n[1] Adding python statement with userId...")

result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
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
    "withStatement": {
        "statementId": stmt_id,
        "title": "Python Code",
        "engine": "python",
        "formula": "# Python test\ntotal = sum(range(5))\nprint(f'Total: {total}')"
    },
    "data": {
        "id": generate_nanoid(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id,
        "userId": USER_ID  # Adding userId from network trace
    }
})

print(json.dumps(result, indent=2))

# Query to verify
print(f"\n[2] Querying calculation...")

query_result = execute_query("""
    query GetCalc($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
      calculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
      ) {
        statements {
          title
          engine
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

print("\n" + "="*70)
print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("="*70)
