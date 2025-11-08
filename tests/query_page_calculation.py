#!/usr/bin/env python3
"""
Query the calculation on the page we just created
"""

import requests
import json

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"

# The page we just created where calculationId = pageId
PAGE_ID = "lnznMQnnEyWZZp8eyAO46"
CALC_ID = PAGE_ID  # They're the same!

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
print(f" Querying Calculation on Page: {PAGE_ID}")
print("="*70)

# Try to get the calculation stats first
print("\n[1] Getting calculation stats...")

stats = execute_query("""
    query GetStats($workspaceId: ID!, $calculationId: ID!) {
      calculationStats(workspaceId: $workspaceId, calculationId: $calculationId)
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": CALC_ID
})

print(json.dumps(stats, indent=2))

# Get the calculation history to find revisions
print("\n[2] Getting calculation history...")

history = execute_query("""
    query GetHistory($workspaceId: ID!, $calculationId: ID!) {
      calculationHistory(workspaceId: $workspaceId, calculationId: $calculationId, first: 10) {
        edges {
          cursor
          node {
            revisionId
            statementCount
            timestamp
          }
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": CALC_ID
})

print(json.dumps(history, indent=2))

# Try different revisionIds
print("\n[3] Trying different revisionIds...")

revision_attempts = ["ffffffff", "0", "latest", "35BCWQN6Yf1zLTwBmEe2RzQUp2R"]

for rev_id in revision_attempts:
    print(f"\n  Attempting with revisionId: {rev_id}")

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
        "revisionId": rev_id
    })

    if "errors" not in result:
        print("  [SUCCESS]")
        print(json.dumps(result, indent=2))
        break
    else:
        print(f"  [FAILED] {result['errors'][0]['message']}")

# Also try to introspect what the calculation query actually returns
print("\n[4] Introspecting Calculation type...")

introspect = execute_query("""
    query {
      __type(name: "Calculation") {
        name
        fields {
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
""")

print("Calculation type fields:")
if "data" in introspect:
    for field in introspect["data"]["__type"]["fields"]:
        print(f"  - {field['name']}: {field['type'].get('name', field['type'].get('ofType', {}).get('name', 'complex'))}")

print("\n" + "="*70)
