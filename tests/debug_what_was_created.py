#!/usr/bin/env python3
"""
Debug what was actually created
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

# The pages we created that supposedly worked
test_pages = [
    ("sB5JJ-ptCwxRMfHU0N028", "5 mathjs statements"),
    ("tTP-tIBzgpq_A5vrD4i95", "mixed engine types"),
]

print("="*70)
print(" Debugging What Was Created")
print("="*70)

for page_id, description in test_pages:
    print(f"\n[Page: {page_id}] ({description})")
    print(f"URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")

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

    if "errors" in result:
        print("  [ERROR]", result["errors"][0]["message"])
    elif "data" in result and result["data"]["calculation"]:
        calc = result["data"]["calculation"]
        print(f"  Calculation ID: {calc['calculationId']}")
        print(f"  Revision ID: {calc['revisionId']}")
        print(f"  Statements: {len(calc['statements'])}")
        for stmt in calc['statements']:
            print(f"    - [{stmt['engine']}] {stmt['title']}")
    else:
        print("  [NO DATA] calculation returned null")

# Now let's compare with your manually created one
print("\n" + "="*70)
print(" YOUR Manually Created Page (for comparison)")
print("="*70)

manual_page = "9Ui8lEJAc6rXv3dS0P-s0"
print(f"Page: {manual_page}")

manual_result = execute_query("""
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
          engine
          formula
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": manual_page,
    "revisionId": "ffffffff"
})

if "data" in manual_result and manual_result["data"]["calculation"]:
    calc = manual_result["data"]["calculation"]
    print(f"  Statements: {len(calc['statements'])}")
    for stmt in calc['statements']:
        print(f"    - [{stmt['engine']}] {stmt['title']}: {stmt['formula']}")

print("\n" + "="*70)
print("\nQUESTION: What's the difference between our API-created")
print("calculations and your manually-created ones?")
print("="*70)
