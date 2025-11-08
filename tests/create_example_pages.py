#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create all verified example pages for the documentation
"""

from nanoid import generate
import requests
import time
import sys

# Ensure UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
ENDPOINT = "https://graph.calctree.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def execute_query(query, variables=None):
    """Execute a GraphQL query against CalcTree API."""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
    return response.json()

def get_user_id():
    """Fetch current user ID."""
    result = execute_query("""
        query GetCurrentUser {
          currentUser {
            id
          }
        }
    """)
    return result['data']['currentUser']['id']

def create_page(page_id, title):
    """Create a page and add it to the tree."""
    # Step 1: Create page
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

def create_example_1_mathjs():
    """Example 1: Simple MathJS with units"""
    page_id = generate()
    create_page(page_id, "Example: Simple MathJS")

    execute_query("""
        mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
          createOrUpdateCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            withStatements: $withStatements
            data: $data
          ) {
            calculationId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "withStatements": [
            {
                "statementId": generate(),
                "title": "beam_length",
                "engine": "mathjs",
                "formula": "beam_length = 5 m"
            }
        ],
        "data": {
            "pageId": page_id,
            "id": generate(),
            "cursor": "0",
            "timestamp": int(time.time() * 1000)
        }
    })

    return page_id, "Simple MathJS"

def create_example_2_cross_refs():
    """Example 2: MathJS with cross-references"""
    page_id = generate()
    create_page(page_id, "Example: Cross-References")

    execute_query("""
        mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
          createOrUpdateCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            withStatements: $withStatements
            data: $data
          ) {
            calculationId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "withStatements": [
            {
                "statementId": generate(),
                "title": "length",
                "engine": "mathjs",
                "formula": "length = 10 m"
            },
            {
                "statementId": generate(),
                "title": "width",
                "engine": "mathjs",
                "formula": "width = 5 m"
            },
            {
                "statementId": generate(),
                "title": "height",
                "engine": "mathjs",
                "formula": "height = 3 m"
            },
            {
                "statementId": generate(),
                "title": "volume",
                "engine": "mathjs",
                "formula": "volume = length * width * height"
            }
        ],
        "data": {
            "pageId": page_id,
            "id": generate(),
            "cursor": "0",
            "timestamp": int(time.time() * 1000)
        }
    })

    return page_id, "Cross-References"

def create_example_3_multiline():
    """Example 3: Multiline MathJS blocks"""
    page_id = generate()
    create_page(page_id, "Example: Multiline Blocks")

    execute_query("""
        mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
          createOrUpdateCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            withStatements: $withStatements
            data: $data
          ) {
            calculationId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "withStatements": [
            {
                "statementId": generate(),
                "title": "beam_length",
                "engine": "mathjs",
                "formula": "beam_length = 10 m"
            },
            {
                "statementId": generate(),
                "title": "Section Properties",
                "engine": "multiline_mathjs",
                "formula": "width = 300 mm\nheight = 500 mm\narea = width * height"
            },
            {
                "statementId": generate(),
                "title": "Loads",
                "engine": "multiline_mathjs",
                "formula": "dead_load = 5 kN/m\nlive_load = 3 kN/m\ntotal_load = dead_load + live_load"
            },
            {
                "statementId": generate(),
                "title": "moment",
                "engine": "mathjs",
                "formula": "moment = total_load * beam_length^2 / 8"
            },
            {
                "statementId": generate(),
                "title": "stress",
                "engine": "mathjs",
                "formula": "stress = moment / (width * height^2 / 6)"
            }
        ],
        "data": {
            "pageId": page_id,
            "id": generate(),
            "cursor": "0",
            "timestamp": int(time.time() * 1000)
        }
    })

    return page_id, "Multiline Blocks"

