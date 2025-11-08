#!/usr/bin/env python3
"""
Create a demo page with calculations properly linked via data.pageId
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

def create_calculation_on_page(workspace_id, page_id, calc_id, stmt_id, title, formula, engine):
    """Create a calculation linked to a page"""
    result = execute_query("""
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
        "workspaceId": workspace_id,
        "calculationId": calc_id,
        "withStatement": {
            "statementId": stmt_id,
            "title": title,
            "formula": formula,
            "engine": engine
        },
        "data": {
            "pageId": page_id
        }
    })
    return result

def add_statement(workspace_id, calc_id, stmt_id, title, formula, engine):
    """Add a statement to a calculation"""
    result = execute_query("""
        mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!) {
          addStatementToCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            revisionId: $revisionId
            withStatement: $withStatement
          ) {
            calculationId
          }
        }
    """, {
        "workspaceId": workspace_id,
        "calculationId": calc_id,
        "revisionId": "ffffffff",
        "withStatement": {
            "statementId": stmt_id,
            "title": title,
            "formula": formula,
            "engine": engine
        }
    })
    return result

print("="*70)
print(" Creating Demo Page with All Calculation Types")
print("="*70)

# Step 1: Create page
page_id = generate_nanoid()
print(f"\n[1] Creating page: {page_id}")

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
        "title": "CalcTree API Demo - Multi-Engine Calculations",
        "workspaceId": WORKSPACE_ID
    }
})

if "errors" in create_result:
    print("[ERROR]", json.dumps(create_result["errors"], indent=2))
    exit(1)

print("[SUCCESS] Page created")

# Step 2: Add to tree
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

print("[SUCCESS] Added to page tree")

# Step 3: Create calculations with different engines
print("\n[2] Creating MathJS calculation (basic inputs)...")
calc_1 = generate_nanoid()
create_calculation_on_page(WORKSPACE_ID, page_id, calc_1, generate_nanoid(), "beam_length", "10 m", "mathjs")
add_statement(WORKSPACE_ID, calc_1, generate_nanoid(), "load", "5000 N", "mathjs")
add_statement(WORKSPACE_ID, calc_1, generate_nanoid(), "moment", "load * beam_length", "mathjs")
print("[SUCCESS] MathJS calculation created")

print("\n[3] Creating Multi-MathJS calculation...")
calc_2 = generate_nanoid()
multi_mathjs_formula = """width = 300 mm
height = 500 mm
area = width * height
perimeter = 2 * (width + height)"""
create_calculation_on_page(WORKSPACE_ID, page_id, calc_2, generate_nanoid(), "section_props", multi_mathjs_formula, "multi-mathjs")
print("[SUCCESS] Multi-MathJS calculation created")

print("\n[4] Creating Math-Block calculation...")
calc_3 = generate_nanoid()
mathblock_formula = """E = 200000 MPa
I = 50000000 mm^4
L = 6 m
deflection = (5 * load * L^3) / (384 * E * I)"""
create_calculation_on_page(WORKSPACE_ID, page_id, calc_3, generate_nanoid(), "deflection_calc", mathblock_formula, "math-block")
print("[SUCCESS] Math-Block calculation created")

print("\n[5] Creating Python calculation...")
calc_4 = generate_nanoid()
python_formula = """import math

# Beam section properties
width = 300  # mm
height = 500  # mm

# Calculate section modulus
I = (width * height**3) / 12
c = height / 2
section_modulus = I / c

print(f"Moment of Inertia: {I:,.0f} mm^4")
print(f"Section Modulus: {section_modulus:,.0f} mm^3")"""
create_calculation_on_page(WORKSPACE_ID, page_id, calc_4, generate_nanoid(), "python_beam_calc", python_formula, "python")
print("[SUCCESS] Python calculation created")

print("\n[6] Creating Python calculation with NumPy...")
calc_5 = generate_nanoid()
numpy_formula = """import numpy as np

# Multiple load cases
loads = np.array([1000, 2000, 1500, 1800])  # N
distances = np.array([1, 2, 3, 4])  # m

moments = loads * distances
total_moment = np.sum(moments)
max_moment = np.max(moments)

print(f"Individual moments: {moments} N.m")
print(f"Total moment: {total_moment} N.m")
print(f"Maximum moment: {max_moment} N.m")"""
create_calculation_on_page(WORKSPACE_ID, page_id, calc_5, generate_nanoid(), "numpy_load_analysis", numpy_formula, "python")
print("[SUCCESS] NumPy calculation created")

print("\n[7] Creating design check calculation...")
calc_6 = generate_nanoid()
create_calculation_on_page(WORKSPACE_ID, page_id, calc_6, generate_nanoid(), "material_strength", "350 MPa", "mathjs")
add_statement(WORKSPACE_ID, calc_6, generate_nanoid(), "safety_factor", "1.5", "mathjs")
add_statement(WORKSPACE_ID, calc_6, generate_nanoid(), "allowable_stress", "material_strength / safety_factor", "mathjs")
print("[SUCCESS] Design check calculation created")

print("\n" + "="*70)
print(" SUCCESS! Demo Page Created")
print("="*70)
print(f"\nPage URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("\nThis page demonstrates:")
print("  - MathJS: Simple calculations with units")
print("  - Multi-MathJS: Multiple lines in one block")
print("  - Math-Block: Advanced mathematical formulas")
print("  - Python: Custom calculations with print statements")
print("  - Python + NumPy: Array-based calculations")
print("  - Combined: Calculations referencing other variables")
print("\nCalculation IDs created:")
print(f"  MathJS:        {calc_1}")
print(f"  Multi-MathJS:  {calc_2}")
print(f"  Math-Block:    {calc_3}")
print(f"  Python:        {calc_4}")
print(f"  NumPy:         {calc_5}")
print(f"  Design Check:  {calc_6}")
print("="*70)
