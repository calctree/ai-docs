#!/usr/bin/env python3
"""
CalcTree API Testing Script
Tests various API endpoints and documents working vs non-working features
"""

import requests
import json
from typing import Dict, Any, Optional

# Configuration
WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"

# Headers for all requests
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def execute_query(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a GraphQL query and return the response"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=payload)
    return response.json()

def generate_nanoid() -> str:
    """Generate a nanoid-style ID (21 chars, alphanumeric + underscore/hyphen)"""
    try:
        from nanoid import generate
        return generate()
    except ImportError:
        # Fallback to a simple implementation if nanoid not installed
        import random
        import string
        alphabet = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choices(alphabet, k=21))

def test_current_user():
    """Test 1: Get current user information"""
    print("\n" + "="*60)
    print("TEST 1: Get Current User")
    print("="*60)

    query = """
    query GetCurrentUser {
      currentUser {
        id
        email
        fullName
        workspaces {
          id
          name
          role
        }
      }
    }
    """

    result = execute_query(query)
    print(json.dumps(result, indent=2))
    return result

def test_get_pages():
    """Test 2: Get all pages in workspace"""
    print("\n" + "="*60)
    print("TEST 2: Get All Pages in Workspace")
    print("="*60)

    query = """
    query GetPages($workspaceId: ID!) {
      pages(workspaceId: $workspaceId) {
        id
        title
        parentId
        createdAt
        updatedAt
      }
    }
    """

    result = execute_query(query, {"workspaceId": WORKSPACE_ID})
    print(json.dumps(result, indent=2))
    return result

def test_create_page_without_id():
    """Test 3: Create page WITHOUT providing an ID (let API generate it)"""
    print("\n" + "="*60)
    print("TEST 3: Create Page Without ID")
    print("="*60)

    query = """
    mutation CreatePage($workspaceId: ID!, $page: PageInput!) {
      createPageSync(workspaceId: $workspaceId, page: $page) {
        id
        title
      }
    }
    """

    variables = {
        "workspaceId": WORKSPACE_ID,
        "page": {
            "title": "API Test Page (No ID)"
        }
    }

    result = execute_query(query, variables)
    print(json.dumps(result, indent=2))
    return result

def test_create_page_with_nanoid():
    """Test 4: Create page WITH nanoid"""
    print("\n" + "="*60)
    print("TEST 4: Create Page With Nanoid")
    print("="*60)

    page_id = generate_nanoid()
    print(f"Generated page ID: {page_id}")

    query = """
    mutation CreatePage($workspaceId: ID!, $page: PageInput!) {
      createPageSync(workspaceId: $workspaceId, page: $page) {
        id
        title
      }
    }
    """

    variables = {
        "workspaceId": WORKSPACE_ID,
        "page": {
            "id": page_id,
            "title": "API Test Page (With Nanoid)"
        }
    }

    result = execute_query(query, variables)
    print(json.dumps(result, indent=2))

    if "data" in result and result["data"]["createPageSync"]:
        page_id = result["data"]["createPageSync"]["id"]
        page_url = f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}"
        print(f"\n[SUCCESS] Page URL: {page_url}")
        return {"result": result, "page_id": page_id}

    return {"result": result, "page_id": None}

def test_create_calculation_single_statement(page_id: str):
    """Test 5: Create calculation with single statement"""
    print("\n" + "="*60)
    print("TEST 5: Create Calculation - Single Statement")
    print("="*60)

    query = """
    mutation CreateCalculation($workspaceId: ID!, $pageId: ID!, $statements: [StatementInput!]!) {
      createCalculationWithMultipleStatementsSync(
        workspaceId: $workspaceId
        pageId: $pageId
        statements: $statements
      ) {
        id
        revisionId
        statements {
          id
          title
          formula
          value
          unit
          error
        }
      }
    }
    """

    variables = {
        "workspaceId": WORKSPACE_ID,
        "pageId": page_id,
        "statements": [
            {"title": "length", "formula": "10", "unit": "m"}
        ]
    }

    result = execute_query(query, variables)
    print(json.dumps(result, indent=2))
    return result

