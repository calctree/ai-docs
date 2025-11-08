#!/usr/bin/env python3
"""
Test how to properly link calculations to a page
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
print(" Testing Page-Calculation Linking")
print("="*70)

# Check if there's a pageId parameter in createCalculation
print("\n[1] Introspecting createCalculation mutation...")

introspect = execute_query("""
    query {
      __type(name: "Mutation") {
        fields {
          name
          args {
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
    }
""")

if "data" in introspect:
    fields = introspect["data"]["__type"]["fields"]
    create_calc = [f for f in fields if f["name"] == "createCalculation"]
    print(json.dumps(create_calc, indent=2))

# Check CreateStatementInput to see if it has pageId
print("\n[2] Checking CreateStatementInput for pageId field...")

stmt_input = execute_query("""
    query {
      __type(name: "CreateStatementInput") {
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

print(json.dumps(stmt_input, indent=2))

# Look for mutations that might link calculations to pages
print("\n[3] Looking for page content or linking mutations...")

if "data" in introspect:
    fields = introspect["data"]["__type"]["fields"]
    content_mutations = [f for f in fields if "content" in f["name"].lower() or "link" in f["name"].lower()]
    print(json.dumps(content_mutations[:5], indent=2))

# Try creating a calculation WITH pageId in the data field
print("\n[4] Testing createCalculation with data.pageId...")

page_id = generate_nanoid()

# Create page
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
        "title": "Test Page with Linked Calculation",
        "workspaceId": WORKSPACE_ID
    }
})

print("Page created:", create_page.get("data", {}).get("createPageSync", {}).get("id"))

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

print("Added to tree")

# Create calculation with data field containing pageId
calc_id = generate_nanoid()

calc_with_data = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "withStatement": {
        "statementId": generate_nanoid(),
        "title": "test_value",
        "formula": "42",
        "engine": "mathjs"
    },
    "data": {
        "pageId": page_id
    }
})

print("\nCalculation with data.pageId result:")
print(json.dumps(calc_with_data, indent=2))

print(f"\nPage URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("Check if calculation appears on the page!")
