#!/usr/bin/env python3
"""
Test adding calculations to page content
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
print(" Testing Page Content with Calculations")
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
        "title": "Test Page Content",
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

print("[SUCCESS] Page created")

# Create calculation
calc_id = generate_nanoid()
stmt_id = generate_nanoid()

print(f"\n[2] Creating calculation: {calc_id}")

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

# Try putInitialPageContent with markdown that references the calculation
print(f"\n[3] Adding page content with calculation reference...")

# Check PutPageContentInput schema
introspect = execute_query("""
    query {
      __type(name: "PutPageContentInput") {
        inputFields {
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

print("PutPageContentInput fields:")
print(json.dumps(introspect, indent=2))

# Try different content formats
print(f"\n[4] Attempting putInitialPageContent...")

# Attempt 1: Simple content
content_result1 = execute_query("""
    mutation PutContent($workspaceId: ID!, $input: PutPageContentInput!) {
      putInitialPageContent(workspaceId: $workspaceId, input: $input)
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {
        "pageId": page_id,
        "content": f"# Test Page\\n\\nCalculation ID: {calc_id}"
    }
})

print("Attempt 1 - Simple content:")
print(json.dumps(content_result1, indent=2))

# Check if there's a different way to get page content
print(f"\n[5] Checking page content...")

check_content = execute_query("""
    query GetPageContent($workspaceId: ID!, $pageId: ID!) {
      pageContent(workspaceId: $workspaceId, pageId: $pageId) {
        pageId
        content
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "pageId": page_id
})

print(json.dumps(check_content, indent=2))

print("\n" + "="*70)
print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print(f"Calculation ID: {calc_id}")
print("="*70)
print("\nPlease check if calculations appear on the page!")
