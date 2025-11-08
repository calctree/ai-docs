#!/usr/bin/env python3
"""
Test alternative calculation creation methods
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
print(" Testing Alternative Calculation Creation Methods")
print("="*70)

# Create a test page
page_id = generate_nanoid()
print(f"\n[1] Creating test page: {page_id}")

create_page = execute_query("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {
        "id": page_id,
        "title": "Test Alternative Methods",
        "workspaceId": WORKSPACE_ID
    }
})

# Add to tree
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

print("[SUCCESS] Page created and added to tree")

# Method 1: createOrUpdateCalculation
print(f"\n[2] Method 1: createOrUpdateCalculation...")
calc_id_1 = generate_nanoid()

method1 = execute_query("""
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
    "calculationId": calc_id_1,
    "withStatements": [
        {
            "statementId": generate_nanoid(),
            "title": "method1_test",
            "formula": "100",
            "engine": "mathjs"
        }
    ],
    "data": {
        "pageId": page_id
    }
})

print(json.dumps(method1, indent=2))

# Method 2: createCalculationWithMultipleStatements (async)
print(f"\n[3] Method 2: createCalculationWithMultipleStatements...")
calc_id_2 = generate_nanoid()

method2 = execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createCalculationWithMultipleStatements(
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
    "calculationId": calc_id_2,
    "withStatements": [
        {
            "statementId": generate_nanoid(),
            "title": "method2_test",
            "formula": "200",
            "engine": "mathjs"
        },
        {
            "statementId": generate_nanoid(),
            "title": "method2_test2",
            "formula": "300",
            "engine": "mathjs"
        }
    ],
    "data": {
        "pageId": page_id
    }
})

print(json.dumps(method2, indent=2))

# Check pageContent with correct field
print(f"\n[4] Checking page content (correct field name)...")

page_content = execute_query("""
    query GetPageContent($workspaceId: ID!, $pageId: ID!) {
      pageContent(workspaceId: $workspaceId, pageId: $pageId) {
        pageId
        version
        content
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "pageId": page_id
})

print(json.dumps(page_content, indent=2))

# Try to query individual calculations
print(f"\n[5] Querying individual calculation...")

# We need a revisionId - let's try "ffffffff" or "0"
calc_query = execute_query("""
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
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id_1,
    "revisionId": "ffffffff"
})

print("Calculation query result:")
print(json.dumps(calc_query, indent=2))

print("\n" + "="*70)
print(f"Test page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print(f"Calc ID 1: {calc_id_1}")
print(f"Calc ID 2: {calc_id_2}")
print("="*70)
