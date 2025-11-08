#!/usr/bin/env python3
"""
CalcTree API Reference Implementation

This script demonstrates the correct way to interact with the CalcTree GraphQL API
to create pages and calculations.

Requirements:
    pip install nanoid requests

Usage:
    python calctree_api_reference.py

Author: Tested and verified 2025-11-08
"""

import requests
from typing import Dict, Any, Optional

# Configuration - replace with your values
WORKSPACE_ID = "your-workspace-id-here"
API_KEY = "your-api-key-here"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"

# API request headers
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def execute_graphql(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a GraphQL query against the CalcTree API

    Args:
        query: GraphQL query string
        variables: Optional variables dictionary

    Returns:
        API response as dictionary
    """
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=payload)
    return response.json()

def generate_id() -> str:
    """
    Generate a nanoid for use as page/calculation/statement ID

    CalcTree requires nanoid format (21 characters: alphanumeric + underscore/hyphen)
    """
    try:
        from nanoid import generate
        return generate()
    except ImportError:
        print("ERROR: nanoid library not found. Install with: pip install nanoid")
        import random
        import string
        # Fallback generator (not recommended for production)
        alphabet = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choices(alphabet, k=21))

def create_page(workspace_id: str, title: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new page in CalcTree

    Args:
        workspace_id: The workspace ID
        title: Page title
        parent_id: Optional parent page ID for hierarchy

    Returns:
        API response containing page id and title
    """
    page_id = generate_id()

    query = """
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
        title
      }
    }
    """

    variables = {
        "workspaceId": workspace_id,
        "input": {
            "id": page_id,
            "title": title,
            "workspaceId": workspace_id
        }
    }

    if parent_id:
        variables["input"]["parentId"] = parent_id

    result = execute_graphql(query, variables)

    if "errors" in result:
        print(f"ERROR creating page: {result['errors']}")
        return None

    return {
        "page_id": page_id,
        "title": title,
        "url": f"https://app.calctree.com/edit/{workspace_id}/{page_id}",
        "response": result
    }

def create_calculation(workspace_id: str, title: str, formula: str) -> Dict[str, Any]:
    """
    Create a new calculation with a single statement

    Args:
        workspace_id: The workspace ID
        title: Variable name for the statement
        formula: Formula string (e.g., "10 m" or "x + y")

    Returns:
        API response containing calculation id
    """
    calc_id = generate_id()
    statement_id = generate_id()

    query = """
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

    variables = {
        "workspaceId": workspace_id,
        "calculationId": calc_id,
        "withStatement": {
            "statementId": statement_id,
            "title": title,
            "formula": formula,
            "engine": "mathjs"
        }
    }

    result = execute_graphql(query, variables)

    if "errors" in result:
        print(f"ERROR creating calculation: {result['errors']}")
        return None

    return {
        "calculation_id": calc_id,
        "statement_id": statement_id,
        "response": result
    }

def add_statement(workspace_id: str, calculation_id: str, title: str, formula: str) -> Dict[str, Any]:
    """
    Add a statement to an existing calculation

    Args:
        workspace_id: The workspace ID
        calculation_id: The calculation ID to add to
        title: Variable name for the statement
        formula: Formula string (e.g., "10 m" or "x + y")

    Returns:
        API response

    Note:
        Always use revisionId="ffffffff" when adding statements
    """
    statement_id = generate_id()

    query = """
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
      ) {
        calculationId
        revisionId
      }
    }
    """

    variables = {
        "workspaceId": workspace_id,
        "calculationId": calculation_id,
        "revisionId": "ffffffff",  # CRITICAL: Always use "ffffffff"
        "withStatement": {
            "statementId": statement_id,
            "title": title,
            "formula": formula,
            "engine": "mathjs"
        }
    }

    result = execute_graphql(query, variables)

    if "errors" in result:
        print(f"ERROR adding statement: {result['errors']}")
        return None

    return {
        "statement_id": statement_id,
        "response": result
    }

def create_beam_analysis_example():
    """
    Complete example: Create a page with a beam analysis calculation
    """
    print("="*70)
    print(" CalcTree API Reference Example: Beam Analysis")
    print("="*70)

    # Step 1: Create page
    print("\n[1] Creating page...")
    page_result = create_page(
        workspace_id=WORKSPACE_ID,
        title="Simple Beam Analysis - API Example"
    )

    if not page_result:
        return

    print(f"    ✓ Page created: {page_result['page_id']}")
    print(f"    ✓ URL: {page_result['url']}")

    # Step 2: Create calculation with first statement
    print("\n[2] Creating calculation with load statement...")
    calc_result = create_calculation(
        workspace_id=WORKSPACE_ID,
        title="load",
        formula="1000 N"
    )

    if not calc_result:
        return

    print(f"    ✓ Calculation created: {calc_result['calculation_id']}")

    # Step 3: Add beam length
    print("\n[3] Adding beam length statement...")
    add_result_1 = add_statement(
        workspace_id=WORKSPACE_ID,
        calculation_id=calc_result['calculation_id'],
        title="beam_length",
        formula="5 m"
    )

    if add_result_1:
        print(f"    ✓ Statement added: {add_result_1['statement_id']}")

    # Step 4: Add calculated moment
    print("\n[4] Adding calculated moment...")
    add_result_2 = add_statement(
        workspace_id=WORKSPACE_ID,
        calculation_id=calc_result['calculation_id'],
        title="moment",
        formula="load * beam_length"
    )

    if add_result_2:
        print(f"    ✓ Statement added: {add_result_2['statement_id']}")

    # Summary
    print("\n" + "="*70)
    print(" Summary")
    print("="*70)
    print(f"Page URL:        {page_result['url']}")
    print(f"Page ID:         {page_result['page_id']}")
    print(f"Calculation ID:  {calc_result['calculation_id']}")
    print("="*70)
    print("\nOpen the page URL in your browser to view the calculation!")

if __name__ == "__main__":
    # Check configuration
    if WORKSPACE_ID == "your-workspace-id-here" or API_KEY == "your-api-key-here":
        print("ERROR: Please update WORKSPACE_ID and API_KEY in the script")
        exit(1)

    # Check nanoid is installed
    try:
        import nanoid
        print("✓ nanoid library is installed")
    except ImportError:
        print("⚠ WARNING: nanoid library not found")
        print("  Install with: pip install nanoid")
        print("  Using fallback ID generator (not recommended for production)")

    # Run example
    create_beam_analysis_example()
