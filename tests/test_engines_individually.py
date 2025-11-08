#!/usr/bin/env python3
"""
Test each engine type individually with createOrUpdateCalculation
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

def create_page_with_engine(engine_name, title, formula):
    """Create a page with one statement of the given engine type"""
    page_id = generate_nanoid()
    print(f"\n{'='*70}")
    print(f" Testing: {engine_name}")
    print(f"{'='*70}")
    print(f"Creating page: {page_id}")

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
            "title": f"TEST: {engine_name}",
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

    # Create calculation
    stmt_id = generate_nanoid()
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
        "calculationId": page_id,
        "withStatements": [
            {
                "statementId": stmt_id,
                "title": title,
                "engine": engine_name,
                "formula": formula
            }
        ],
        "data": {
            "pageId": page_id,
            "id": generate_nanoid(),
            "cursor": "0",
            "timestamp": int(time.time() * 1000)
        }
    })

    print(f"Mutation result: {json.dumps(calc_result, indent=2)}")

    # Query to verify
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
              formula
            }
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "revisionId": "ffffffff"
    })

    print(f"Query result: {json.dumps(query_result, indent=2)}")
    print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")

    return page_id

# Test each engine type
print("="*70)
print(" TESTING EACH ENGINE TYPE INDIVIDUALLY")
print("="*70)

# 1. mathjs (we know this works)
mathjs_page = create_page_with_engine(
    "mathjs",
    "beam_length",
    "10 m"
)

# 2. multiline_mathjs (correct name from network trace)
multiline_page = create_page_with_engine(
    "multiline_mathjs",
    "Multi-line Math",
    "width = 300 mm\nheight = 500 mm\narea = width * height"
)

# 3. python
python_page = create_page_with_engine(
    "python",
    "Python Calc",
    "import math\nresult = math.sqrt(16)\nprint(f'Square root: {result}')"
)

print("\n" + "="*70)
print(" SUMMARY")
print("="*70)
print(f"mathjs page: https://app.calctree.com/edit/{WORKSPACE_ID}/{mathjs_page}")
print(f"multiline_mathjs page: https://app.calctree.com/edit/{WORKSPACE_ID}/{multiline_page}")
print(f"python page: https://app.calctree.com/edit/{WORKSPACE_ID}/{python_page}")
print("="*70)
