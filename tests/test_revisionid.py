#!/usr/bin/env python3
"""
Test revisionId handling
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

def generate_nanoid():
    try:
        from nanoid import generate
        return generate()
    except ImportError:
        import random
        import string
        alphabet = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choices(alphabet, k=21))

# Create page
page_id = generate_nanoid()
page_result = execute_query("""
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
        "title": "RevisionId Test",
        "workspaceId": WORKSPACE_ID
    }
})

print("Page created:", json.dumps(page_result, indent=2))

# Create calculation
calc_id = generate_nanoid()
stmt_id_1 = generate_nanoid()

calc_result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
        revisionId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "withStatement": {
        "statementId": stmt_id_1,
        "title": "x",
        "formula": "5",
        "engine": "mathjs"
    }
})

print("\nCalculation created:", json.dumps(calc_result, indent=2))

# Try adding statement with revisionId = "ffffffff"
print("\n" + "="*60)
print("Testing addStatementSync with revisionId = 'ffffffff'")
print("="*60)

stmt_id_2 = generate_nanoid()

add_result_fff = execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $input: CreateStatementInput!) {
      addStatementSync(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        input: $input
      ) {
        calculationId
        revisionId
        statement {
          statementId
          title
          formula
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "revisionId": "ffffffff",
    "input": {
        "statementId": stmt_id_2,
        "title": "y",
        "formula": "10",
        "engine": "mathjs"
    }
})

print(json.dumps(add_result_fff, indent=2))

# If ffffffff works, try adding another statement
if "data" in add_result_fff and add_result_fff["data"]["addStatementSync"]:
    print("\n[SUCCESS] ffffffff works!")
    new_revision = add_result_fff["data"]["addStatementSync"]["revisionId"]
    print(f"New revisionId: {new_revision}")

    # Add another statement using ffffffff again
    stmt_id_3 = generate_nanoid()
    add_result_2 = execute_query("""
        mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $input: CreateStatementInput!) {
          addStatementSync(
            workspaceId: $workspaceId
            calculationId: $calculationId
            revisionId: $revisionId
            input: $input
          ) {
            calculationId
            revisionId
            statement {
              statementId
              title
              formula
            }
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": calc_id,
        "revisionId": "ffffffff",
        "input": {
            "statementId": stmt_id_3,
            "title": "z",
            "formula": "x + y",
            "engine": "mathjs"
        }
    })

    print("\nAdding third statement with ffffffff:")
    print(json.dumps(add_result_2, indent=2))

print(f"\nPage URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
