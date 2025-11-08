#!/usr/bin/env python3
"""
Test each engine type separately
"""

import requests
import json
import time

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
    from nanoid import generate
    return generate()

def create_page_with_statements(title, statements):
    """Helper to create page and add statements"""
    page_id = generate_nanoid()

    # Create page
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
            "title": title,
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

    # Create calculation
    result = execute_query("""
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
        "withStatements": statements,
        "data": {
            "pageId": page_id,
            "id": generate_nanoid(),
            "cursor": "0",
            "timestamp": int(time.time() * 1000)
        }
    })

    # Query back
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
            }
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "revisionId": "ffffffff"
    })

    return page_id, result, query_result

print("="*70)
print(" Testing Engine Types Separately")
print("="*70)

# Test 1: Multi-MathJS only
print("\n[1] Testing Multi-MathJS only...")
multi_mathjs_statements = [
    {
        "statementId": generate_nanoid(),
        "title": "section_calc",
        "engine": "multi-mathjs",
        "formula": "width = 300 mm\nheight = 500 mm\narea = width * height"
    },
    {
        "statementId": generate_nanoid(),
        "title": "loads",
        "engine": "multi-mathjs",
        "formula": "dead_load = 2.5 kN\nlive_load = 3.0 kN\ntotal = dead_load + live_load"
    }
]

page1, create1, query1 = create_page_with_statements("TEST: Multi-MathJS Only", multi_mathjs_statements)

print(f"  Page: {page1}")
print(f"  Creation result:", "SUCCESS" if "data" in create1 else "ERROR")
if "data" in query1 and query1["data"]["calculation"]:
    print(f"  Query result: {len(query1['data']['calculation']['statements'])} statements")
    for stmt in query1['data']['calculation']['statements']:
        print(f"    - [{stmt['engine']}] {stmt['title']}")
else:
    print(f"  Query result: ERROR or null")

# Test 2: Python only
print("\n[2] Testing Python only...")
python_statements = [
    {
        "statementId": generate_nanoid(),
        "title": "python_simple",
        "engine": "python",
        "formula": "import math\nresult = math.sqrt(16)\nprint(f'Result: {result}')"
    },
    {
        "statementId": generate_nanoid(),
        "title": "python_numpy",
        "engine": "python",
        "formula": "import numpy as np\nforces = np.array([1000, 2000, 1500])\nmax_force = np.max(forces)\nprint(f'Max force: {max_force} N')"
    }
]

page2, create2, query2 = create_page_with_statements("TEST: Python Only", python_statements)

print(f"  Page: {page2}")
print(f"  Creation result:", "SUCCESS" if "data" in create2 else "ERROR")
if "data" in query2 and query2["data"]["calculation"]:
    print(f"  Query result: {len(query2['data']['calculation']['statements'])} statements")
    for stmt in query2['data']['calculation']['statements']:
        print(f"    - [{stmt['engine']}] {stmt['title']}")
else:
    print(f"  Query result: ERROR or null")

# Test 3: Math-block only
print("\n[3] Testing Math-block only...")
mathblock_statements = [
    {
        "statementId": generate_nanoid(),
        "title": "mathblock_calc",
        "engine": "math-block",
        "formula": "x = 5\ny = 10\nz = x^2 + y^2"
    }
]

page3, create3, query3 = create_page_with_statements("TEST: Math-Block Only", mathblock_statements)

print(f"  Page: {page3}")
print(f"  Creation result:", "SUCCESS" if "data" in create3 else "ERROR")
if "data" in query3 and query3["data"]["calculation"]:
    print(f"  Query result: {len(query3['data']['calculation']['statements'])} statements")
    for stmt in query3['data']['calculation']['statements']:
        print(f"    - [{stmt['engine']}] {stmt['title']}")
else:
    print(f"  Query result: ERROR or null")

print("\n" + "="*70)
print(" RESULTS")
print("="*70)
print(f"Multi-MathJS: https://app.calctree.com/edit/{WORKSPACE_ID}/{page1}")
print(f"Python:       https://app.calctree.com/edit/{WORKSPACE_ID}/{page2}")
print(f"Math-Block:   https://app.calctree.com/edit/{WORKSPACE_ID}/{page3}")
print("\nPlease check which pages show statements in the RHS panel!")
print("="*70)
