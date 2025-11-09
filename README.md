# CalcTree API Documentation

Complete documentation for the CalcTree GraphQL API - create engineering calculations programmatically with support for MathJS, Python, and multi-statement calculations with automatic unit handling.

## Quick Start

```python
from nanoid import generate
import requests

WORKSPACE_ID = "your-workspace-id"
API_KEY = "your-api-key"
ENDPOINT = "https://graph.calctree.com/graphql"

# 1. Create page
page_id = generate()
requests.post(ENDPOINT,
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={"query": """
        mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
          createPageSync(workspaceId: $workspaceId, input: $input) { id }
        }
    """, "variables": {
        "workspaceId": WORKSPACE_ID,
        "input": {"id": page_id, "title": "My Calculation", "workspaceId": WORKSPACE_ID}
    }}
)

# 2. Add to page tree (CRITICAL - don't skip!)
requests.post(ENDPOINT,
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={"query": """
        mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
          addPageNode(workspaceId: $workspaceId, input: $input) { newPageId }
        }
    """, "variables": {
        "workspaceId": WORKSPACE_ID,
        "input": {"pageId": page_id}
    }}
)

# 3. Add calculation
requests.post(ENDPOINT,
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={"query": """
        mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
          createOrUpdateCalculation(
            workspaceId: $workspaceId
            calculationId: $calculationId
            withStatements: $withStatements
            data: $data
          ) { calculationId }
        }
    """, "variables": {
        "workspaceId": WORKSPACE_ID,
        "calculationId": page_id,  # Use page_id as calculation_id
        "withStatements": [{
            "statementId": generate(),
            "title": "beam_length",
            "engine": "mathjs",
            "formula": "beam_length = 10 m"  # MUST include variable assignment
        }],
        "data": {
            "pageId": page_id,  # CRITICAL - links calculation to page
            "id": generate(),
            "cursor": "0",
            "timestamp": int(time.time() * 1000)
        }
    }}
)

print(f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

## Documentation Structure

### Core Guides
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete GraphQL schema, mutations, queries, and required fields
- **[CALCULATION_GUIDE.md](CALCULATION_GUIDE.md)** - Formula syntax, variable scoping, units, and engine types
- **[PYTHON_GUIDE.md](PYTHON_GUIDE.md)** - Pre-installed libraries (26+ packages) and Python-specific examples
- **[MDX_SYNTAX.md](MDX_SYNTAX.md)** - Page content syntax with MDX components and markdown elements
- **[EXAMPLES.md](EXAMPLES.md)** - Copy-paste ready code examples
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common mistakes and solutions

## Key Concepts

### Two Critical Requirements

**#1: Always call `addPageNode` after creating a page**
```python
# Step 1: Create page
createPageSync(...)

# Step 2: Add to tree (REQUIRED!)
addPageNode(...)  # Page won't appear without this
```

**#2: Always include `data.pageId` when creating calculations**
```python
createOrUpdateCalculation(
    calculationId: page_id,
    withStatements: [...],
    data: {
        pageId: page_id,  # CRITICAL - without this, calculation won't link to page
        ...
    }
)
```

### Formula Syntax

MathJS formulas **MUST** include variable assignment:

✅ **Correct:** `beam_length = 10 m`
❌ **Wrong:** `10 m`

### Variable Scoping

All statements in a calculation share the same scope:

```javascript
// Statement 1
length = 10 m

// Statement 2
width = 5 m

// Statement 3 - references Statement 1 and 2
area = length * width  // This works!
```

### Engine Types

- `"mathjs"` - Single variable assignment with units
- `"multiline_mathjs"` - Multiple statements (separated by `\n`)
- `"python"` - Python code (requires `userId` in data field)

## ID Format

All IDs use **nanoid format** (21 characters: alphanumeric + `_` or `-`), **NOT** UUIDs:

```python
from nanoid import generate

page_id = generate()  # Returns: "9Ui8lEJAc6rXv3dS0P-s0"
```

## GraphQL Endpoint

```
https://graph.calctree.com/graphql
```

**Headers:**
```json
{
  "Content-Type": "application/json",
  "x-api-key": "your-api-key"
}
```

## Getting Started

1. Install dependencies: `pip install nanoid requests`
2. Get your API key from CalcTree workspace settings
3. Get your workspace ID from the URL: `https://app.calctree.com/edit/{workspace-id}/...`
4. Try the Quick Start example above
5. Check [EXAMPLES.md](EXAMPLES.md) for more complete examples

## Resources

- **Official CalcTree Docs**: https://calctree.gitbook.io/docs
- **CalcTree Website**: https://www.calctree.com
- **GraphQL Endpoint**: https://graph.calctree.com/graphql

## Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for:
- Pages not appearing in tree → Missing `addPageNode`
- Calculations not showing on page → Missing `data.pageId`
- Wrong formula syntax → Must use `variable = value`
- ID format errors → Use nanoid, not UUID
- Python authorization errors → Query limitation (statements are created successfully)
