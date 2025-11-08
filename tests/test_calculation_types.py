#!/usr/bin/env python3
"""
Test different calculation types: mathjs, math-block, python
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
print(" Testing Different Calculation Types")
print("="*70)

# First, let's introspect to see what engines are available
print("\n[1] Checking available engine types...")

# Create a page first
page_id = generate_nanoid()
print(f"\n[2] Creating page: {page_id}")

create_result = execute_query("""
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
        "title": "Multi-Engine Calculation Test",
        "workspaceId": WORKSPACE_ID
    }
})

if "errors" in create_result:
    print("[ERROR]", json.dumps(create_result["errors"], indent=2))
    exit(1)

print("[SUCCESS] Page created")

# Add to tree
add_tree = execute_query("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) {
        newPageId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {"pageId": page_id}
})

print("[SUCCESS] Added to tree")

# Test 1: Try mathjs engine (we know this works)
print("\n[3] Creating calculation with mathjs engine...")
calc_id_1 = generate_nanoid()

mathjs_result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id_1,
    "withStatement": {
        "statementId": generate_nanoid(),
        "title": "mathjs_test",
        "formula": "10 m",
        "engine": "mathjs"
    }
})

print(json.dumps(mathjs_result, indent=2))

# Test 2: Try "math-block" engine
print("\n[4] Testing 'math-block' engine...")
calc_id_2 = generate_nanoid()

mathblock_result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id_2,
    "withStatement": {
        "statementId": generate_nanoid(),
        "title": "math_block_test",
        "formula": "x = 5\\ny = 10\\nresult = x + y",
        "engine": "math-block"
    }
})

print(json.dumps(mathblock_result, indent=2))

# Test 3: Try "multi-mathjs" engine
print("\n[5] Testing 'multi-mathjs' engine...")
calc_id_3 = generate_nanoid()

multimathjs_result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id_3,
    "withStatement": {
        "statementId": generate_nanoid(),
        "title": "multi_mathjs_test",
        "formula": "a = 2\\nb = 3\\nc = a * b",
        "engine": "multi-mathjs"
    }
})

print(json.dumps(multimathjs_result, indent=2))

# Test 4: Try "python" engine
print("\n[6] Testing 'python' engine...")
calc_id_4 = generate_nanoid()

python_result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id_4,
    "withStatement": {
        "statementId": generate_nanoid(),
        "title": "python_test",
        "formula": "import math\\nresult = math.sqrt(16)",
        "engine": "python"
    }
})

print(json.dumps(python_result, indent=2))

# Test 5: Try "python3" engine
print("\n[7] Testing 'python3' engine...")
calc_id_5 = generate_nanoid()

python3_result = execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id_5,
    "withStatement": {
        "statementId": generate_nanoid(),
        "title": "python3_test",
        "formula": "value = 42",
        "engine": "python3"
    }
})

print(json.dumps(python3_result, indent=2))

print("\n" + "="*70)
print(" Summary")
print("="*70)
print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("\nCheck which engines worked by visiting the page!")
print("="*70)
