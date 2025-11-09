# CalcTree MDX Syntax Guide

Complete reference for writing CalcTree page content with MDX components and markdown.

## Overview

CalcTree uses MDX (Markdown + JSX) for page content, combining standard markdown with custom calculation components. The markdown engine is based on PlateJS for standard elements, with CalcTree-specific components for calculations and inputs.

---

## Critical Format Rules

- Output markdown/MDX formatted text only
- Use blank lines between all content blocks
- **NO backticks, indentation, or code block formatting around MDX components**
- Write MDX components as raw MDX directly in the markdown
- All explanatory text must be in markdown, never inside formula attributes

---

## CalcTree MDX Components

### EquationBlock (Math Block)

The primary component for engineering calculations. Also known as "math block".

**Syntax:**
```
<EquationBlock name="BlockName" formula='statement1\nstatement2\nstatement3' />
```

**Key Requirements:**
1. **Blank lines** before and after each EquationBlock (mandatory)
2. Use `\n` to separate statements within formula attribute
3. Use single quotes (') for formula attribute if it contains double quotes
4. **NO comments on same line** - All explanations/comments must be in plain text BEFORE the EquationBlock

**Example:**
```
Calculate beam properties:

<EquationBlock name="Inputs" formula='P = 50 kN\nL = 6 m\nE = 200000 MPa' />

Intermediate calculations:

<EquationBlock name="Calculations" formula='M_max = P * L / 4\ndelta = P * L^3 / (48 * E * I)' />
```

**Complex Multi-Line Example:**
```
Project cost calculations:

<EquationBlock name="CostBreakdown" formula="# Project cost calculations&#10;baseCost = budget * 0.7&#10;overheadCost = budget * 0.2&#10;contingency = budget * 0.1&#10;&#10;# Team calculations&#10;weeksPerDeveloper = timelineWeeks * teamSize&#10;hourlyRate = 150&#10;developerCost = weeksPerDeveloper * 40 * hourlyRate&#10;&#10;# Final calculations&#10;totalProjectCost = baseCost + overheadCost + contingency&#10;remainingBudget = budget - totalProjectCost" />
```

**Note:** `&#10;` is the HTML entity for newline when using double quotes. Use `\n` with single quotes instead.

---

### SelectInput

Dropdown selection input component.

**Syntax:**
```
<SelectInput name="variableName" description="Display Label" formula='variableName=ctselect(["Option1", "Option2", "Option3"], "DefaultOption")' />
```

**Example:**
```
<SelectInput name="projectType" description="Project Type" formula='projectType=ctselect(["Web App", "Mobile App", "Desktop App", "API Service"], "Web App")' />
```

---

### RadioInput

Radio button selection input component.

**Syntax:**
```
<RadioInput name="variableName" description="Display Label" formula='variableName=ctselect(["Option1", "Option2", "Option3"], "DefaultOption")' />
```

**Example:**
```
<RadioInput name="radioProjectType" description="Project Type" formula='projectType=ctselect(["Web App", "Mobile App", "Desktop App", "API Service"], "Web App")' />
```

---

### SimpleInput

Single numeric input field.

**Syntax:**
```
<SimpleInput name="variableName" format="general" decimal={0} description="Display Label" formula="variableName=defaultValue" />
```

**Attributes:**
- `name` - Variable name
- `format` - Number format ("general", "decimal", etc.)
- `decimal` - Number of decimal places (as JSX expression: `{0}`, `{2}`, etc.)
- `description` - Label shown to user
- `formula` - Initial value assignment

**Example:**
```
<SimpleInput name="teamSize" format="general" decimal={0} description="Team Size" formula="teamSize=5" />
```

---

### MatrixBlock

Matrix/table input component.

**Syntax:**
```
<MatrixBlock name="matrixName" format="general" decimal={0} description="Display Label" formula="matrixName=[[row1col1,row1col2],[row2col1,row2col2]]" />
```

**Example:**
```
<MatrixBlock name="teamSizeMat" format="general" decimal={0} description="Team Size Matrix" formula="teamSizeMat=[[1,2],[3,4]]" />
```

---

## Standard Markdown Elements

CalcTree uses PlateJS for standard markdown rendering.

### Headings

```
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
```

---

### Text Formatting

**Bold:**
```
**bold text**
```

**Italic:**
```
_italic text_
```

**Combined (bold + italic):**
```
_**bold and italic**_
```

**Strikethrough:**
```
~~strikethrough text~~
```

**Inline code:**
```
Use `inline code` for variable names or code snippets.
```

---

### Links

**Hyperlinks:**
```
[Link text](https://example.com)
```

**Example:**
```
See the [CalcTree documentation](https://calctree.com/docs) for more details.
```

---

### Images

```
![Alt text](image-url)
```

**Example:**
```
![Beam diagram](https://example.com/beam.png)
```

---

### Blockquotes

```
> This is a blockquote.
> It can span multiple lines.
```

---

### Lists

**Unordered lists:**
```
- First item
- Second item
- Third item
```

**Ordered lists:**
```
1. First step
2. Second step
3. Third step
```

**Task lists:**
```
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task
```

---

### Code Blocks

**Fenced code blocks with syntax highlighting:**

````
```python
def calculate_moment(load, length):
    return load * length / 4
```
````

**JavaScript example:**

````
```javascript
function greet() {
  console.info("Hello World!")
}
```
````

---

### Tables

```
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Row 1    | Data     | More     |
| Row 2    | Data     | More     |
```

**Example with formatting:**

```
| **Plugin** | **Element** | **Inline** | **Void** |
|-----------|-------------|------------|----------|
| Heading   | Yes         | No         | No       |
| Image     | Yes         | No         | Yes      |
| Mention   | Yes         | Yes        | Yes      |
```

---

### Horizontal Rules

```
---
```

Use three or more hyphens to create a horizontal line separator.

---

### LaTeX Math

**Block equations (centered):**
```
$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
```

**Inline equations:**
```
The quadratic formula $\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$ solves for x.
```

---

### Columns

Create multi-column layouts:

```
<column_group>
<column width="33%">First column content</column>
<column width="33%">Second column content</column>
<column width="34%">Third column content</column>
</column_group>
```

**Note:** Widths must sum to 100%.

---

## Variable and Unit Rules

### Units on Inputs Only

- **INPUT variables**: Always include units (e.g., `P = 50 kN`)
- **CALCULATED variables**: Never include units - they're computed automatically (e.g., `M_max = P * L / 4`)

**Correct:**
```
<EquationBlock name="Inputs" formula='P = 50 kN\nL = 6 m' />

<EquationBlock name="Calculations" formula='M_max = P * L / 4' />
```

**Incorrect:**
```
<EquationBlock name="Calculations" formula='M_max = P * L / 4 kN*m' />
```

### Variable Naming

- Use underscores, not apostrophes: `f_c` not `f'c`
- Use descriptive names: `beam_length` not `L` (unless standard notation)
- No spaces in variable names

---

## Document Structure Best Practices

### 1. Inputs Section

Define all input variables with units:

```
## Design Parameters

<EquationBlock name="Inputs" formula='N_star = 1500 kN\nf_c = 32 MPa\nD = 400 mm\nB = 400 mm\ncover = 40 mm' />
```

### 2. Calculations Section

Intermediate calculations without units:

```
## Section Capacity

Calculate cross-sectional area and capacity:

<EquationBlock name="Capacity" formula='A_g = B * D\nphi = 0.6\nN_uo = 0.85 * f_c * A_g\nphi_N_uo = phi * N_uo' />
```

### 3. Checks Section

Results and conditional checks:

```
## Design Check

<EquationBlock name="Check" formula='utilization = N_star / phi_N_uo\nstatus = utilization <= 1.0 ? "PASS" : "FAIL"' />
```

---

## Function Definitions

Define custom functions within EquationBlocks:

```
<EquationBlock name="Functions" formula='f(x) = x^3\nc = f(3)\ng(a,b) = a * b + 2\nresult = g(5, 10)' />
```

**Complex function example:**
```
Define load factors based on member type:

<EquationBlock name="LoadFactors" formula='phi(type) = equalText(type, "Beam") ? 0.8 : equalText(type, "Column") ? 0.6 : 0.7\nmember_type = "Beam"\nfactor = phi(member_type)' />
```

---

## Conditional Logic

Use ternary operators for checks:

```
<EquationBlock name="Checks" formula='result = condition ? "OK" : "NG"\nutilization_ratio = demand / capacity\nstatus = utilization_ratio <= 1.0 ? "PASS" : "FAIL"' />
```

---

## Mathematical Operations

CalcTree uses mathjs syntax:

- Addition: `a + b`
- Subtraction: `a - b`
- Multiplication: `a * b`
- Division: `a / b`
- Exponentiation: `a^b` or `pow(a, b)`
- Square root: `sqrt(x)`
- Absolute value: `abs(x)`
- Min/max: `min(a, b, c)`, `max(a, b, c)`
- Trigonometry: `sin(x)`, `cos(x)`, `tan(x)`

---

## String Comparisons

Use `equalText()` function for string comparisons:

```
<EquationBlock name="MaterialCheck" formula='result = equalText(material, "Steel") ? steel_value : concrete_value' />
```

---

## Complete Example: Concrete Column Design

```
# Concrete Column Design to AS3600

## Design Parameters

<EquationBlock name="Inputs" formula='N_star = 1500 kN\nf_c = 32 MPa\nD = 400 mm\nB = 400 mm\ncover = 40 mm' />

## Concrete Properties

Define concrete strength reduction factors:

<EquationBlock name="Properties" formula='alpha_1 = 0.85 - 0.0015 * f_c\nalpha_1_final = alpha_1 >= 0.67 ? alpha_1 : 0.67\nalpha_2 = 0.85 - 0.0025 * f_c\nalpha_2_final = alpha_2 >= 0.67 ? alpha_2 : 0.67' />

## Section Capacity

Calculate gross cross-sectional area and capacity:

<EquationBlock name="Capacity" formula='A_g = B * D\nphi = 0.6\nN_uo = 0.85 * f_c * A_g\nphi_N_uo = phi * N_uo' />

## Design Check

<EquationBlock name="Check" formula='utilization = N_star / phi_N_uo\nstatus = utilization <= 1.0 ? "PASS" : "FAIL"' />

The column has a utilization ratio shown above and the design check status is displayed.
```

---

## Comments and Documentation

**CORRECT** - Comment before block:
```
This calculates the maximum moment for a simply supported beam:

<EquationBlock name="Moment" formula='M_max = w * L^2 / 8' />
```

**INCORRECT** - Never inline comments:
```
<EquationBlock name="Moment" formula='M_max = w * L^2 / 8  # maximum moment' />
```

All explanatory text must be in markdown above or below the EquationBlock, never inside the formula attribute.

---

## Best Practices Summary

1. **Always use blank lines** around MDX components
2. **Group related calculations** in the same EquationBlock
3. **Use descriptive names** for components (e.g., "Inputs", "BeamCapacity", "SafetyChecks")
4. **Define inputs first**, then calculations, then checks
5. **Only specify units on inputs** - let CalcTree compute output units
6. **Use functions for reusable logic** rather than repeating formulas
7. **Add markdown descriptions** above blocks to explain what they calculate
8. **Use ternary operators** for conditional logic and checks
9. **Avoid inline comments** - all documentation should be in markdown, not in formulas
10. **Use `&#10;` for newlines** in double-quoted attributes, or use `\n` with single quotes

---

## Integration with API

When creating page content via the API using `putInitialPageContent`, embed MDX components in the markdown string.

**Note:** In GraphQL strings, backslashes must be escaped (`\\n` instead of `\n`):

```graphql
mutation UpdatePageContent {
  putInitialPageContent(
    workspaceId: "workspace_id"
    input: {
      pageId: "page_id"
      markdown: "# My Calculation\\n\\n<EquationBlock name='Inputs' formula='x = 5\\\\ny = 10\\\\nresult = x * y' />\\n\\nThe result shows the product."
    }
  )
}
```

See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation.
