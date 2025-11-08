#!/usr/bin/env python3
"""
Create a page with multiple multiline_mathjs blocks
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
print(" TEST: Multiple multiline_mathjs Blocks")
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
        "title": "TEST: Multiple Math Blocks",
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

# Create calculation with multiple multiline_mathjs blocks
print(f"\n[2] Creating calculation with 5 multiline_mathjs blocks...")

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
            "statementId": generate_nanoid(),
            "title": "Beam Dimensions",
            "engine": "multiline_mathjs",
            "formula": "length = 10 m\nwidth = 300 mm\nheight = 500 mm"
        },
        {
            "statementId": generate_nanoid(),
            "title": "Material Properties",
            "engine": "multiline_mathjs",
            "formula": "E = 200 GPa\nnu = 0.3\nrho = 7850 kg/m^3"
        },
        {
            "statementId": generate_nanoid(),
            "title": "Loading",
            "engine": "multiline_mathjs",
            "formula": "q = 10 kN/m\nP = 50 kN\nM = 100 kN*m"
        },
        {
            "statementId": generate_nanoid(),
            "title": "Section Properties",
            "engine": "multiline_mathjs",
            "formula": "A = width * height\nI = width * height^3 / 12\nW = I / (height/2)"
        },
        {
            "statementId": generate_nanoid(),
            "title": "Results",
            "engine": "multiline_mathjs",
            "formula": "sigma_max = M / W\ntau_max = P / A\ndeflection = 5 * q * length^4 / (384 * E * I)"
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate_nanoid(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

print(json.dumps(calc_result, indent=2))

# Query to verify
print(f"\n[3] Querying all statements...")

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
print("\nExpected: 5 multiline_mathjs blocks with engineering calculations")
print("="*70)
