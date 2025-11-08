#!/usr/bin/env python3
"""
Create a comprehensive demo page with all calculation types
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

def create_calculation(workspace_id, calc_id, stmt_id, title, formula, engine):
    """Create a calculation"""
    result = execute_query("""
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
        "workspaceId": workspace_id,
        "calculationId": calc_id,
        "withStatement": {
            "statementId": stmt_id,
            "title": title,
            "formula": formula,
            "engine": engine
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
print(" Creating Comprehensive Demo Page")
print("="*70)

# Create page
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
        "title": "CalcTree API Demo - All Calculation Types",
        "workspaceId": WORKSPACE_ID
    }
})

print("[SUCCESS] Page created")

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

print("[SUCCESS] Added to tree")

# CALCULATION 1: Simple mathjs calculations
print("\n[2] Creating mathjs calculation (simple values with units)...")
calc_1 = generate_nanoid()
create_calculation(WORKSPACE_ID, calc_1, generate_nanoid(), "beam_length", "10 m", "mathjs")
add_statement(WORKSPACE_ID, calc_1, generate_nanoid(), "load", "5000 N", "mathjs")
add_statement(WORKSPACE_ID, calc_1, generate_nanoid(), "moment", "load * beam_length", "mathjs")
print("[SUCCESS] Created mathjs calculation")

# CALCULATION 2: Multi-mathjs (multiple statements in one block)
print("\n[3] Creating multi-mathjs calculation...")
calc_2 = generate_nanoid()
multi_mathjs_formula = """width = 300 mm
height = 500 mm
area = width * height
perimeter = 2 * (width + height)"""
create_calculation(WORKSPACE_ID, calc_2, generate_nanoid(), "section_properties", multi_mathjs_formula, "multi-mathjs")
print("[SUCCESS] Created multi-mathjs calculation")

# CALCULATION 3: Math-block
print("\n[4] Creating math-block calculation...")
calc_3 = generate_nanoid()
mathblock_formula = """E = 200000 MPa
I = 50000000 mm^4
L = 6 m
deflection = (5 * load * L^3) / (384 * E * I)"""
create_calculation(WORKSPACE_ID, calc_3, generate_nanoid(), "beam_deflection", mathblock_formula, "math-block")
print("[SUCCESS] Created math-block calculation")

# CALCULATION 4: Python calculation
print("\n[5] Creating python calculation...")
calc_4 = generate_nanoid()
python_formula = """import math

# Calculate section modulus
width = 300  # mm
height = 500  # mm

I = (width * height**3) / 12
c = height / 2
section_modulus = I / c

print(f"Section Modulus: {section_modulus:.2f} mm^3")"""
create_calculation(WORKSPACE_ID, calc_4, generate_nanoid(), "python_section_calc", python_formula, "python")
print("[SUCCESS] Created python calculation")

# CALCULATION 5: Another python with imports
print("\n[6] Creating advanced python calculation...")
calc_5 = generate_nanoid()
python_advanced = """import numpy as np

# Stress analysis
forces = np.array([1000, 2000, 1500])  # N
areas = np.array([100, 150, 120])  # mm^2

stresses = forces / areas  # MPa
max_stress = np.max(stresses)
avg_stress = np.mean(stresses)

result = {
    'max_stress': max_stress,
    'avg_stress': avg_stress,
    'forces': forces.tolist()
}"""
create_calculation(WORKSPACE_ID, calc_5, generate_nanoid(), "stress_analysis", python_advanced, "python")
print("[SUCCESS] Created advanced python calculation")

# CALCULATION 6: Combined calculation using results from others
print("\n[7] Creating combined mathjs calculation...")
calc_6 = generate_nanoid()
create_calculation(WORKSPACE_ID, calc_6, generate_nanoid(), "factor_of_safety", "2.5", "mathjs")
add_statement(WORKSPACE_ID, calc_6, generate_nanoid(), "allowable_stress", "250 MPa", "mathjs")
add_statement(WORKSPACE_ID, calc_6, generate_nanoid(), "design_stress", "allowable_stress / factor_of_safety", "mathjs")
print("[SUCCESS] Created combined calculation")

print("\n" + "="*70)
print(" Demo Page Created Successfully!")
print("="*70)
print(f"\nPage URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
print("\nThis page contains:")
print("  ✓ MathJS calculations (simple statements)")
print("  ✓ Multi-MathJS calculations (multiple statements in one block)")
print("  ✓ Math-block calculations")
print("  ✓ Python calculations (simple)")
print("  ✓ Python calculations (with NumPy)")
print("  ✓ Combined calculations")
print("\nOpen the URL to see all calculation types in action!")
print("="*70)
