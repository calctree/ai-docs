#!/usr/bin/env python3
"""
Test correct mathjs syntax based on user feedback:
- Formula should be: variable_name = 10 m (not just "10 m")
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
print(" TEST: Correct MathJS Syntax")
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
        "title": "TEST: Correct Syntax",
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

# Create calculation with CORRECT syntax: variable_name = value
print(f"\n[2] Creating statements with variable_name = value syntax...")

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
            "title": "beam_length",
            "engine": "mathjs",
            "formula": "beam_length = 10 m"  # CORRECT: variable_name = value
        },
        {
            "statementId": generate_nanoid(),
            "title": "beam_width",
            "engine": "mathjs",
            "formula": "beam_width = 300 mm"
        },
        {
            "statementId": generate_nanoid(),
            "title": "load",
            "engine": "mathjs",
            "formula": "load = 5 kN"
        },
        {
            "statementId": generate_nanoid(),
            "title": "moment",
            "engine": "mathjs",
            "formula": "moment = load * beam_length"  # References other variables
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
print("\nStatements created with CORRECT syntax:")
print("  1. beam_length = 10 m")
print("  2. beam_width = 300 mm")
print("  3. load = 5 kN")
print("  4. moment = load * beam_length (references other variables)")
print("="*70)
