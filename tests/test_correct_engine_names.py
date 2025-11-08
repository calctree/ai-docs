#!/usr/bin/env python3
"""
Test with CORRECT engine names from network trace
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

print("="*70)
print(" TEST: Correct Engine Names (multiline_mathjs)")
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
        "title": "TEST: Correct Engine Names",
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

print("[SUCCESS]")

# Now use createCalculation (not createOrUpdateCalculation) to add ONE statement at a time
# This matches your network trace

# Statement 1: mathjs
print(f"\n[2] Adding statement 1 (mathjs)...")
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
        "statementId": stmt_id_1
    }
})

print(json.dumps(result1, indent=2))

# Statement 2: multiline_mathjs (CORRECT NAME!)
print(f"\n[3] Adding statement 2 (multiline_mathjs)...")
stmt_id_2 = generate_nanoid()

# Get the revision from previous result
revision = result1.get("data", {}).get("createCalculation", {}).get("revisionId", "")

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
    "revisionId": revision if revision else "",
    "withStatement": {
        "statementId": stmt_id_2,
        "title": "Multi-line Math",
        "engine": "multiline_mathjs",  # CORRECT NAME!
        "formula": "width = 300 mm\nheight = 500 mm\narea = width * height"
    },
    "data": {
        "id": generate_nanoid(),
        "cursor": revision if revision else "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_2
    }
})

print(json.dumps(result2, indent=2))

# Statement 3: Python
print(f"\n[4] Adding statement 3 (python)...")
stmt_id_3 = generate_nanoid()

revision2 = result2.get("data", {}).get("addStatementToCalculation", {}).get("revisionId", revision)

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
    "revisionId": revision2 if revision2 else "",
    "withStatement": {
        "statementId": stmt_id_3,
        "title": "Python Calc",
        "engine": "python",
        "formula": "import math\nresult = math.sqrt(16)\nprint(f'Square root: {result}')"
    },
    "data": {
        "id": generate_nanoid(),
        "cursor": revision2 if revision2 else "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_3
    }
})

print(json.dumps(result3, indent=2))

# Query all statements
print(f"\n[5] Querying all statements...")

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

print(json.dumps(query_result, indent=2))

print("\n" + "="*70)
print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("\nExpected:")
print("  1. beam_length (mathjs)")
print("  2. Multi-line Math (multiline_mathjs)")
print("  3. Python Calc (python)")
print("\nCheck if all 3 appear in RHS panel!")
print("="*70)