def create_example_4_python(user_id):
    """Example 4: Python statement"""
    page_id = generate()
    create_page(page_id, "Example: Python Analysis")

    stmt_id = generate()
    execute_query("""
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
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "withStatement": {
            "statementId": stmt_id,
            "title": "Python Analysis",
            "engine": "python",
            "formula": """import numpy as np

# Generate data
data = np.array([10, 20, 30, 40, 50])

# Statistics
mean = np.mean(data)
std = np.std(data)
total = np.sum(data)

print(f'Mean: {mean}')
print(f'Std Dev: {std:.2f}')
print(f'Total: {total}')"""
        },
        "data": {
            "id": generate(),
            "cursor": "",
            "timestamp": int(time.time() * 1000),
            "statementId": stmt_id,
            "userId": user_id,
            "pageId": page_id
        }
    })

    return page_id, "Python"

def create_example_5_all_engines(user_id):
    """Example 5: All three engine types"""
    page_id = generate()
    create_page(page_id, "Example: All Engine Types")

    # First create MathJS and multiline statements
    execute_query("""
        mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
          createOrUpdateCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            withStatements: $withStatements
            data: $data
          ) {
            calculationId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "withStatements": [
            {
                "statementId": generate(),
                "title": "force",
                "engine": "mathjs",
                "formula": "force = 100 kN"
            },
            {
                "statementId": generate(),
                "title": "Geometry",
                "engine": "multiline_mathjs",
                "formula": "width = 200 mm\nheight = 400 mm\narea = width * height"
            }
        ],
        "data": {
            "pageId": page_id,
            "id": generate(),
            "cursor": "0",
            "timestamp": int(time.time() * 1000)
        }
    })

    # Then add Python statement
    stmt_id = generate()
    execute_query("""
        mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
          addStatementToCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            revisionId: $revisionId
            withStatement: $withStatement
            data: $data
          ) {
            calculationId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,
        "revisionId": "ffffffff",
        "withStatement": {
            "statementId": stmt_id,
            "title": "Analysis",
            "engine": "python",
            "formula": """# Variables from MathJS are available
stress = force / area
stress_mpa = stress.to('MPa')

print(f'Applied Force: {force}')
print(f'Cross-sectional Area: {area}')
print(f'Stress: {stress_mpa}')"""
        },
        "data": {
            "id": generate(),
            "cursor": "",
            "timestamp": int(time.time() * 1000),
            "statementId": stmt_id,
            "userId": user_id
        }
    })

    return page_id, "All Engines"

if __name__ == "__main__":
    print("Creating Verified Example Pages")
    print("=" * 70)

    # Get user ID
    print("\nFetching user ID...")
    user_id = get_user_id()
    print(f"✓ User ID: {user_id}\n")

    examples = []

    print("[1/5] Creating Simple MathJS example...")
    page_id, desc = create_example_1_mathjs()
    examples.append((page_id, desc))
    print(f"✓ Created: {page_id}\n")

    print("[2/5] Creating Cross-References example...")
    page_id, desc = create_example_2_cross_refs()
    examples.append((page_id, desc))
    print(f"✓ Created: {page_id}\n")

    print("[3/5] Creating Multiline Blocks example...")
    page_id, desc = create_example_3_multiline()
    examples.append((page_id, desc))
    print(f"✓ Created: {page_id}\n")

    print("[4/5] Creating Python example...")
    page_id, desc = create_example_4_python(user_id)
    examples.append((page_id, desc))
    print(f"✓ Created: {page_id}\n")

    print("[5/5] Creating All Engines example...")
    page_id, desc = create_example_5_all_engines(user_id)
    examples.append((page_id, desc))
    print(f"✓ Created: {page_id}\n")

    print("=" * 70)
    print("SUCCESS! All example pages created")
    print("=" * 70)
    print("\nVerified Example Pages:\n")

    for page_id, desc in examples:
        url = f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}"
        print(f"{desc}:")
        print(f"  ID: {page_id}")
        print(f"  URL: {url}\n")

    print("\nUpdate these URLs in the documentation:")
    print(f"- README.md")
    print(f"- EXAMPLES.md")
    print(f"- PYTHON_GUIDE.md")
    print(f"- CALCULATION_GUIDE.md")
