#!/usr/bin/env python3
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

# Introspect PageTreeCorrelation
result = execute_query("""
    query {
      __type(name: "PageTreeCorrelation") {
        name
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

print("PageTreeCorrelation fields:")
print(json.dumps(result, indent=2))