def test_create_calculation_multiple_statements(page_id: str):
    """Test 6: Create calculation with multiple statements"""
    print("\n" + "="*60)
    print("TEST 6: Create Calculation - Multiple Statements")
    print("="*60)

    query = """
    mutation CreateCalculation($workspaceId: ID!, $pageId: ID!, $statements: [StatementInput!]!) {
      createCalculationWithMultipleStatementsSync(
        workspaceId: $workspaceId
        pageId: $pageId
        statements: $statements
      ) {
        id
        revisionId
        statements {
          id
          title
          formula
          value
          unit
          error
        }
      }
    }
    """

    variables = {
        "workspaceId": WORKSPACE_ID,
        "pageId": page_id,
        "statements": [
            {"title": "load", "formula": "1000", "unit": "N"},
            {"title": "length", "formula": "5", "unit": "m"},
            {"title": "moment", "formula": "load * length", "unit": "N*m"}
        ]
    }

    result = execute_query(query, variables)
    print(json.dumps(result, indent=2))
    return result

def test_create_calculation_alternate_mutation(page_id: str):
    """Test 7: Try createCalculation mutation (without Sync suffix)"""
    print("\n" + "="*60)
    print("TEST 7: Create Calculation - Alternate Mutation (createCalculation)")
    print("="*60)

    query = """
    mutation CreateCalculation($workspaceId: ID!, $pageId: ID!, $statement: StatementInput!) {
      createCalculation(
        workspaceId: $workspaceId
        pageId: $pageId
        statement: $statement
      ) {
        correlationId
      }
    }
    """

    variables = {
        "workspaceId": WORKSPACE_ID,
        "pageId": page_id,
        "statement": {
            "title": "test_value",
            "formula": "42",
            "unit": "mm"
        }
    }

    result = execute_query(query, variables)
    print(json.dumps(result, indent=2))
    return result

def test_introspection_page_input():
    """Test 8: Introspect PageInput type to see available fields"""
    print("\n" + "="*60)
    print("TEST 8: Introspection - PageInput Type")
    print("="*60)

    query = """
    query IntrospectPageInput {
      __type(name: "PageInput") {
        name
        kind
        inputFields {
          name
          type {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
      }
    }
    """

    result = execute_query(query)
    print(json.dumps(result, indent=2))
    return result

def test_introspection_statement_input():
    """Test 9: Introspect StatementInput type"""
    print("\n" + "="*60)
    print("TEST 9: Introspection - StatementInput Type")
    print("="*60)

    query = """
    query IntrospectStatementInput {
      __type(name: "StatementInput") {
        name
        kind
        inputFields {
          name
          type {
            name
            kind
            ofType {
              name
              kind
            }
          }
        }
      }
    }
    """

    result = execute_query(query)
    print(json.dumps(result, indent=2))
    return result

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "#"*60)
    print("# CalcTree API Testing Suite")
    print("#"*60)

    # Test 1: Current user
    test_current_user()

    # Test 2: Get pages
    test_get_pages()

    # Test 3: Introspection
    test_introspection_page_input()
    test_introspection_statement_input()

    # Test 4: Create page without ID
    test_create_page_without_id()

    # Test 5: Create page with nanoid
    page_result = test_create_page_with_nanoid()

    if page_result["page_id"]:
        # Test 6: Single statement calculation
        test_create_calculation_single_statement(page_result["page_id"])

        # Test 7: Multiple statement calculation
        test_create_calculation_multiple_statements(page_result["page_id"])

        # Test 8: Alternate mutation
        test_create_calculation_alternate_mutation(page_result["page_id"])

    print("\n" + "#"*60)
    print("# Testing Complete")
    print("#"*60)

if __name__ == "__main__":
    # Check if nanoid is installed
    try:
        import nanoid
        print("[OK] nanoid library is installed")
    except ImportError:
        print("[WARNING] nanoid library not installed, using fallback ID generator")
        print("  Install with: pip install nanoid")

    run_all_tests()
