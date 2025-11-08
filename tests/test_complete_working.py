#!/usr/bin/env python3
"""
Complete working example with correct revisionId handling
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

print("="*70)
print(" COMPLETE WORKING EXAMPLE: Page + Multiple Calculations")
print("="*70)

# Step 1: Create page
page_id = generate_nanoid()
print(f"\n[1] Creating page: {page_id}")

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
        "title": "Complete Beam Calculation",
        "workspaceId": WORKSPACE_ID
    }
})

if "errors" in page_result:
    print("[ERROR]", json.dumps(page_result["errors"], indent=2))
    exit(1)

print("[SUCCESS] Page created")
page_url = f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}"

# Step 2: Create calculation with first statement
calc_id = generate_nanoid()
stmt_id_1 = generate_nanoid()

print(f"\n[2] Creating calculation: {calc_id}")
print(f"    First statement: {stmt_id_1}")

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
        "title": "beam_length",
        "formula": "10 m",
        "engine": "mathjs"
    }
})

if "errors" in calc_result:
    print("[ERROR]", json.dumps(calc_result["errors"], indent=2))
    exit(1)

print("[SUCCESS] Calculation created")
print(f"Returned revisionId: {calc_result['data']['createCalculation']['revisionId']}")

# Step 3: Add second statement using revisionId = "ffffffff"
print(f"\n[3] Adding second statement using revisionId='ffffffff'")

stmt_id_2 = generate_nanoid()

add_result_1 = execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
      ) {
        calculationId
        revisionId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id_2,
        "title": "load",
        "formula": "1000 N",
        "engine": "mathjs"
    }
})

if "errors" in add_result_1:
    print("[ERROR]", json.dumps(add_result_1["errors"], indent=2))
else:
    print("[SUCCESS] Second statement added")
    print(f"Returned revisionId: {add_result_1['data']['addStatementToCalculation']['revisionId']}")

    # Step 4: Add third statement (calculated value)
    print(f"\n[4] Adding third statement (calculated) using revisionId='ffffffff'")

    stmt_id_3 = generate_nanoid()

    add_result_2 = execute_query("""
        mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!) {
          addStatementToCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            revisionId: $revisionId
            withStatement: $withStatement
          ) {
            calculationId
            revisionId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": calc_id,
        "revisionId": "ffffffff",
        "withStatement": {
            "statementId": stmt_id_3,
            "title": "moment",
            "formula": "load * beam_length",
            "engine": "mathjs"
        }
    })

    if "errors" in add_result_2:
        print("[ERROR]", json.dumps(add_result_2["errors"], indent=2))
    else:
        print("[SUCCESS] Third statement added")
        print(f"Returned revisionId: {add_result_2['data']['addStatementToCalculation']['revisionId']}")

print("\n" + "="*70)
print(" SUMMARY")
print("="*70)
print(f"Page URL:       {page_url}")
print(f"Page ID:        {page_id}")
print(f"Calculation ID: {calc_id}")
print("="*70)
print("\nOpen the page URL to see your calculations!")
