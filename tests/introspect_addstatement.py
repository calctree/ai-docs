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

# Get addStatementSync signature
result = execute_query("""
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
""")

if "data" in result:
    fields = result["data"]["__type"]["fields"]
    add_stmt_fields = [f for f in fields if "addStatement" in f["name"]]
    print("addStatement mutations:")
    print(json.dumps(add_stmt_fields, indent=2))
