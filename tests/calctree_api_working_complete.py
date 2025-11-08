#!/usr/bin/env python3
"""
CalcTree API - Complete Working Example
Successfully creates a page with calculations using verified API calls
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def execute_query(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a GraphQL query"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=payload)
    return response.json()

def generate_nanoid() -> str:
    """Generate nanoid"""
    try:
        from nanoid import generate
        return generate()
    except ImportError:
        import random
        import string
        alphabet = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choices(alphabet, k=21))

def create_page_with_calculation():
    """
    COMPLETE WORKING EXAMPLE
    Creates a page and calculation with proper API calls
    """
    print("\n" + "="*70)
    print(" COMPLETE WORKING EXAMPLE: Create Page + Calculation ")
    print("="*70)

    # Step 1: Create a new page
    page_id = generate_nanoid()
    print(f"\n[Step 1] Creating page with ID: {page_id}")
    print("-" * 70)

    page_query = """
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
        title
      }
    }
    """

    page_variables = {
        "workspaceId": WORKSPACE_ID,
        "input": {
            "id": page_id,
            "title": "Structural Beam Analysis",
            "workspaceId": WORKSPACE_ID
        }
    }

    page_result = execute_query(page_query, page_variables)

    if "errors" in page_result:
        print("[ERROR] Failed to create page:")
        print(json.dumps(page_result["errors"], indent=2))
        return None

    print(f"[SUCCESS] Page created!")
    print(json.dumps(page_result["data"], indent=2))

    page_url = f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}"

    # Step 2: Create a calculation
    calc_id = generate_nanoid()
    statement_id = generate_nanoid()

    print(f"\n[Step 2] Creating calculation with ID: {calc_id}")
    print(f"         First statement ID: {statement_id}")
    print("-" * 70)

    calc_query = """
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
      ) {
        calculationId
        revisionId
      }
    }
    """

    calc_variables = {
        "workspaceId": WORKSPACE_ID,
        "calculationId": calc_id,
        "withStatement": {
            "statementId": statement_id,
            "title": "beam_length",
            "formula": "10 m",
            "engine": "mathjs"
        }
    }

    calc_result = execute_query(calc_query, calc_variables)

    if "errors" in calc_result:
        print("[ERROR] Failed to create calculation:")
        print(json.dumps(calc_result["errors"], indent=2))
    else:
        print(f"[SUCCESS] Calculation created!")
        print(json.dumps(calc_result["data"], indent=2))

        revision_id = calc_result["data"]["createCalculation"]["revisionId"]

        # Step 3: Add more statements to the calculation
        if revision_id:
            print(f"\n[Step 3] Adding more statements to calculation")
            print("-" * 70)

            statement_id_2 = generate_nanoid()

            add_stmt_query = """
            mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $input: CreateStatementInput!) {
              addStatementSync(
                workspaceId: $workspaceId
                calculationId: $calculationId
                revisionId: $revisionId
                input: $input
              ) {
                calculationId
                revisionId
                statement {
                  statementId
                  title
                  formula
                }
              }
            }
            """

            add_stmt_variables = {
                "workspaceId": WORKSPACE_ID,
                "calculationId": calc_id,
                "revisionId": revision_id,
                "input": {
                    "statementId": statement_id_2,
                    "title": "load",
                    "formula": "1000 N",
                    "engine": "mathjs"
                }
            }

            add_result = execute_query(add_stmt_query, add_stmt_variables)

            if "errors" in add_result:
                print("[ERROR] Failed to add statement:")
                print(json.dumps(add_result["errors"], indent=2))
            else:
                print(f"[SUCCESS] Statement added!")
                print(json.dumps(add_result["data"], indent=2))

                # Step 4: Add a calculated value
                statement_id_3 = generate_nanoid()
                new_revision = add_result["data"]["addStatementSync"]["revisionId"]

                if new_revision:
                    add_stmt_variables_3 = {
                        "workspaceId": WORKSPACE_ID,
                        "calculationId": calc_id,
                        "revisionId": new_revision,
                        "input": {
                            "statementId": statement_id_3,
                            "title": "moment",
                            "formula": "load * beam_length",
                            "engine": "mathjs"
                        }
                    }

                    add_result_3 = execute_query(add_stmt_query, add_stmt_variables_3)

                    if "errors" in add_result_3:
                        print("[ERROR] Failed to add calculated statement:")
                        print(json.dumps(add_result_3["errors"], indent=2))
                    else:
                        print(f"[SUCCESS] Calculated statement added!")
                        print(json.dumps(add_result_3["data"], indent=2))

    # Step 4: Add content to the page
    print(f"\n[Step 4] Adding markdown content to page")
    print("-" * 70)

    content_query = """
    mutation PutContent($workspaceId: ID!, $input: PutPageContentInput!) {
      putInitialPageContent(workspaceId: $workspaceId, input: $input)
    }
    """

    markdown_content = f"""# Structural Beam Analysis

This calculation determines the moment in a simply supported beam.

**Calculation ID:** {calc_id}

## Inputs
- Beam length
- Applied load

## Outputs
- Bending moment
"""

    content_variables = {
        "workspaceId": WORKSPACE_ID,
        "input": {
            "pageId": page_id,
            "content": markdown_content
        }
    }

    content_result = execute_query(content_query, content_variables)

    if "errors" in content_result:
        print("[ERROR] Failed to add content:")
        print(json.dumps(content_result["errors"], indent=2))
    else:
        print(f"[SUCCESS] Content added to page!")
        print(json.dumps(content_result["data"], indent=2))

    # Summary
    print("\n" + "="*70)
    print(" SUMMARY ")
    print("="*70)
    print(f"Page URL:         {page_url}")
    print(f"Page ID:          {page_id}")
    print(f"Calculation ID:   {calc_id}")
    print("="*70)

    return {
        "page_url": page_url,
        "page_id": page_id,
        "calc_id": calc_id
    }

if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# CalcTree API - Complete Working Example")
    print("#"*70)

    result = create_page_with_calculation()

    if result:
        print(f"\n\n[FINAL RESULT]")
        print(f"Visit your new page at:")
        print(f"  {result['page_url']}")

    print("\n" + "#"*70)
    print("# Done")
    print("#"*70 + "\n")
