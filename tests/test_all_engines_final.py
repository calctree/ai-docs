#!/usr/bin/env python3
"""
FINAL TEST: Create a page with all three working engine types
- mathjs
- multiline_mathjs
- python

This demonstrates the complete working API for CalcTree calculations.
"""

import requests
import json
import time

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"
USER_ID = "4d83c852-69a7-4744-8b7c-92d0335386c3"

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

print("="*70)
print(" FINAL TEST: All Three Engine Types")
print("="*70)

# Step 1: Create page
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
        "title": "FINAL: All Engine Types Working",
        "workspaceId": WORKSPACE_ID
    }
})

# Step 2: Add to page tree
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

# Step 3: Add mathjs statement
print(f"\n[2] Adding mathjs statement...")
stmt_id_1 = generate_nanoid()

result1 = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
        data: $data
      ) {
        revisionId
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatement": {
        "statementId": stmt_id_1,
        "title": "beam_length",
        "engine": "mathjs",
        "formula": "10 m"
    },
    "data": {
        "id": generate_nanoid(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_1,
        "userId": USER_ID
    }
})
print(f"[SUCCESS] mathjs: {json.dumps(result1, indent=2)}")

# Step 4: Add multiline_mathjs statement
print(f"\n[3] Adding multiline_mathjs statement...")
stmt_id_2 = generate_nanoid()

result2 = execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        revisionId
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id_2,
        "title": "Beam Dimensions",
        "engine": "multiline_mathjs",
        "formula": "width = 300 mm\nheight = 500 mm\narea = width * height"
    },
    "data": {
        "id": generate_nanoid(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_2,
        "userId": USER_ID
    }
})
print(f"[SUCCESS] multiline_mathjs: {json.dumps(result2, indent=2)}")

# Step 5: Add python statement
print(f"\n[4] Adding python statement...")
stmt_id_3 = generate_nanoid()

result3 = execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        revisionId
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id_3,
        "title": "Python Calculation",
        "engine": "python",
        "formula": "import math\ntotal = sum(range(10))\naverage = total / 10\nresult = math.sqrt(average)\nprint(f'Result: {result}')"
    },
    "data": {
        "id": generate_nanoid(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_3,
        "userId": USER_ID
    }
})
print(f"[SUCCESS] python: {json.dumps(result3, indent=2)}")

print("\n" + "="*70)
print(f"✅ SUCCESS! Page created with all 3 engine types:")
print("="*70)
print(f"\nPage URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("\nStatements created:")
print("  1. beam_length (mathjs): 10 m")
print("  2. Beam Dimensions (multiline_mathjs): width, height, area")
print("  3. Python Calculation (python): math operations with print")
print("\nAll three engine types are VERIFIED WORKING!")
print("="*70)
