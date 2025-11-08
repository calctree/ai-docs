# CalcTree API Examples

Complete, copy-paste ready examples.

## Setup Code

All examples use this setup:

```python
from nanoid import generate
import requests
import time

WORKSPACE_ID = "your-workspace-id"  # Get from URL
API_KEY = "your-api-key"            # Get from workspace settings
ENDPOINT = "https://graph.calctree.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def execute_query(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
    return response.json()
```

---

## Example 1: Simple Page with Single MathJS Statement

```python
# Generate IDs
page_id = generate()

# Step 1: Create page
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
        "title": "Simple Beam Length",
        "workspaceId": WORKSPACE_ID
    }
})

# Step 2: Add to page tree (CRITICAL!)
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

# Step 3: Create calculation with one statement
execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,  # Use page_id as calculation_id
    "withStatements": [
        {
            "statementId": generate(),
            "title": "beam_length",
            "engine": "mathjs",
            "formula": "beam_length = 10 m"  # MUST include variable assignment
        }
    ],
    "data": {
        "pageId": page_id,  # CRITICAL - links calculation to page
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

---

## Example 2: Multi-Statement Calculation with Cross-References

This example shows variables referencing each other within the same calculation scope.

```python
page_id = generate()

# Create page and add to tree (same as Example 1)
execute_query("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) { id }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {"id": page_id, "title": "Beam Analysis", "workspaceId": WORKSPACE_ID}
})

execute_query("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) { newPageId }
    }
""", {"workspaceId": WORKSPACE_ID, "input": {"pageId": page_id}})

# Create calculation with multiple cross-referencing statements
execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatements": [
        {
            "statementId": generate(),
            "title": "beam_length",
            "engine": "mathjs",
            "formula": "beam_length = 10 m"
        },
        {
            "statementId": generate(),
            "title": "beam_width",
            "engine": "mathjs",
            "formula": "beam_width = 300 mm"
        },
        {
            "statementId": generate(),
            "title": "load",
            "engine": "mathjs",
            "formula": "load = 5 kN"
        },
        {
            "statementId": generate(),
            "title": "moment",
            "engine": "mathjs",
            "formula": "moment = load * beam_length"  # References load and beam_length
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

---

## Example 3: Multiline MathJS (Multiple Math Blocks)

Engineering calculation with 5 multiline_mathjs blocks.

```python
page_id = generate()

# Create page (omitted for brevity - same as above)
# ...

# Create calculation with multiline_mathjs blocks
execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatements": [
        {
            "statementId": generate(),
            "title": "Beam Dimensions",
            "engine": "multiline_mathjs",
            "formula": "length = 10 m\nwidth = 300 mm\nheight = 500 mm"
        },
        {
            "statementId": generate(),
            "title": "Material Properties",
            "engine": "multiline_mathjs",
            "formula": "E = 200 GPa\nnu = 0.3\nrho = 7850 kg/m^3"
        },
        {
            "statementId": generate(),
            "title": "Loading",
            "engine": "multiline_mathjs",
            "formula": "q = 10 kN/m\nP = 50 kN\nM = 100 kN*m"
        },
        {
            "statementId": generate(),
            "title": "Section Properties",
            "engine": "multiline_mathjs",
            "formula": "A = width * height\nI = width * height^3 / 12\nW = I / (height/2)"
        },
        {
            "statementId": generate(),
            "title": "Results",
            "engine": "multiline_mathjs",
            "formula": "sigma_max = M / W\ntau_max = P / A\ndeflection = 5 * q * length^4 / (384 * E * I)"
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

---

## Example 4: Python Statement

**Note:** Python statements require `userId` in the `data` field.

```python
USER_ID = "your-user-id"  # Get from network trace when manually creating python block

page_id = generate()

# Create page (omitted for brevity)
# ...

# Create python statement - note userId in data field
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
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
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
        "userId": USER_ID  # REQUIRED for Python
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

**Note:** Querying calculations with Python may return "Not Authorised!" but the statement IS created - verify in the UI.

---

## Example 5: All Three Engine Types

Demonstrates mathjs, multiline_mathjs, and python in one calculation.

```python
USER_ID = "your-user-id"

page_id = generate()

# Create page (omitted)
# ...

# Step 1: Create with mathjs statement
stmt_id_1 = generate()
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
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatement": {
        "statementId": stmt_id_1,
        "title": "beam_length",
        "engine": "mathjs",
        "formula": "beam_length = 10 m"
    },
    "data": {
        "id": generate(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_1,
        "userId": USER_ID
    }
})

# Step 2: Add multiline_mathjs statement
stmt_id_2 = generate()
execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        revisionId
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id_2,
        "title": "Beam Dimensions",
        "engine": "multiline_mathjs",
        "formula": "width = 300 mm\nheight = 500 mm\narea = width * height"
    },
    "data": {
        "id": generate(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_2,
        "userId": USER_ID
    }
})

# Step 3: Add python statement
stmt_id_3 = generate()
execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        revisionId
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id_3,
        "title": "Python Calculation",
        "engine": "python",
        "formula": "import math\ntotal = sum(range(10))\naverage = total / 10\nresult = math.sqrt(average)\nprint(f'Result: {result}')"
    },
    "data": {
        "id": generate(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id_3,
        "userId": USER_ID
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

---

## Example 6: Engineering Calculation with NumPy

Complete structural analysis using Python libraries.

```python
USER_ID = "your-user-id"
page_id = generate()

# Create page (omitted)
# ...

# MathJS inputs
execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatements": [
        {
            "statementId": generate(),
            "title": "Inputs",
            "engine": "multiline_mathjs",
            "formula": "L = 10 m\nE = 200 GPa\nI = 0.001 m^4\nq = 10 kN/m"
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

# Add Python analysis
stmt_id = generate()
execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id,
        "title": "Deflection Analysis",
        "engine": "python",
        "formula": """import numpy as np
