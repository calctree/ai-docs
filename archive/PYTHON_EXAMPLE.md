# Python Engine - Complete Working Example

## ✅ VERIFIED WORKING

The python engine is fully supported and working. The key requirement is including `userId` in the `data` field.

### Working Python Page

https://app.calctree.com/edit/98ea9cce-909a-44e9-9359-be53c3d67d04/8Pv7LKZMHWRqOVwAuoeQi

### Complete Python Example

```python
from nanoid import generate
import requests
import time

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "your-api-key"
USER_ID = "your-user-id"  # Get from your network trace when manually creating a python block
GRAPHQL_ENDPOINT = "https://graph.calctree.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def execute_query(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(GRAPHQL_ENDPOINT, headers=HEADERS, json=payload)
    return response.json()

# Step 1: Create page
page_id = generate()
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
        "title": "Python Calculations",
        "workspaceId": WORKSPACE_ID
    }
})

# Step 2: Add to page tree (REQUIRED!)
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

# Step 3: Add Python statement with userId in data
stmt_id = generate()
data_id = generate()

execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
        data: $data
      ) {
        revisionId
        calculationId
        __typename
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,  # Use page_id as calculationId
    "withStatement": {
        "statementId": stmt_id,
        "title": "Python Code",
        "engine": "python",
        "formula": "# Python test\ntotal = sum(range(5))\nprint(f'Total: {total}')"
    },
    "data": {
        "id": data_id,
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id,
        "userId": USER_ID  # CRITICAL for python engine
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

## Key Differences for Python Engine

1. **Must include `userId` in `data` field** - This is required for python statements
2. **Use `createCalculation` (singular)** - Works better than `createOrUpdateCalculation` for python
3. **Include `__typename` in response** - Matches the UI's network trace format
4. **Set `cursor: ""`** - Empty string for initial statement

## Supported Python Libraries

CalcTree provides a comprehensive Python environment with these pre-installed libraries:

### Core Scientific Computing
- **numpy** - Numerical computing and arrays
- **scipy** - Scientific computing and optimization
- **pandas** - Data analysis and manipulation
- **matplotlib** - Plotting and visualization
- **seaborn** - Statistical data visualization
- **SymPy** - Symbolic mathematics
- **Scikit-learn** - Machine learning

### Engineering & Structural Analysis
- **anaStruct** - Structural analysis
- **OpenSeesPy + OpsVis** - Finite element analysis
- **PyNite** - Structural analysis
- **pyFrame3DD** - 3D frame analysis
- **pycba** - Continuous beam analysis
- **sectionproperties** - Cross-section properties
- **StructPy** - Structural engineering
- **pyCalculiX** - Finite element analysis
- **eurocodepy** - Eurocode calculations

### Specialized Engineering
- **Groundhog** - Geotechnical engineering
- **GemPy** - 3D geological modeling
- **REDi** - Resilience assessment
- **energy-py-linear** - Energy optimization

### Utilities & Tools
- **handcalcs** - Show calculation steps
- **ezdxf** - DXF file handling
- **SimPy** - Discrete event simulation
- **pysal** - Spatial analysis
- **joypy** - Ridgeline plots
- **topojson** - Topology handling

### Standard Library
- **math** - Mathematical functions
- All Python 3 standard library modules

### Example with NumPy:
```python
{
    "statementId": generate(),
    "title": "NumPy Analysis",
    "engine": "python",
    "formula": "import numpy as np\nimport matplotlib.pyplot as plt\ndata = np.array([1, 2, 3, 4, 5])\nmean = np.mean(data)\nstd = np.std(data)\nprint(f'Mean: {mean}, Std Dev: {std}')"
}
```

### Example with Structural Analysis:
```python
{
    "statementId": generate(),
    "title": "Beam Analysis",
    "engine": "python",
    "formula": "from anastruct import SystemElements\nss = SystemElements()\nss.add_element(location=[[0, 0], [10, 0]])\nss.q_load(q=-10, element_id=1)\nss.solve()\nprint(f'Max deflection: {ss.get_node_displacements()}')"
}
```

## Working with Units in Python

**CalcTree provides unit-aware integration between Python and MathJS:**

```python
# CalcTree-specific functions:
# - ct.quantity() - Create unit-aware quantities
# - ct.open() - Open files uploaded to workspace

# Referencing MathJS variables:
# Variables from MathJS statements can be referenced directly in Python
# Units are preserved when crossing from MathJS to Python

# Example:
# If MathJS defines: beam_length = 10 m
# Python can use it: total = beam_length * 2  # Maintains units
```

**Note:** Detailed syntax for `ct.quantity()` and unit handling between MathJS and Python should be tested and documented based on actual usage.

## Note About Query Authorization

**Important:** When querying calculations with python statements, you may get "Not Authorised!" errors. This is an API query limitation, but the statements ARE successfully created and appear in the UI. Always verify by checking the page URL in the browser.
