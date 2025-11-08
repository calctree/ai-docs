#!/usr/bin/env python3
"""
Create a page with python statements only
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
print(" TEST: Python Statements Only")
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
        "title": "TEST: Python Only",
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

# Create calculation with multiple python statements
print(f"\n[2] Creating calculation with 3 python statements...")

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
    "calculationId": page_id,
    "withStatements": [
        {
            "statementId": generate_nanoid(),
            "title": "Basic Math",
            "engine": "python",
            "formula": "import math\nresult = math.sqrt(16)\nprint(f'Square root: {result}')"
        },
        {
            "statementId": generate_nanoid(),
            "title": "List Operations",
            "engine": "python",
            "formula": "numbers = [1, 2, 3, 4, 5]\ntotal = sum(numbers)\naverage = total / len(numbers)\nprint(f'Average: {average}')"
        },
        {
            "statementId": generate_nanoid(),
            "title": "String Formatting",
            "engine": "python",
            "formula": "name = 'CalcTree'\nversion = '2.0'\nmessage = f'{name} v{version}'\nprint(message)"
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

# Query to verify
print(f"\n[3] Querying all statements...")

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
print("\nExpected: 3 python statements")
print("="*70)
