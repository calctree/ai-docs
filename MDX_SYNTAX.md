# CalcTree MDX Syntax Guide

Complete reference for writing CalcTree page content with MDX components and markdown.

---

## CRITICAL INSTRUCTIONS FOR CHATGPT

**READ THIS FIRST - THIS IS MANDATORY:**

When you generate MDX content for CalcTree in a chat interface, your response MUST follow this exact format:

1. First line: Paste instruction
2. Second line: Opening code fence ````markdown`
3. The actual MDX content (components, markdown, etc.)
4. Last line: Closing code fence ````

**YOUR COMPLETE RESPONSE STRUCTURE:**
```
Copy the code below and paste into CalcTree using Ctrl+Shift+V (Cmd+Shift+V on Mac).

```markdown
# Calculation Title

<EquationBlock name="Inputs" formula='x = 5 m\ny = 10 m' />

<EquationBlock name="Results" formula='area = x * y' />
```
```

**CRITICAL RULES:**
- The ONLY calculation component is `<EquationBlock>` - NOT `<MathBlock>`, NOT `<Assignment>`
- Use `formula='...'` as a STRING attribute - NOT `statements={...}` with JSX
- DO NOT output raw MDX without the code fence wrapper

---

## Overview

CalcTree uses MDX (Markdown + JSX) for page content, combining standard markdown with custom calculation components. The markdown engine is based on PlateJS for standard elements, with CalcTree-specific components for calculations and inputs.

---

## Critical Rules for AI Agents

**⚠️ IMPORTANT: The ONLY calculation component is `<EquationBlock>`. There is NO `<Assignment>` component. All calculations must use `<EquationBlock>`.**

### 1. Output Format

**CRITICAL: How to present MDX depends on the context:**

**If responding in a chat interface (ChatGPT, Claude chat, etc.):**
- **ALWAYS wrap the ENTIRE MDX output in a markdown code fence** (````markdown ... ````)
- This is REQUIRED for chat interfaces - do not skip this step
- Include the paste instruction before the code block
- The code block makes it easy for users to copy the content

**Example for chat interfaces:**

---

Copy the code below and paste into CalcTree using **Ctrl+Shift+V** (Cmd+Shift+V on Mac) to paste without formatting.

````markdown
# Your Calculation Title

<EquationBlock name="Inputs" formula='x = 5 m\ny = 10 m' />

<EquationBlock name="Results" formula='area = x * y' />
````

---

**If responding in a coding tool (Claude Code, Cursor, etc.):**
- Provide the raw MDX directly without wrapping in code fences
- The user can copy it directly from the response

**Example for coding tools:**

---

Copy the text below and paste into CalcTree using **Ctrl+Shift+V** (Cmd+Shift+V on Mac) to paste without formatting.

# Your Calculation Title

<EquationBlock name="Inputs" formula='x = 5 m\ny = 10 m' />

<EquationBlock name="Results" formula='area = x * y' />

---

**Key rule for BOTH contexts:**
- Individual MDX components are NEVER wrapped in code blocks within the actual content
- The entire content (if using a code fence) is wrapped once, not each component separately

### 2. Blank Lines Around Components

**CRITICAL:** Every MDX component (EquationBlock, SelectInput, RadioInput, SimpleInput, MatrixBlock) MUST be:
- Preceded by a blank line
- Followed by a blank line
- Written on its own line, never inline with text

```
[Text content]
[BLANK LINE] ← Required
<EquationBlock ... />
[BLANK LINE] ← Required
[More text content]
```

This is the #1 most common mistake.

### 3. Formula Attribute Syntax

**Two supported patterns for `formula` attributes:**

**Pattern 1: Single-line with `\n` escape sequences** (recommended)
```
<EquationBlock name="Inputs" formula='L = 5 m\nB = 2 m\nt = 12 mm' />
```

**Pattern 2: Multi-line with actual newlines**
```
<EquationBlock name="Inputs" formula='L = 5 m
B = 2 m
t = 12 mm
' />
```

**CRITICAL rules for both patterns:**
- The first statement MUST appear on the SAME line as `formula='` (no newline after the opening quote)
- NEVER use JSX expression syntax: `formula={...}` or template literals with backticks
- NEVER use inline comments within formulas
- Always use string attributes: `formula="..."` or `formula='...'`

**WRONG - Creates blank line at top:**
```
<EquationBlock name="Inputs" formula='
L = 5 m
B = 2 m
' />
```

**CORRECT:**
```
<EquationBlock name="Inputs" formula='L = 5 m
B = 2 m
' />
```

### 4. Chaining & Scope

**All EquationBlocks in a page share the same calculation scope.** Variables defined in one block are automatically available in later blocks.

