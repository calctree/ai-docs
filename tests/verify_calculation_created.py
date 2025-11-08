#!/usr/bin/env python3
"""
Verify that calculations were actually created with statements
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

print("="*70)
print(" Verifying Calculation Creation")
print("="*70)

# These are calculation IDs we created in previous tests
test_calculations = [
    ("NUdbzKyemNw15KK7nRh-3", "0cEWulNSnpnpRus4yxNMW"),  # (calc_id, page_id)
    ("xL6ulPuuMekCvyMvMveHz", "2SLiEsY6xoMnDr4TEyzXw"),
]

for calc_id, page_id in test_calculations:
    print(f"\n[Checking] Calculation: {calc_id}")
    print(f"           Page: {page_id}")

    # First try with revisionId = "ffffffff"
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
        "calculationId": calc_id,
        "revisionId": "ffffffff"
    })

    if "errors" in result:
        print("  [ERROR] with ffffffff:")
        print(json.dumps(result["errors"], indent=2))

        # Try with the actual revisionId from the calculation
        # Get revisionId first
        stats = execute_query("""
            query GetStats($workspaceId: ID!, $calculationId: ID!) {
              calculationStats(workspaceId: $workspaceId, calculationId: $calculationId) {
                latestRevisionId
              }
            }
        """, {
            "workspaceId": WORKSPACE_ID,
            "calculationId": calc_id
        })

        if "data" in stats and stats["data"]["calculationStats"]:
            revision_id = stats["data"]["calculationStats"]["latestRevisionId"]
            print(f"  Found revisionId: {revision_id}")

            # Try with actual revision ID
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
                "calculationId": calc_id,
                "revisionId": revision_id
            })

            print("  [Result] with actual revisionId:")
            print(json.dumps(result2, indent=2))
    else:
        print("  [SUCCESS]:")
        print(json.dumps(result, indent=2))

print("\n" + "="*70)
print(" Creating NEW test to verify workflow")
print("="*70)

# Let's create a brand new page and calculation to test the complete flow
from nanoid import generate

page_id = generate()
print(f"\n[1] Creating page: {page_id}")

create_page = execute_query("""
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
        "title": "VERIFICATION TEST - Check RHS Panel",
        "workspaceId": WORKSPACE_ID
    }
})

print(json.dumps(create_page, indent=2))

# Add to tree
print("\n[2] Adding to tree...")
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
print("  [SUCCESS]")

# Create calculation
calc_id = generate()
stmt_id = generate()

print(f"\n[3] Creating calculation: {calc_id}")
print(f"    Statement ID: {stmt_id}")

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
        statements {
          statementId
          title
          formula
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "withStatements": [
        {
            "statementId": stmt_id,
            "title": "test_value",
            "formula": "42",
            "engine": "mathjs"
        }
    ],
    "data": {
        "pageId": page_id
    }
})

print(json.dumps(calc_result, indent=2))

# Verify we can query it back
print(f"\n[4] Verifying calculation exists...")

if "data" in calc_result and calc_result["data"]["createOrUpdateCalculation"]:
    returned_revision = calc_result["data"]["createOrUpdateCalculation"]["revisionId"]

    if returned_revision:
        verify = execute_query("""
            query GetCalc($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
              calculation(
                workspaceId: $workspaceId
                calculationId: $calculationId
                revisionId: $revisionId
              ) {
                calculationId
                statements {
                  statementId
                  title
                  formula
                }
              }
            }
        """, {
            "workspaceId": WORKSPACE_ID,
            "calculationId": calc_id,
            "revisionId": returned_revision
        })

        print(json.dumps(verify, indent=2))

print("\n" + "="*70)
print(" VERIFICATION PAGE CREATED")
print("="*70)
print(f"URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print(f"Calculation ID: {calc_id}")
print(f"Statement ID: {stmt_id}")
print("\nPlease check this page in CalcTree:")
print("  1. Does the page appear in the tree?")
print("  2. Does the calculation appear in the RHS statement list?")
print("  3. If not, what do you see?")
print("="*70)
