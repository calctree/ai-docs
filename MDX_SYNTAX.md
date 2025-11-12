# CalcTree MDX Syntax Guide

Complete reference for writing CalcTree page content with MDX components and markdown.

## Overview

CalcTree uses MDX (Markdown + JSX) for page content, combining standard markdown with custom calculation components. The markdown engine is based on PlateJS for standard elements, with CalcTree-specific components for calculations and inputs.

---

## Critical Rules for AI Agents Generating MDX

When generating CalcTree page content, follow these formatting rules:

### ⚠️ MOST CRITICAL RULE: Blank Lines Around Components

**EVERY MDX component (EquationBlock, SelectInput, RadioInput, SimpleInput, MatrixBlock) MUST be:**
- Preceded by a blank line (double newline `\n\n`)
- Followed by a blank line (double newline `\n\n`)
- Written on its own line, never inline with text
- Written as raw MDX, NEVER wrapped in code blocks (\`\`\`)

This is the #1 most common mistake. Always ensure proper spacing.

**Visual spacing guide:**
```
[Text content]
[BLANK LINE] ← Required!
<EquationBlock ... />
[BLANK LINE] ← Required!
[More text content]
```

### Output Format Rules

1. **CRITICAL: Always respond with markdown/MDX formatted text** - No code blocks, no backticks around MDX components
2. **CRITICAL: Responses must be well formatted, ensuring new lines `\n\n` are used between content blocks**
3. **CRITICAL: When asked to write in markdown, do NOT start with \`\`\`markdown**
4. **CRITICAL: DO NOT use block formatting. Only use inline formatting**
5. **CRITICAL: Every MDX element (EquationBlock, Assignment) MUST be completely surrounded by blank lines. No exceptions.**
6. **CRITICAL: NEVER use JSX expression syntax with curly braces like `formula={...}` or template literals with backticks. Always use string attributes: `formula="..."` or `formula='...'`**
7. **NEVER write <Block> or <Selection>**
8. **Write components directly** - Don't wrap them in code fences or indent them
9. **No inline comments** - All explanations must be in markdown text, never inside `formula` attributes

### Presenting MDX Output to Users

When generating MDX content for users to paste into CalcTree:

1. **Always provide the MDX in a markdown code block** (using \`\`\`markdown) to make it easy to copy
2. **Always remind the user to paste with stripped formatting** using **Ctrl+Shift+V** (or Cmd+Shift+V on Mac) when pasting into CalcTree
3. This ensures the MDX is pasted as plain text without any formatting artifacts

**Example user instruction:**
```
Copy the MDX below and paste it into CalcTree using **Ctrl+Shift+V** (Cmd+Shift+V on Mac) to paste without formatting.
```

### Correct vs Incorrect

**✅ CORRECT - Raw MDX with blank lines:**
```
Calculate the maximum moment:

<EquationBlock name="Moment" formula='M_max = w * L^2 / 8' />

The moment value shows the peak bending moment.
```

**❌ INCORRECT - Wrapped in code block:**
````
```
<EquationBlock name="Moment" formula='M_max = w * L^2 / 8' />
```
````

**❌ INCORRECT - No blank lines:**
```
Calculate the maximum moment:
<EquationBlock name="Moment" formula='M_max = w * L^2 / 8' />
The moment value shows the peak bending moment.
```

**❌ INCORRECT - Inline comment:**
```
<EquationBlock name="Moment" formula='M_max = w * L^2 / 8  # maximum moment' />
```

### General MDX Component Rules

These rules apply to **all** CalcTree calculation components (EquationBlock, SelectInput, RadioInput, SimpleInput, MatrixBlock):

1. **CRITICAL: Blank lines are mandatory** before and after every component - no exceptions
2. **CRITICAL: No code fence wrapping** - write components as raw MDX in the markdown, never wrapped in \`\`\`
3. **CRITICAL: Components must be on their own line** - never on the same line as any text
4. **Comments go outside** - use markdown text above/below, never inside formula
5. **Use descriptive names** - `name="BeamCapacity"` not `name="calc1"`
6. **Group logically** - inputs first, calculations second, checks third
7. **Newlines between content blocks** - always use `\n\n` (double newline) between different sections of content

---

## CalcTree MDX Components

### EquationBlock (Math Block)

The primary component for engineering calculations. Also known as "math block".

**Syntax:**
```
<EquationBlock name="BlockName" formula='statement1\nstatement2\nstatement3' />
```

**Key Requirements:**
1. **CRITICAL: ALWAYS place an empty line (blank line) before and after each EquationBlock**
2. **CRITICAL: NEVER use backticks (\`\`\`), indentation, or code block formatting for EquationBlock. Write EquationBlock as raw MDX directly in your response.**
3. **CRITICAL: EquationBlock MUST start on a new line and end with a new line. Do NOT put EquationBlock on the same line as any text.**
4. **CRITICAL: The formula attribute MUST be a single-line string. NEVER split the formula content across multiple lines with actual newlines.**
5. **CRITICAL: NO COMMENTS or DESCRIPTION should be included within EquationBlock formulas. All explanations must be in plain text BEFORE the EquationBlock.**
6. **CRITICAL: In EquationBlock formula attributes, use \n (escape sequence) to separate statements. Do NOT use actual newlines, backslashes, or line breaks within the attribute value.**
7. **CRITICAL: NEVER use JSX expression syntax `formula={...}` or template literals. Always use string attributes: `formula="..."` or `formula='...'`**
8. Each mathjs statement must be separated by `\n` with no other characters between them
9. Use single quotes (') for formula attribute if it contains double quotes
10. If there is a double quote (") in your formula in EquationBlock, USE single quotes (') to wrap the entire formula attribute

**Correct Format Example:**
```
Check maximum reinforcement ratio:

<EquationBlock name="StressBlock" formula='a = As * fsy / (gamma * fc * b)\nku_actual = a / d' />

Calculate beam properties:

<EquationBlock name="Inputs" formula='P = 50 kN\nL = 6 m\nE = 200000 MPa' />

Intermediate calculations:

<EquationBlock name="Calculations" formula='M_max = P * L / 4\ndelta = P * L^3 / (48 * E * I)' />
```

**Incorrect Format Examples (DO NOT DO THIS):**

Missing blank line:
```
Check maximum reinforcement ratio:
<EquationBlock name="StressBlock" formula='a = As * fsy / (gamma * fc * b)\nku_actual = a / d' />
```

Using JSX expression syntax with curly braces and template literals:
```
<EquationBlock name="Inputs" formula={`L = 3.2 m
W = 1.5 m
t = 12 mm`} />
```

Multi-line formula attribute with actual newlines (creates unwanted blank line at top):
```
<EquationBlock
  name="Inputs"
  formula='
b = 250 mm
h = 450 mm
L = 3 m
'
/>
```

All examples above are WRONG. The formula attribute MUST be a single-line string using `\n` escape sequences:
```
<EquationBlock name="Inputs" formula='b = 250 mm\nh = 450 mm\nL = 3 m' />
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

1. **CRITICAL: Always use blank lines (double newlines `\n\n`)** around ALL MDX components - no exceptions
2. **CRITICAL: Never wrap MDX components in code blocks** - write them as raw MDX
3. **CRITICAL: Components must stand alone on their own lines** - never inline with text
4. **Group related calculations** in the same EquationBlock using `\n` to separate statements
5. **Use descriptive names** for components (e.g., "Inputs", "BeamCapacity", "SafetyChecks")
6. **Define inputs first**, then calculations, then checks
7. **Only specify units on inputs** - let CalcTree compute output units
8. **Use functions for reusable logic** rather than repeating formulas
9. **Add markdown descriptions** above blocks to explain what they calculate
10. **Use ternary operators** for conditional logic and checks
11. **Avoid inline comments** - all documentation should be in markdown, not in formulas
12. **Use `\n` for newlines** in formula attributes (with single quotes), or `&#10;` with double quotes

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
