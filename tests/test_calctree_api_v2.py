#!/usr/bin/env python3
"""
CalcTree API Testing Script - Version 2
Updated based on actual API schema discovery
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
        import random
        import string
        alphabet = string.ascii_letters + string.digits + '_-'
        return ''.join(random.choices(alphabet, k=21))

def test_introspect_createpageinput():
    """Introspect CreatePageInput type"""
    print("\n" + "="*60)
    print("TEST: Introspection - CreatePageInput Type")
    print("="*60)

    query = """
    query IntrospectCreatePageInput {
      __type(name: "CreatePageInput") {
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

def test_introspect_mutations():
    """Introspect available mutation fields"""
    print("\n" + "="*60)
    print("TEST: Introspection - Mutation Type")
    print("="*60)

    query = """
    query IntrospectMutations {
      __schema {
        mutationType {
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
    }
    """

    result = execute_query(query)

    # Filter for page-related mutations
    if "data" in result and result["data"]["__schema"]["mutationType"]:
        mutations = result["data"]["__schema"]["mutationType"]["fields"]
        page_mutations = [m for m in mutations if "page" in m["name"].lower()]
        print(json.dumps(page_mutations, indent=2))

    return result

def test_introspect_page_type():
    """Introspect Page type fields"""
    print("\n" + "="*60)
    print("TEST: Introspection - Page Type")
    print("="*60)

    query = """
    query IntrospectPage {
      __type(name: "Page") {
        name
        kind
        fields {
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

def test_create_page_corrected():
    """Create page with correct mutation format"""
    print("\n" + "="*60)
    print("TEST: Create Page - Corrected Format")
    print("="*60)

    page_id = generate_nanoid()
    print(f"Generated page ID: {page_id}")

    query = """
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
        title
      }
    }
    """

    variables = {
        "workspaceId": WORKSPACE_ID,
        "input": {
            "id": page_id,
            "title": "API Test Page - Corrected",
            "workspaceId": WORKSPACE_ID
        }
    }

    result = execute_query(query, variables)
    print(json.dumps(result, indent=2))

    if "data" in result and result.get("data", {}).get("createPageSync"):
        page_id = result["data"]["createPageSync"]["id"]
        page_url = f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}"
        print(f"\n[SUCCESS] Page created!")
        print(f"Page URL: {page_url}")
        return {"result": result, "page_id": page_id}

    return {"result": result, "page_id": None}

def test_get_pages_corrected():
    """Get pages with correct field names"""
    print("\n" + "="*60)
    print("TEST: Get Pages - Corrected Fields")
    print("="*60)

    query = """
    query GetPages($workspaceId: ID!) {
      pages(workspaceId: $workspaceId) {
        id
        title
        deletedAt
      }
    }
    """

    result = execute_query(query, {"workspaceId": WORKSPACE_ID})
    print(json.dumps(result, indent=2))
    return result

def test_introspect_statement_mutations():
    """Find correct mutation for creating calculations"""
    print("\n" + "="*60)
    print("TEST: Find Calculation/Statement Mutations")
    print("="*60)

    query = """
    query IntrospectMutations {
      __schema {
        mutationType {
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
    }
    """

    result = execute_query(query)

    if "data" in result and result["data"]["__schema"]["mutationType"]:
        mutations = result["data"]["__schema"]["mutationType"]["fields"]
        calc_mutations = [m for m in mutations if "calculation" in m["name"].lower() or "statement" in m["name"].lower()]
        print(json.dumps(calc_mutations, indent=2))

    return result

def test_create_calculation_v2(page_id: str):
    """Try creating calculation with different approach"""
    print("\n" + "="*60)
    print("TEST: Create Calculation - Attempt 2")
    print("="*60)

    statement_id = generate_nanoid()

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
            "statementId": statement_id,
            "formula": "length = 10 m"
        }
    }

    result = execute_query(query, variables)
    print(json.dumps(result, indent=2))
    return result

def test_introspect_query_fields():
    """Check what query fields are available"""
    print("\n" + "="*60)
    print("TEST: Available Query Fields")
    print("="*60)

    query = """
    query IntrospectQueries {
      __schema {
        queryType {
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
    }
    """

    result = execute_query(query)

    if "data" in result and result["data"]["__schema"]["queryType"]:
        queries = result["data"]["__schema"]["queryType"]["fields"]
        # Filter for useful queries
        useful = [q for q in queries if any(keyword in q["name"].lower() for keyword in ["page", "calculation", "workspace", "user"])]
        print(json.dumps(useful, indent=2))

    return result

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "#"*60)
    print("# CalcTree API Testing Suite - Version 2")
    print("#"*60)

    # Introspection tests first
    test_introspect_page_type()
    test_introspect_createpageinput()
    test_introspect_mutations()
    test_introspect_query_fields()
    test_introspect_statement_mutations()

    # Get existing pages
    test_get_pages_corrected()

    # Create a new page
    page_result = test_create_page_corrected()

    if page_result["page_id"]:
        # Try to create calculations
        test_create_calculation_v2(page_result["page_id"])

    print("\n" + "#"*60)
    print("# Testing Complete")
    print("#"*60)

if __name__ == "__main__":
    run_all_tests()
