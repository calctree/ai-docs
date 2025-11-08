# CalcTree Calculation Syntax Guide

## Table of Contents
1. [Calculation Scope & Variables](#calculation-scope--variables)
2. [MathJS Syntax](#mathjs-syntax)
3. [Multiline MathJS Syntax](#multiline-mathjs-syntax)
4. [Python Syntax](#python-syntax)
5. [Variable Referencing](#variable-referencing)
6. [Display Types](#display-types)
7. [Complete Examples](#complete-examples)

---

## Calculation Scope & Variables

### Key Concepts

**Calculation Scope:**
- All statements within a single calculation share the same variable scope
- Variables defined in one statement can be referenced by other statements in the same calculation
- The `calculationId` determines the scope boundary
- Variables are evaluated in the order they appear

**Statement Structure:**
- `title`: The display name for the statement (appears in UI sidebar)
- `formula`: The actual mathematical expression or code
- `engine`: The calculation engine (`mathjs`, `multiline_mathjs`, or `python`)

**Variable Names:**
- Use clear, descriptive names (e.g., `beam_length`, `total_load`)
- Can contain letters, numbers, and underscores
- Should be snake_case for consistency
- The `title` field is the statement identifier, not necessarily the variable name

---

## MathJS Syntax

### Assignment Display Type (Default)

**Formula Pattern:** `variable_name = value units`

**Rules:**
1. Variable name MUST be included in the formula
2. Use `=` to assign value to variable
3. Units are optional but recommended
4. Each statement creates ONE variable

**Examples:**

```javascript
// Basic assignment with units
beam_length = 10 m
width = 300 mm
height = 500 mm
load = 5 kN

// Assignment without units
count = 42
factor = 1.5
name = "Steel Beam"

// Calculated assignments (referencing other variables)
area = width * height
moment = load * beam_length
stress = moment / (width * height^2 / 6)
```

### Unit Handling

**Supported Operations:**
```javascript
// Unit arithmetic
pressure = 1 kPa
area = 1 m^2
force = pressure * area  // Returns: 1 kN

// Unit conversion using 'to'
length_m = 3 m + 200 cm  // Returns: 5 m
length_ft = length_m to ft  // Converts to feet

// Invalid operations are prevented
invalid = 10 m + 5 kg  // ERROR: Cannot add incompatible units
```

**Common Units:**
- Length: `m`, `mm`, `cm`, `km`, `ft`, `in`
- Force: `N`, `kN`, `MN`, `lbf`, `kip`
- Pressure: `Pa`, `kPa`, `MPa`, `GPa`, `psi`, `ksi`
- Area: `m^2`, `mm^2`, `ft^2`, `in^2`
- Volume: `m^3`, `L`, `gal`, `ft^3`

### Mathematical Functions

```javascript
// Built-in Math.js functions
sqrt_value = sqrt(16)
abs_value = abs(-10)
max_value = max(5, 10, 3)
min_value = min(5, 10, 3)
rounded = round(3.7)

// Trigonometric (angles in radians)
sin_val = sin(pi/2)
cos_val = cos(0)
tan_val = tan(pi/4)

// With units
result = sqrt(25 m^2)  // Returns: 5 m
```

---

## Multiline MathJS Syntax

### When to Use
- Multiple related variables in one statement
- Intermediate calculations
- Complex multi-step formulas

**Formula Pattern:** Multiple lines separated by `\n`

**Examples:**

```javascript
// Multiple assignments in one statement
width = 300 mm
height = 500 mm
area = width * height

// Intermediate calculations
E = 200 GPa
nu = 0.3
G = E / (2 * (1 + nu))
K = E / (3 * (1 - 2*nu))

// Section properties
b = 400 mm
h = 600 mm
A = b * h
I = b * h^3 / 12
W = I / (h/2)
```

**Rules:**
1. Each line creates a new variable
2. Variables from earlier lines can be used in later lines
3. All variables created in the block are available to other statements
4. Use `\n` (actual newline character) to separate lines in API calls

---

## Python Syntax

### Basic Structure

**Formula Pattern:** Python code with imports and calculations

**Key Requirements:**
1. Include `userId` in the `data` field when creating python statements via API
2. Variables defined in global scope are available to other statements
3. Use `print()` for output display

**Examples:**

```python
# Basic calculation
import math
total = sum(range(10))
average = total / 10
result = math.sqrt(average)
print(f'Result: {result}')

# Using NumPy
import numpy as np
array = np.array([1, 2, 3, 4, 5])
mean_value = np.mean(array)
std_value = np.std(array)
print(f'Mean: {mean_value}, Std: {std_value}')

# Reading workspace files
data = ct.open('data.csv', mode='rb').read()
print(f'File size: {len(data)} bytes')
```

### Available Libraries

CalcTree provides 26+ pre-installed Python libraries:

**Core Scientific:** numpy, scipy, pandas, matplotlib, seaborn, SymPy, Scikit-learn

**Engineering/Structural:** anaStruct, OpenSeesPy+OpsVis, PyNite, pyFrame3DD, pycba, sectionproperties, StructPy, pyCalculiX, eurocodepy

**Specialized:** Groundhog (geotechnical), GemPy (geological), REDi (resilience), energy-py-linear

**Utilities:** handcalcs, ezdxf, SimPy, pysal, joypy, topojson

**Standard:** math, all Python 3 standard library

**CalcTree-specific:** `ct.open()` for workspace files, `ct.quantity()` for units

### Referencing MathJS Variables in Python

Variables defined in mathjs statements within the same calculation scope can be referenced in Python.

**CRITICAL: MathJS variables with units are automatically `ct.quantity()` objects:**

```python
# MathJS defines:
# beam_length = 10 m
# load = 5 kN

# Python code - variables automatically have units:
moment = beam_length * load  # Returns: 50 kN*m (unit math automatic)

# Convert units
moment_Nm = moment.to("N*m")  # Returns: 50000 N*m

# Extract numeric value
value = moment_Nm.magnitude()  # Returns: 50000.0

print(f'Moment: {moment}')
print(f'Moment in N*m: {moment_Nm}')
```

**Do NOT wrap MathJS variables with `ct.quantity()`** - they already have units attached automatically.

See [PYTHON_GUIDE.md](PYTHON_GUIDE.md) for complete unit handling documentation.

---

## Variable Referencing

### Within Same Calculation Scope

All statements in a calculation can reference variables from other statements:

**Example Calculation Structure:**

```javascript
// Statement 1: Input parameters (mathjs)
title: "beam_length"
formula: "beam_length = 10 m"

// Statement 2: More inputs (mathjs)
title: "load"
formula: "load = 5 kN"

// Statement 3: Calculated result (mathjs) - references Statement 1 & 2
title: "moment"
formula: "moment = load * beam_length"  // Uses load and beam_length

// Statement 4: Section properties (multiline_mathjs)
title: "Section"
formula: "width = 300 mm\nheight = 500 mm\nI = width * height^3 / 12"

// Statement 5: Stress calculation (mathjs) - references Statement 3 & 4
title: "stress"
formula: "stress = moment / (I / (height/2))"  // Uses moment, I, and height
```

### Cross-Statement Dependencies

Variables flow through the calculation in order:
1. Input variables (no dependencies)
2. Intermediate calculations (depend on inputs)
3. Final results (depend on intermediates)

**Best Practice:** Organize statements logically from inputs → calculations → outputs

---

## Display Types

### 1. Assignment (Default)
- Simple variable with assigned value
- Syntax: `variable_name = value units`
- Use for: Input parameters, calculated results

### 2. Selection (Dropdown) List
- User selects from predefined options
- Can populate from CSV data
- Returns selected value to calculation scope

### 3. Tabular Matrix
- Display data in table format
- Can reference individual cells
- Useful for schedules and structured data

### 4. Options
- Multiple choice selection
- Similar to dropdown but different UI

### 5. Traffic Light
- Visual indicator (red/yellow/green)
- Based on conditional logic
- Use for: Pass/fail criteria, safety factors

**Note:** Display types are configured in the UI. Via API, use Assignment type (standard formula syntax).

---

## Complete Examples

### Example 1: Simple Beam Analysis

```python
from nanoid import generate
import requests
import time

# ... (setup code)

# Create interrelated calculation
execute_query("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) {
        calculationId
        revisionId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatements": [
        {
            "statementId": generate(),
            "title": "Geometry",
            "engine": "multiline_mathjs",
            "formula": "L = 10 m\nb = 300 mm\nh = 500 mm"
        },
        {
            "statementId": generate(),
            "title": "Loading",
            "engine": "multiline_mathjs",
            "formula": "q = 10 kN/m\nP = 50 kN"
        },
        {
            "statementId": generate(),
            "title": "Section Properties",
            "engine": "multiline_mathjs",
            "formula": "A = b * h\nI = b * h^3 / 12\nW = I / (h/2)"
        },
        {
            "statementId": generate(),
            "title": "max_moment",
            "engine": "mathjs",
            "formula": "max_moment = q * L^2 / 8 + P * L / 4"
        },
        {
            "statementId": generate(),
            "title": "max_stress",
            "engine": "mathjs",
            "formula": "max_stress = max_moment / W"
        },
        {
            "statementId": generate(),
            "title": "Analysis",
            "engine": "python",
            "formula": "import math\nprint(f'Max Stress: {max_stress}')\nif max_stress < 250e6:  # Pa\n    print('PASS: Stress within limits')\nelse:\n    print('FAIL: Stress exceeds limits')"
        }
    ],
    "data": {
        "pageId": page_id,
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})
```

### Example 2: Material Properties with Cross-References

```javascript
// Statement 1: Material constants
E = 200 GPa
nu = 0.3
rho = 7850 kg/m^3

// Statement 2: Derived properties (references Statement 1)
G = E / (2 * (1 + nu))
K = E / (3 * (1 - 2*nu))

// Statement 3: Geometry
L = 5 m
A = 0.01 m^2

// Statement 4: Mass calculation (references Statements 1 and 3)
mass = rho * A * L

// Statement 5: Stiffness (references Statements 1, 2, and 3)
axial_stiffness = E * A / L
shear_stiffness = G * A / L
```

### Example 3: Mixed Engine Types

```python
# MathJS: Input
beam_length = 10 m
load = 5 kN

# Multiline MathJS: Section
width = 300 mm
height = 500 mm
I = width * height^3 / 12

# MathJS: Calculate moment
moment = load * beam_length

# Python: Analysis and reporting
import numpy as np
print(f'Beam Length: {beam_length}')
print(f'Applied Load: {load}')
print(f'Bending Moment: {moment}')
stress_array = np.linspace(0, moment, 10)
print(f'Max stress in array: {max(stress_array)}')
```

---

## Summary: Creating Multi-Statement Calculations

1. **Use `createOrUpdateCalculation`** with all statements in `withStatements` array
2. **Set `calculationId = pageId`** to link calculation to page
3. **Use correct syntax** for each engine type:
   - mathjs: `variable_name = value units`
   - multiline_mathjs: Multiple lines with `\n`
   - python: Standard Python code
4. **Reference variables** by name across statements in same calculation
5. **Order matters**: Define variables before using them
6. **Include units** for physical quantities (mathjs handles unit math)
7. **For python**: Include `userId` in `data` field when creating via API

---

## API Notes

- Query authorization may fail for calculations with python statements, but statements ARE created successfully
- Always verify page URL in browser to confirm statements appear
- Use `revisionId: "ffffffff"` for operations even though API returns `null`
- All IDs use nanoid format (21 characters)
