# Python Engine - Complete Guide

The python engine is fully supported and working. The key requirement is including `userId` in the `data` field.

## Complete Python Example

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

CalcTree provides a comprehensive Python environment with 26+ pre-installed libraries:

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

CalcTree provides comprehensive unit handling in Python using the `pint` library, with built-in CalcTree functions for unit-aware calculations.

### Key Concepts

**IMPORTANT:** When you reference MathJS variables with units in Python, they are **automatically** `ct.quantity()` objects - you don't need to wrap them!

### Creating Unit-Aware Values

Use `ct.quantity()` to create values with physical units:

```python
# Create quantities with units
force = ct.quantity("1 N")
area = ct.quantity("1 m^2")

# CalcTree automatically handles unit arithmetic
pressure = force / area  # Returns: 1 Pa (kg/m/s^2)
```

### Unit Operations

**Create a unit with magnitude 1.0:**
```python
kN = ct.units("kN")
```

**Convert to compatible units:**
```python
pressure_kPa = pressure.to("kPa")
```

**Extract numeric value (without unit):**
```python
value = pressure_kPa.magnitude()
```

### Working with MathJS Variables (CRITICAL)

**When MathJS variables have units, they automatically become `ct.quantity()` objects in Python:**

```python
# MathJS statement defines:
# width = 100 mm
# height = 2.5 m

# In Python - these are ALREADY ct.quantity objects:
area = width * height  # Unit math happens automatically

# Convert to different unit
area_m2 = area.to("m^2")

# Get just the number
numeric_value = area_m2.magnitude()
```

**Do NOT re-wrap page parameters:**
```python
# ❌ WRONG - don't do this:
width_qty = ct.quantity(width)  # width is already a quantity!

# ✅ CORRECT - use directly:
area = width * height  # Just use them
```

### Complete Example: MathJS → Python with Units

```python
# Assume MathJS defines:
# beam_length = 10 m
# load = 5 kN

# Python code:
# Variables automatically have units attached
moment = load * beam_length  # Returns: 50 kN*m

# Convert to different units
moment_Nm = moment.to("N*m")  # Returns: 50000 N*m

# Extract numeric value
moment_value = moment_Nm.magnitude()  # Returns: 50000.0

# Create new quantities
max_stress = ct.quantity("250 MPa")
safety_factor = max_stress / moment  # Unit-aware division

print(f"Moment: {moment}")
print(f"Moment in N*m: {moment_Nm}")
print(f"Numeric value: {moment_value}")
```

### Unit Validation

CalcTree enforces physical consistency - invalid operations raise errors:

```python
# ❌ This will raise an error:
invalid = ct.quantity("5 s") + ct.quantity("2 m")  # Can't add time and length!

# ✅ This works:
valid = ct.quantity("5 m") + ct.quantity("200 cm")  # Returns: 7 m
```

### Practical Engineering Example

```python
# MathJS inputs with units:
# E = 200 GPa
# I = 0.001 m^4
# L = 10 m
# q = 10 kN/m

# Python analysis - all variables automatically have units
max_deflection = (5 * q * L**4) / (384 * E * I)

# Convert to mm for reporting
deflection_mm = max_deflection.to("mm")

# Check against limit
limit = ct.quantity("25 mm")
if deflection_mm < limit:
    print(f"✓ PASS: Deflection {deflection_mm} < {limit}")
else:
    print(f"✗ FAIL: Deflection {deflection_mm} > {limit}")

# Extract value for further calculations
deflection_value = deflection_mm.magnitude()
```

### CalcTree Unit Functions Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `ct.quantity("value unit")` | Create unit-aware value | `ct.quantity("100 kN")` |
| `ct.units("unit")` | Create unit with magnitude 1.0 | `ct.units("MPa")` |
| `.to("unit")` | Convert to different unit | `pressure.to("kPa")` |
| `.magnitude()` | Extract numeric value | `value.magnitude()` |

### Important Notes

1. **MathJS variables with units are automatically `ct.quantity()` objects** - don't wrap them again
2. **Unit arithmetic is automatic** - just use operators normally
3. **CalcTree uses the pint library** - see [pint documentation](https://pint.readthedocs.io/en/stable/) for advanced features
4. **Invalid unit operations raise errors** - this provides built-in quality control

---

## Working with Files

### Reading Uploaded Files

Use `ct.open()` to access files that have been uploaded to the workspace:

```python
# Read text file
content = ct.open('data.csv', mode='r').read()

# Read binary file
binary_data = ct.open('image.png', mode='rb').read()
```

### CSV Files with Pandas

```python
import pandas as pd
import io

# Read CSV file
csv_content = ct.open('beam_data.csv', mode='r').read()

# Parse with pandas
df = pd.read_csv(io.StringIO(csv_content))

# Work with DataFrame
max_value = df['load'].max()
filtered = df[df['load'] > 10]
```

### Excel Files

```python
import pandas as pd
import io

# Read Excel file
excel_data = ct.open('calculations.xlsx', mode='rb').read()

# Parse with pandas
df = pd.read_excel(io.BytesIO(excel_data), sheet_name='Sheet1')
```

### JSON Files

```python
import json

# Read JSON file
json_content = ct.open('config.json', mode='r').read()

# Parse JSON
data = json.loads(json_content)
settings = data['settings']
```

### File Upload Process

Files must be uploaded to the workspace before they can be accessed with `ct.open()`. See [API_REFERENCE.md](API_REFERENCE.md#file-management) for the complete upload process:

1. Get presigned upload URL (`createPresignedUploadPost`)
2. Upload file to S3
3. Register file in workspace (`addWorkspaceFile`)

Once uploaded, files are available to all Python statements in the workspace.

### Complete Example

```python
# File already uploaded to workspace as 'test_data.csv'

import pandas as pd
import io

# Read CSV
csv_data = ct.open('test_data.csv', mode='r').read()
df = pd.read_csv(io.StringIO(csv_data))

# Analyze
total_load = df['load'].sum()
avg_length = df['length'].mean()

# Create unit-aware quantities
total_load_qty = ct.quantity(f'{total_load} kN')
avg_length_qty = ct.quantity(f'{avg_length} m')

print(f'Total Load: {total_load_qty}')
print(f'Average Length: {avg_length_qty}')
```

---

## Note About Query Authorization

**Important:** When querying calculations with python statements, you may get "Not Authorised!" errors. This is an API query limitation, but the statements ARE successfully created and appear in the UI. Always verify by checking the page URL in the browser.
