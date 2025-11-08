#!/usr/bin/env python3
"""
Test: Create page with ALL engine types (mathjs, multi-mathjs, python)
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
print(" TEST: All Engine Types (mathjs, multi-mathjs, python)")
print("="*70)

# Create page
page_id = generate_nanoid()
print(f"\n[1] Creating page: {page_id}")

execute_query("""
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
        "title": "Complete Demo - All Engine Types",
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

# Create calculation with mixed engine types
print(f"\n[2] Creating calculation with multiple engine types...")

statements = [
    # MathJS statements (single variable)
    {
        "statementId": generate_nanoid(),
        "title": "beam_length",
        "engine": "mathjs",
        "formula": "beam_length = 10 m"
    },
    {
        "statementId": generate_nanoid(),
        "title": "load",
        "engine": "mathjs",
        "formula": "load = 5000 N"
    },
    {
        "statementId": generate_nanoid(),
        "title": "moment",
        "engine": "mathjs",
        "formula": "moment = load * beam_length"
    },
    # Multi-MathJS (multiple lines in one statement)
    {
        "statementId": generate_nanoid(),
        "title": "section_properties",
        "engine": "multi-mathjs",
        "formula": "width = 300 mm\nheight = 500 mm\narea = width * height\nperimeter = 2 * (width + height)"
    },
    # Another Multi-MathJS
    {
        "statementId": generate_nanoid(),
        "title": "load_factors",
        "engine": "multi-mathjs",
        "formula": "dead_load = 2.5 kN\nlive_load = 3.0 kN\ntotal_load = dead_load + live_load"
    },
    # Python statement
    {
        "statementId": generate_nanoid(),
        "title": "python_calc",
        "engine": "python",
        "formula": "import math\n\n# Calculate section modulus\nwidth = 300  # mm\nheight = 500  # mm\n\nI = (width * height**3) / 12\nc = height / 2\nsection_modulus = I / c\n\nprint(f'Section Modulus: {section_modulus:.2f} mm^3')"
    },
    # Python with NumPy
    {
        "statementId": generate_nanoid(),
        "title": "stress_analysis",
        "engine": "python",
        "formula": "import numpy as np\n\n# Stress analysis\nforces = np.array([1000, 2000, 1500, 1800])  # N\nareas = np.array([100, 150, 120, 130])  # mm^2\n\nstresses = forces / areas\nmax_stress = np.max(stresses)\navg_stress = np.mean(stresses)\n\nprint(f'Max stress: {max_stress:.2f} MPa')\nprint(f'Avg stress: {avg_stress:.2f} MPa')"
    },
    # Final MathJS for design check
    {
        "statementId": generate_nanoid(),
        "title": "design_check",
        "engine": "mathjs",
        "formula": "design_check = moment / 1000"
    }
]

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
    "withStatements": statements,
    "data": {
        "pageId": page_id,
        "id": generate_nanoid(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

print(json.dumps(calc_result, indent=2))

# Query back to verify
print(f"\n[3] Verifying all statements created...")

query_result = execute_query("""
    query GetCalc($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
      calculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
      ) {
        statements {
          statementId
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

if "data" in query_result and query_result["data"]["calculation"]:
    statements_returned = query_result["data"]["calculation"]["statements"]
    print(f"\n[SUCCESS] Created {len(statements_returned)} statements:\n")

    for i, stmt in enumerate(statements_returned, 1):
        formula_preview = stmt['formula'][:50] + "..." if len(stmt['formula']) > 50 else stmt['formula']
        print(f"  {i}. [{stmt['engine']}] {stmt['title']}: {formula_preview}")

print("\n" + "="*70)
print(" COMPLETE DEMO PAGE CREATED")
print("="*70)
print(f"URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("\nThis page contains:")
print("  - 3 MathJS statements (single variable)")
print("  - 2 Multi-MathJS statements (multiple variables per block)")
print("  - 2 Python statements (including NumPy)")
print("\nCheck if all statements appear and execute correctly in the RHS panel!")
print("="*70)