import matplotlib.pyplot as plt

# Create position array
x = np.linspace(0, L, 100)

# Calculate deflection (simply supported beam)
deflection = (q * x / (24 * E * I)) * (L**3 - 2*L*x**2 + x**3)

# Find max deflection
max_def = np.max(np.abs(deflection))
print(f'Maximum deflection: {max_def:.6f} m')

# Print summary
print(f'Beam length: {L} m')
print(f'Load: {q} kN/m')
print(f'Max deflection at center: {max_def:.3f} m')"""
    },
    "data": {
        "id": generate(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id,
        "userId": USER_ID
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

---

## Example 7: Unit-Aware Python with MathJS Integration

Demonstrates proper unit handling when using MathJS variables in Python.

**Key concept:** MathJS variables with units are automatically `ct.quantity()` objects in Python.

```python
USER_ID = "your-user-id"
page_id = generate()

# Create page (omitted for brevity)
# ...

# Step 1: Define inputs with MathJS (with units)
execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatements": [
        {
            "statementId": generate(),
            "title": "Inputs",
            "engine": "multiline_mathjs",
            "formula": "beam_length = 10 m\nload = 5 kN\nE = 200 GPa\nI = 0.001 m^4"
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})

# Step 2: Add Python analysis with unit-aware calculations
stmt_id = generate()
execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id,
        "title": "Unit-Aware Analysis",
        "engine": "python",
        "formula": """# MathJS variables automatically have units attached!
# beam_length, load, E, I are all ct.quantity() objects

# Calculate moment - unit arithmetic is automatic
moment = load * beam_length  # Returns: 50 kN*m

# Calculate deflection with units
deflection = (load * beam_length**3) / (48 * E * I)

# Convert to different units
moment_Nm = moment.to("N*m")  # Convert to N*m
deflection_mm = deflection.to("mm")  # Convert to mm

# Extract numeric values
moment_value = moment_Nm.magnitude()
deflection_value = deflection_mm.magnitude()

# Create new quantities for limits
max_moment = ct.quantity("100 kN*m")
max_deflection = ct.quantity("25 mm")

# Unit-aware comparisons
print(f"Moment: {moment} = {moment_Nm}")
print(f"Deflection: {deflection} = {deflection_mm}")
print()

# Check limits with units
if moment < max_moment:
    print(f"✓ Moment OK: {moment} < {max_moment}")
else:
    print(f"✗ Moment FAIL: {moment} > {max_moment}")

if deflection_mm < max_deflection:
    print(f"✓ Deflection OK: {deflection_mm} < {max_deflection}")
else:
    print(f"✗ Deflection FAIL: {deflection_mm} > {max_deflection}")

