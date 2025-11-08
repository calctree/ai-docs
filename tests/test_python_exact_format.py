#!/usr/bin/env python3
"""
Test python with EXACT network trace format
Replicating exactly what the UI does when manually adding python
"""

import requests
import json
import time

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"
USER_ID = "4d83c852-69a7-4744-8b7c-92d0335386c3"

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
print(" TEST: Python with Exact Network Trace Format")
print("="*70)

# Create NEW page for this test
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
        "title": "TEST: Python Exact Format",
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

# Exactly replicate the manual creation network trace
stmt_id = generate_nanoid()
data_id = generate_nanoid()

print(f"\n[2] Adding python statement with EXACT format from network trace...")
print(f"    statementId: {stmt_id}")
print(f"    data.id: {data_id}")

# Use EXACT same mutation and format as network trace
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
        __typename
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,  # Using page_id as calculationId (from your trace)
    "withStatement": {
        "statementId": stmt_id,
        "title": "Python Code",
        "engine": "python",
        "formula": "# Python test\ntotal = sum(range(5))\nprint(f'Total: {total}')"
    },
    "data": {
        "id": data_id,
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id,
        "userId": USER_ID
    }
})

print(json.dumps(result, indent=2))

# Query to verify
print(f"\n[3] Querying calculation...")

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
print("\nExpected: 1 python statement")
print("Check the page in UI to see if python statement appears!")
print("="*70)
