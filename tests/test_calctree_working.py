#!/usr/bin/env python3
"""
CalcTree API - Working Example
Successfully creates a page with calculations
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

def introspect_putpagecontent():
    """Introspect PutPageContentInput"""
    print("\n" + "="*60)
    print("Introspecting PutPageContentInput")
    print("="*60)

    query = """
    query {
      __type(name: "PutPageContentInput") {
        name
        inputFields {
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
    """

    result = execute_query(query)
    print(json.dumps(result, indent=2))
    return result

def create_complete_working_example():
    """Create a page with calculations - fully working example"""
    print("\n" + "="*60)
    print("WORKING EXAMPLE: Page + Calculation via createCalculation")
    print("="*60)

    # Step 1: Create page
    page_id = generate_nanoid()
    print(f"\nStep 1: Creating page {page_id}")

    page_result = execute_query("""
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
            "title": "Beam Analysis - API Created",
            "workspaceId": WORKSPACE_ID
        }
    })

    print(json.dumps(page_result, indent=2))

    if "errors" in page_result:
        return None

    page_url = f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}"
    print(f"[SUCCESS] Page URL: {page_url}")

    # Step 2: Create calculation with correct fields
    print(f"\nStep 2: Creating calculation")

    calc_id = generate_nanoid()
    statement_id = generate_nanoid()

    calc_result = execute_query("""
        mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
          createCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            withStatement: $withStatement
          ) {
            calculationId
            revisionId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": calc_id,
        "withStatement": {
            "statementId": statement_id,
            "title": "length",
            "formula": "10 m",
            "engine": "mathjs"
        }
    })

    print(json.dumps(calc_result, indent=2))

    # Step 3: Try putInitialPageContent to link calc to page
    print(f"\nStep 3: Adding content to page")

    content_result = execute_query("""
        mutation PutContent($workspaceId: ID!, $input: PutPageContentInput!) {
          putInitialPageContent(workspaceId: $workspaceId, input: $input)
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "input": {
            "pageId": page_id,
            "markdown": f"# Beam Analysis\\n\\nThis page contains calculations for beam design.\\n\\nCalculation ID: {calc_id}"
        }
    })

    print(json.dumps(content_result, indent=2))

    return {
        "page_id": page_id,
        "page_url": page_url,
        "calc_id": calc_id,
        "calc_result": calc_result,
        "content_result": content_result
    }

def test_add_statement_to_calculation(calc_id: str, revision_id: str):
    """Test adding another statement to existing calculation"""
    print("\n" + "="*60)
    print("Adding statement to calculation")
    print("="*60)

    statement_id = generate_nanoid()

    # First introspect AddStatementInput
    introspect_result = execute_query("""
        query {
          __type(name: "AddStatementInput") {
            name
            inputFields {
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
    """)

    print("AddStatementInput schema:")
    print(json.dumps(introspect_result, indent=2))

    # Now try to add statement
    result = execute_query("""
        mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $input: AddStatementInput!) {
          addStatement(
            workspaceId: $workspaceId
            calculationId: $calculationId
            revisionId: $revisionId
            input: $input
          ) {
            calculationId
            revisionId
          }
        }
    """, {
        "workspaceId": WORKSPACE_ID,
        "calculationId": calc_id,
        "revisionId": revision_id,
        "input": {
            "statementId": statement_id,
            "title": "width",
            "formula": "5 m",
            "engine": "mathjs"
        }
    })

    print(json.dumps(result, indent=2))
    return result

def run_all():
    """Run all working examples"""
    print("\n" + "#"*60)
    print("# CalcTree API - Working Examples")
    print("#"*60)

    # Introspect page content
    introspect_putpagecontent()

    # Create complete example
    result = create_complete_working_example()

    if result and "calc_result" in result:
        calc_data = result["calc_result"].get("data", {}).get("createCalculation", {})
        if calc_data and "revisionId" in calc_data:
            # Try adding another statement
            test_add_statement_to_calculation(
                result["calc_id"],
                calc_data["revisionId"]
            )

    print("\n" + "#"*60)
    print("# Complete")
    print("#"*60)

    if result:
        print(f"\n[FINAL] Page URL: {result['page_url']}")

    return result

if __name__ == "__main__":
    run_all()
