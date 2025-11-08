#!/usr/bin/env python3
"""
Introspect PageContent type to see available fields
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

def execute_query(query):
    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json={"query": query})
    return response.json()

# Introspect PageContent
print("="*70)
print("PageContent Type Fields:")
print("="*70)

result = execute_query("""
    query {
      __type(name: "PageContent") {
        name
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
""")

print(json.dumps(result, indent=2))

# Also check for calculation-related mutations
print("\n" + "="*70)
print("All Calculation Mutations:")
print("="*70)

mutations = execute_query("""
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
""")

if "data" in mutations:
    calc_mutations = [f for f in mutations["data"]["__type"]["fields"] if "calculation" in f["name"].lower()]
    print(json.dumps(calc_mutations[:10], indent=2))

# Check Page type for any calculation-related fields
print("\n" + "="*70)
print("Page Type Fields:")
print("="*70)

page_type = execute_query("""
    query {
      __type(name: "Page") {
        fields {
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

print(json.dumps(page_type, indent=2))
