#!/usr/bin/env python3
"""
CalcTree API Testing Script - Final Working Version
Demonstrates working API calls based on actual schema
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
    """Execute a GraphQL query and return the response"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=payload)
    return response.json()

def generate_nanoid() -> str:
    """Generate a nanoid-style ID"""
    try:
        from nanoid import generate
        return generate()
    except ImportError:
        import random
        import string
        alphabet = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choices(alphabet, k=21))

def introspect_createstatement_input():
    """Find out what CreateStatementInput looks like"""
    print("\n" + "="*60)
    print("Introspecting CreateStatementInput")
    print("="*60)

    query = """
    query {
      __type(name: "CreateStatementInput") {
        name
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

def introspect_createcalculation_mutation():
    """Find the exact signature of createCalculation"""
    print("\n" + "="*60)
    print("Introspecting createCalculation mutation")
    print("="*60)

    query = """
    query {
      __type(name: "Mutation") {
        fields {
          name
          args {
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
    }
    """

    result = execute_query(query)

    # Filter for createCalculation
    if "data" in result:
        fields = result["data"]["__type"]["fields"]
        calc_fields = [f for f in fields if f["name"] == "createCalculation"]
        print(json.dumps(calc_fields, indent=2))

    return result

def create_page_and_calculation():
    """Complete working example: create page and add calculation"""
    print("\n" + "="*60)
    print("COMPLETE WORKING EXAMPLE")
    print("="*60)

    # Step 1: Create a page
    page_id = generate_nanoid()
    print(f"\n1. Creating page with ID: {page_id}")

    create_page_query = """
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
            "title": "Engineering Calculation Example",
            "workspaceId": WORKSPACE_ID
        }
    }

    page_result = execute_query(create_page_query, page_variables)
    print(json.dumps(page_result, indent=2))

    if "errors" in page_result:
        print("\n[ERROR] Failed to create page")
        return None

    page_url = f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}"
    print(f"\n[SUCCESS] Page created: {page_url}")

    # Step 2: Try to create a calculation
    print(f"\n2. Attempting to create calculation...")

    calc_id = generate_nanoid()
    statement_id = generate_nanoid()

    # Based on introspection, the mutation needs calculationId and withStatement
    create_calc_query = """
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
            "pageId": page_id,
            "formula": "length = 10 m"
        }
    }

    calc_result = execute_query(create_calc_query, calc_variables)
    print(json.dumps(calc_result, indent=2))

    return {
        "page_id": page_id,
        "page_url": page_url,
        "calc_result": calc_result
    }

def test_page_content_mutation():
    """Test putting content on a page"""
    print("\n" + "="*60)
    print("Testing Page Content Mutation")
    print("="*60)

    # First introspect to find the right mutation
    query = """
    query {
      __type(name: "Mutation") {
        fields {
          name
          args {
            name
            type {
              name
              kind
              ofType {
                name
              }
            }
          }
        }
      }
    }
    """

    result = execute_query(query)

    if "data" in result:
        fields = result["data"]["__type"]["fields"]
        content_mutations = [f for f in fields if "content" in f["name"].lower() and "page" in f["name"].lower()]
        print(json.dumps(content_mutations, indent=2))

    return result

def run_comprehensive_test():
    """Run comprehensive API testing"""
    print("\n" + "#"*60)
    print("# CalcTree API - Comprehensive Test")
    print("#"*60)

    # Introspection
    introspect_createstatement_input()
    introspect_createcalculation_mutation()

    # Working example
    result = create_page_and_calculation()

    # Test page content
    test_page_content_mutation()

    print("\n" + "#"*60)
    print("# Test Complete")
    print("#"*60)

    return result

if __name__ == "__main__":
    run_comprehensive_test()