# IMPORTANT: Do NOT wrap MathJS variables:
# ❌ WRONG: load_qty = ct.quantity(load)  # load is already a quantity!
# ✅ CORRECT: Just use load directly
"""
    },
    "data": {
        "id": generate(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id,
        "userId": USER_ID
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

**Key takeaways:**
1. MathJS variables (`beam_length`, `load`, etc.) automatically become `ct.quantity()` objects in Python
2. Unit arithmetic happens automatically - just use normal operators
3. Use `.to("unit")` to convert units
4. Use `.magnitude()` to extract numeric values
5. DO NOT wrap MathJS variables with `ct.quantity()` - they already have units

---

## Complete Helper Function

Reusable function for creating pages with calculations:

```python
def create_calctree_page(title, statements, workspace_id, api_key, user_id=None):
    """
    Create a CalcTree page with calculations.

    Args:
        title: Page title
        statements: List of dicts with 'title', 'engine', 'formula'
        workspace_id: CalcTree workspace ID
        api_key: API key
        user_id: User ID (required for Python statements)

    Returns:
        Page URL
    """
    endpoint = "https://graph.calctree.com/graphql"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    def execute(query, variables):
        return requests.post(endpoint, headers=headers,
                           json={"query": query, "variables": variables}).json()

    # Generate page ID
    page_id = generate()

    # Create page
    execute("""
        mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
          createPageSync(workspaceId: $workspaceId, input: $input) { id }
        }
    """, {
        "workspaceId": workspace_id,
        "input": {"id": page_id, "title": title, "workspaceId": workspace_id}
    })

    # Add to tree
    execute("""
        mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
          addPageNode(workspaceId: $workspaceId, input: $input) { newPageId }
        }
    """, {"workspaceId": workspace_id, "input": {"pageId": page_id}})

    # Add statements
    with_statements = []
    for stmt in statements:
        with_statements.append({
            "statementId": generate(),
            "title": stmt["title"],
            "engine": stmt["engine"],
            "formula": stmt["formula"]
        })

    data = {
        "pageId": page_id,
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }

    if user_id:
        data["userId"] = user_id

    execute("""
        mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
          createOrUpdateCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            withStatements: $withStatements
            data: $data
          ) {
            calculationId
          }
        }
    """, {
        "workspaceId": workspace_id,
        "calculationId": page_id,
        "withStatements": with_statements,
        "data": data
    })

    return f"https://app.calctree.com/edit/{workspace_id}/{page_id}"


# Usage
url = create_calctree_page(
    title="Beam Analysis",
    statements=[
        {"title": "length", "engine": "mathjs", "formula": "length = 10 m"},
        {"title": "load", "engine": "mathjs", "formula": "load = 5 kN"},
        {"title": "moment", "engine": "mathjs", "formula": "moment = load * length"}
    ],
    workspace_id=WORKSPACE_ID,
    api_key=API_KEY
)
print(url)
```

---

## Example 8: Upload File and Use in Python

Complete workflow for uploading a CSV file and accessing it in a Python calculation.

```python
import os

# Step 1: Get presigned upload URL
presigned_result = execute_query("""
    mutation GetUploadURL($workspaceId: ID!, $fileName: String!, $contentType: String!) {
      createPresignedUploadPost(
        workspaceId: $workspaceId
        fileName: $fileName
        contentType: $contentType
      ) {
        url
        fields
        key
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "fileName": "beam_loads.csv",
    "contentType": "text/csv"
})

s3_url = presigned_result['data']['createPresignedUploadPost']['url']
fields = presigned_result['data']['createPresignedUploadPost']['fields']
file_key = presigned_result['data']['createPresignedUploadPost']['key']

# Step 2: Upload file to S3
with open('beam_loads.csv', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post(s3_url, data=fields, files=files)

if upload_response.status_code not in [200, 204]:
    print(f"Upload failed: {upload_response.status_code}")
    exit(1)

print("✓ File uploaded to S3")

# Step 3: Register file in workspace
file_size = os.path.getsize('beam_loads.csv')
file_result = execute_query("""
    mutation AddFile($workspaceId: ID!, $key: String!, $fileName: String!, $contentType: String!, $size: Int!) {
      addWorkspaceFile(
        workspaceId: $workspaceId
        key: $key
        fileName: $fileName
        contentType: $contentType
        size: $size
      ) {
        id
        fileName
        url
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "key": file_key,
    "fileName": "beam_loads.csv",
    "contentType": "text/csv",
    "size": file_size
})

print(f"✓ File registered: {file_result['data']['addWorkspaceFile']['fileName']}")

# Step 4: Create page that uses the file in Python
page_id = generate()

# Create page (steps omitted for brevity)
# ...

# Add Python statement that reads the uploaded file
stmt_id = generate()
execute_query("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      addStatementToCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        revisionId: $revisionId
        withStatement: $withStatement
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": stmt_id,
        "title": "Load Analysis from CSV",
        "engine": "python",
        "formula": """import pandas as pd
import io

# Read CSV file uploaded to workspace
csv_content = ct.open('beam_loads.csv', mode='r').read()

# Parse with pandas
df = pd.read_csv(io.StringIO(csv_content))

# Analyze data
max_load = df['load'].max()
min_load = df['load'].min()
avg_load = df['load'].mean()
total_rows = len(df)

# Report results
print(f'CSV File Analysis:')
print(f'  Rows: {total_rows}')
print(f'  Max Load: {max_load} kN')
print(f'  Min Load: {min_load} kN')
print(f'  Avg Load: {avg_load:.2f} kN')

# Create unit-aware quantity for further calculations
max_load_qty = ct.quantity(f'{max_load} kN')
print(f'\\nMax load with units: {max_load_qty}')
"""
    },
    "data": {
        "id": generate(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id,
        "userId": USER_ID
    }
})

print(f"Page URL: https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

**Required CSV format (beam_loads.csv):**
```csv
beam_id,load,unit
B001,10,kN
B002,15,kN
B003,12,kN
```

**Key points:**
1. File upload is 3 steps: get presigned URL → upload to S3 → register in workspace
2. Use `ct.open('filename.csv', mode='r')` to read files in Python
3. Files must be uploaded before they can be accessed
4. Use pandas to parse CSV data
5. Combine file data with CalcTree's unit-aware calculations

---

## See Also

- [API_REFERENCE.md](API_REFERENCE.md) - Complete GraphQL API reference
- [CALCULATION_GUIDE.md](CALCULATION_GUIDE.md) - Formula syntax and scoping
- [PYTHON_GUIDE.md](PYTHON_GUIDE.md) - Python libraries and examples
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
