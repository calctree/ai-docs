#!/usr/bin/env python3
"""
Debug why calculations aren't appearing on pages
"""

import requests
import json

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"
PAGE_ID = "LR1gjwmHpwijEWfgxs7Xi"  # The page that should have calculations

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
print(" Debugging Calculation Visibility")
print("="*70)

# Step 1: Check if the page exists and get its details
print(f"\n[1] Checking page {PAGE_ID}...")

page_query = execute_query("""
    query GetPage($workspaceId: ID!, $id: ID!) {
      page(workspaceId: $workspaceId, id: $id) {
        id
        title
        deletedAt
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "id": PAGE_ID
})

print(json.dumps(page_query, indent=2))

# Step 2: Try to get calculations for this page using pageContent query
print(f"\n[2] Checking page content...")

page_content = execute_query("""
    query GetPageContent($workspaceId: ID!, $pageId: ID!) {
      pageContent(workspaceId: $workspaceId, pageId: $pageId) {
        markdown
        calculations {
          id
          revisionId
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "pageId": PAGE_ID
})

print(json.dumps(page_content, indent=2))

# Step 3: Check what the Calculation query looks like
print(f"\n[3] Introspecting Calculation query...")

introspect = execute_query("""
    query {
      __schema {
        queryType {
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
    }
""")

if "data" in introspect:
    fields = introspect["data"]["__schema"]["queryType"]["fields"]
    calc_queries = [f for f in fields if "calculation" in f["name"].lower()]
    print("Calculation-related queries:")
    print(json.dumps(calc_queries[:5], indent=2))

# Step 4: Try querying a specific calculation we created
# (Use one of the calculation IDs from create_working_demo_page.py output)
print(f"\n[4] Testing different ways to link calculations to pages...")

# Create a NEW test page
test_page_id = generate_nanoid()
print(f"\nCreating test page: {test_page_id}")

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
        "id": test_page_id,
        "title": "DEBUG Test Page",
        "workspaceId": WORKSPACE_ID
    }
})

print(json.dumps(create_page, indent=2))

# Add to tree
execute_query("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) {
        newPageId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {"pageId": test_page_id}
})

print("Added to tree")

# Method 1: Create calculation WITH data.pageId
print(f"\n[5] Method 1: Creating calc with data.pageId...")
calc_id_1 = generate_nanoid()

method1 = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
        data: $data
      ) {
        calculationId
        revisionId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id_1,
    "withStatement": {
        "statementId": generate_nanoid(),
        "title": "test1",
        "formula": "42",
        "engine": "mathjs"
    },
    "data": {
        "pageId": test_page_id
    }
})

print(json.dumps(method1, indent=2))

# Now check if it appears on the page
print(f"\n[6] Checking if calculation appears on page...")

check_content = execute_query("""
    query GetPageContent($workspaceId: ID!, $pageId: ID!) {
      pageContent(workspaceId: $workspaceId, pageId: $pageId) {
        markdown
        calculations {
          id
          revisionId
        }
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "pageId": test_page_id
})

print(json.dumps(check_content, indent=2))

# Method 2: Check if there's a mutation to link calculation to page
print(f"\n[7] Looking for mutations to link calculations to pages...")

mutation_introspect = execute_query("""
    query {
      __type(name: "Mutation") {
        fields {
          name
        }
      }
    }
""")

if "data" in mutation_introspect:
    all_mutations = [f["name"] for f in mutation_introspect["data"]["__type"]["fields"]]
    link_mutations = [m for m in all_mutations if "link" in m.lower() or ("calculation" in m.lower() and "page" in m.lower())]
    print("Possible linking mutations:")
    print(json.dumps(link_mutations, indent=2))

print("\n" + "="*70)
print(f"Test page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{test_page_id}")
print("="*70)