```
<EquationBlock name="Inputs" formula='L = 5 m\nB = 2 m' />

<EquationBlock name="Results" formula='A = L * B\nP = 2 * (L + B)' />
```

Variables `L` and `B` from the first block are used in the second block without re-declaring.

### 5. Units: Inputs Only

- **INPUT variables:** Always include units (e.g., `P = 50 kN`)
- **CALCULATED variables:** Never include units - they're computed automatically (e.g., `M_max = P * L / 4`)
- **Unit conversions:** Use the `to` operator (e.g., `A_mm2 = A to mm^2`)

**Example:**
```
<EquationBlock name="Inputs" formula='P = 50 kN\nL = 6 m' />

<EquationBlock name="Calculations" formula='M_max = P * L / 4\nM_kNm = M_max to kN*m' />
```

### 6. JSX Expressions vs String Attributes

**Important distinction:**
- `formula` attribute: **Always a string** (`formula="..."` or `formula='...'`) - NEVER use `{}`
- `decimal` attribute in SimpleInput/MatrixBlock: **Always a JSX expression** (`decimal={2}`) - ALWAYS use `{}`

**Example:**
```
<SimpleInput name="teamSize" format="general" decimal={0} description="Team Size" formula="teamSize=5" />
```

### 7. No Comments Inside Formulas

All explanatory text must be in markdown above or below components, never inside `formula` attributes.

**WRONG:**
```
<EquationBlock name="Moment" formula='M_max = w * L^2 / 8  # maximum moment' />
```

**CORRECT:**
```
Calculate the maximum moment:

<EquationBlock name="Moment" formula='M_max = w * L^2 / 8' />
```

---

## CalcTree MDX Components

### EquationBlock

The primary component for engineering calculations.

**Syntax:**
```
<EquationBlock name="BlockName" formula='statement1\nstatement2\nstatement3' />
```

**Attributes:**
- `name` - Descriptive name for the block (e.g., "Inputs", "BeamCapacity", "Checks")
- `formula` - String containing mathjs statements separated by `\n` or actual newlines

**Example:**
```
Calculate beam properties:

<EquationBlock name="Inputs" formula='P = 50 kN\nL = 6 m\nE = 200000 MPa\nI = 300e6 mm^4' />

Determine maximum moment and deflection:

<EquationBlock name="Results" formula='M_max = P * L / 4\ndelta_max = (P * L^3) / (48 * E * I)' />
```

**Conditional checks:**
```
<EquationBlock name="Checks" formula='utilization = demand / capacity\nstatus = utilization <= 1.0 ? "PASS" : "FAIL"' />
```

### SelectInput

Dropdown selection input.

**Syntax:**
```
<SelectInput name="variableName" description="Label" formula='variableName=ctselect(["Option1", "Option2"], "Default")' />
```

**Example:**
```
<SelectInput name="memberType" description="Member Type" formula='memberType=ctselect(["Beam", "Column", "Slab"], "Beam")' />
```

### RadioInput

Radio button selection input.

**Syntax:**
```
<RadioInput name="variableName" description="Label" formula='variableName=ctselect(["Option1", "Option2"], "Default")' />
```

**Example:**
```
<RadioInput name="loadType" description="Load Type" formula='loadType=ctselect(["Dead", "Live", "Wind"], "Dead")' />
```

### SimpleInput

Single numeric input field.

**Syntax:**
```
<SimpleInput name="variableName" format="general" decimal={0} description="Label" formula="variableName=defaultValue" />
```

**Attributes:**
- `name` - Variable name
- `format` - Number format ("general", "decimal", etc.)
- `decimal` - Decimal places as JSX expression: `{0}`, `{2}`, etc.
- `description` - Label shown to user
- `formula` - Initial value assignment (string attribute)

**Example:**
```
<SimpleInput name="teamSize" format="general" decimal={0} description="Team Size" formula="teamSize=5" />
```

### MatrixBlock

Matrix/table input.

**Syntax:**
```
<MatrixBlock name="matrixName" format="general" decimal={2} description="Label" formula="matrixName=[[r1c1,r1c2],[r2c1,r2c2]]" />
```

**Example:**
```
<MatrixBlock name="loadMatrix" format="general" decimal={2} description="Load Matrix" formula="loadMatrix=[[10,20],[30,40]]" />
```

---

## Standard Markdown Elements

CalcTree supports standard markdown syntax via PlateJS:

### Headings
```
# Heading 1
## Heading 2
### Heading 3
```

### Text Formatting
```
**bold text**
_italic text_
_**bold and italic**_
~~strikethrough~~
`inline code`
```

### Links
```
[Link text](https://example.com)
```

### Images
```
![Alt text](image-url)
```

### Lists
```
- Unordered item
- Another item

1. Ordered item
2. Another item

- [x] Completed task
- [ ] Pending task
```

### Blockquotes
```
> This is a blockquote.
```

### Code Blocks
````
```python
def calculate_moment(load, length):
    return load * length / 4
```
````

### Tables
```
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Row 1    | Data     | More     |
| Row 2    | Data     | More     |
```

### Horizontal Rules
```
---
```

### LaTeX Math

**Block equations:**
```
$$
\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$
```

**Inline equations:**
```
The formula $E = mc^2$ shows energy equivalence.
```

### Columns

```
<column_group>
<column width="50%">Left column content</column>
<column width="50%">Right column content</column>
</column_group>
```

---

## MathJS Operations

CalcTree uses mathjs syntax:

- Arithmetic: `+`, `-`, `*`, `/`
- Exponentiation: `a^b` or `pow(a, b)`
- Functions: `sqrt(x)`, `abs(x)`, `sin(x)`, `cos(x)`, `tan(x)`
- Aggregates: `min(a, b, c)`, `max(a, b, c)`
- Conditionals: `condition ? valueIfTrue : valueIfFalse`
- String comparison: `equalText(str1, str2)`

---

## Document Structure

Organize calculations in three sections:

### 1. Inputs
```
## Design Parameters

<EquationBlock name="Inputs" formula='N_star = 1500 kN\nf_c = 32 MPa\nD = 400 mm\nB = 400 mm' />
```

### 2. Calculations
```
## Section Capacity

<EquationBlock name="Capacity" formula='A_g = B * D\nphi = 0.6\nN_uo = 0.85 * f_c * A_g\nphi_N_uo = phi * N_uo' />
```

### 3. Checks
```
## Design Check

<EquationBlock name="Check" formula='utilization = N_star / phi_N_uo\nstatus = utilization <= 1.0 ? "PASS" : "FAIL"' />
```

---

## Complete Example

```markdown
# Concrete Column Design to AS3600

## Design Parameters

<EquationBlock name="Inputs" formula='N_star = 1500 kN\nf_c = 32 MPa\nD = 400 mm\nB = 400 mm' />

## Section Capacity

Calculate gross area and capacity:

<EquationBlock name="Capacity" formula='A_g = B * D\nphi = 0.6\nN_uo = 0.85 * f_c * A_g\nphi_N_uo = phi * N_uo' />

## Design Check

<EquationBlock name="Check" formula='utilization = N_star / phi_N_uo\nstatus = utilization <= 1.0 ? "PASS" : "FAIL"' />

The column utilization is shown above.
```

---

## Variable Naming Rules

- Use underscores, not apostrophes: `f_c` not `f'c` (apostrophes cause errors in mathjs)
- Use descriptive names: `beam_length` not `L` (unless standard notation)
- No spaces in variable names
- String values must use double quotes: `type = "Steel"`

---

## Integration with API

When using the `putInitialPageContent` API, backslashes must be escaped in GraphQL strings (`\\n` instead of `\n`):

```graphql
mutation UpdatePageContent {
  putInitialPageContent(
    workspaceId: "workspace_id"
    input: {
      pageId: "page_id"
      markdown: "# Calculation\\n\\n<EquationBlock name='Inputs' formula='x = 5\\\\ny = 10' />\\n\\nResult shown above."
    }
  )
}
```

See [API_REFERENCE.md](API_REFERENCE.md) for complete API documentation.

---

## MDX Generation Checklist

Before finalizing generated MDX, verify:

- [ ] **If in chat interface (ChatGPT, Claude): ENTIRE output is wrapped in ````markdown ... ```` code fence**
- [ ] **If in coding tool (Claude Code): Output is raw MDX without code fence wrapper**
- [ ] All components have blank lines before AND after
- [ ] Formula attributes use string syntax (`formula='...'`), never JSX expressions (`formula={...}`)
- [ ] First statement in formula appears on same line as opening quote (no leading newline)
- [ ] No inline comments within formula attributes
- [ ] Units specified on inputs only, not on calculated variables
- [ ] Variable names use underscores, not apostrophes
- [ ] `decimal` attribute uses JSX expression syntax: `decimal={2}`, not `decimal="2"`
- [ ] Components are not wrapped in code blocks (in the actual MDX content)
- [ ] User instructions include: "Paste with Ctrl+Shift+V (Cmd+Shift+V on Mac)"

---

## Copy/Paste Instructions for Users

When presenting MDX to users, always include:

```
Copy the code below and paste into CalcTree using **Ctrl+Shift+V** (Cmd+Shift+V on Mac) to paste without formatting.
```

This ensures the MDX is pasted as plain text without formatting artifacts.
