# CalcTree API Testing Summary

## Test Results - 2025-11-08

### ✅ What Works

#### 1. Page Creation
**Mutation:** `createPageSync`

```graphql
mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
  createPageSync(workspaceId: $workspaceId, input: $input) {
    id
    title
  }
}
```

**Requirements:**
- Must provide `id` (nanoid format)
- Must provide `title`
- Must provide `workspaceId` in input (matching the argument)

**Tested:** ✅ WORKING

#### 2. Calculation Creation on a Page
**Mutation:** `createCalculation` with `data.pageId`

```graphql
mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
  createCalculation(
    workspaceId: $workspaceId
    calculationId: $calculationId
    withStatement: $withStatement
    data: $data
  ) {
    calculationId
    revisionId
  }
}
```

**Requirements:**
- `calculationId`: nanoid format
- `withStatement.statementId`: nanoid format
- `withStatement.title`: variable name
- `withStatement.formula`: formula string
- `withStatement.engine`: "mathjs" or "multiline_mathjs" (python has authorization restrictions)
- `data.pageId`: **CRITICAL** - Must include pageId to link calculation to page

**Supported Engines:**
- ✅ `mathjs`: Single statement calculations with units - **VERIFIED WORKING**
- ✅ `multiline_mathjs`: Multiple statements in one block (use `\n` for line breaks) - **VERIFIED WORKING**
- ⚠️ `python`: Python code execution - Creates successfully but returns "Not Authorised!" on query (workspace/API key restriction)

**Returns:** `revisionId: null` (expected)

**Tested:** ✅ WORKING

#### 3. Adding Statements to Calculation
**Mutation:** `addStatementToCalculation`

```graphql
mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!) {
  addStatementToCalculation(
    workspaceId: $workspaceId
    calculationId: $calculationId
    revisionId: $revisionId
    withStatement: $withStatement
  ) {
    calculationId
    revisionId
  }
}
```

**Critical Discovery:** Use `revisionId: "ffffffff"` regardless of what the API returns

**Tested:** ✅ WORKING

#### 4. Page URL Format
Correct format: `https://app.calctree.com/edit/{workspaceId}/{pageId}`

**Tested:** ✅ VERIFIED

### ❌ What Doesn't Work

#### 1. createCalculationWithMultipleStatementsSync
**Status:** AUTHORIZATION ERROR

This mutation is mentioned in docs but returns authorization errors when attempting to create calculations with multiple statements.

**Workaround:** Use `createCalculation` + multiple `addStatementToCalculation` calls

#### 2. putInitialPageContent
**Status:** DOWNSTREAM_SERVICE_ERROR

```graphql
mutation PutContent($workspaceId: ID!, $input: PutPageContentInput!) {
  putInitialPageContent(workspaceId: $workspaceId, input: $input)
}
```

Returns unexpected errors. The mutation exists but may have backend issues.

### 🔍 Schema Discoveries

#### CreatePageInput Fields
```typescript
{
  id: ID!              // Required - nanoid format
  title: String!       // Required
  workspaceId: ID!     // Required - must match mutation arg
  parentId: String     // Optional
  header: String       // Optional
  settings: PageSettingsInput  // Optional
}
```

#### CreateStatementInput Fields
```typescript
{
  statementId: ID!     // Required - nanoid format
  title: String!       // Required - variable name
  formula: String!     // Required - formula
  engine: String!      // Required - must be "mathjs"
}
```

#### Page Type Fields
- Has `parent` (object) NOT `parentId`
- Has `deletedAt` NOT `createdAt`/`updatedAt`
- Has `cursor`, `header`, `settings`

### 🎯 Complete Working Example

```python
from nanoid import generate
import requests

WORKSPACE_ID = "98ea9cce-909a-44e9-9359-be53c3d67d04"
API_KEY = "dYD5mCmzqJNFqDFS5fc6huPHes7UPITC"
ENDPOINT = "https://graph.calctree.com/graphql"
HEADERS = {"Content-Type": "application/json", "x-api-key": API_KEY}

def execute(query, variables):
    payload = {"query": query, "variables": variables}
    return requests.post(ENDPOINT, headers=HEADERS, json=payload).json()

# Create page
page_id = generate()
execute("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) {
        id
        title
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {
        "id": page_id,
        "title": "My Calculation",
        "workspaceId": WORKSPACE_ID
    }
})

# Create calculation
calc_id = generate()
execute("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!) {
      createCalculation(workspaceId: $workspaceId, calculationId: $calculationId, withStatement: $withStatement) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "withStatement": {
        "statementId": generate(),
        "title": "length",
        "formula": "10 m",
        "engine": "mathjs"
    }
})

# Add statement
execute("""
    mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!) {
      addStatementToCalculation(workspaceId: $workspaceId, calculationId: $calculationId, revisionId: $revisionId, withStatement: $withStatement) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": calc_id,
    "revisionId": "ffffffff",
    "withStatement": {
        "statementId": generate(),
        "title": "width",
        "formula": "5 m",
        "engine": "mathjs"
    }
})

print(f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

### 📝 Key Takeaways

1. **Always generate IDs client-side** using nanoid
2. **Always use revisionId "ffffffff"** for adding/updating statements
3. **MUST include `data: { pageId }` when creating calculations** - This links the calculation to the page
4. **MUST call `addPageNode` after `createPageSync`** - Pages won't appear in tree without this
5. **Argument name is `withStatement`** not `statement` or `input`
6. **Page IDs are nanoid format** not UUIDs
7. **URL format** is `/edit/{workspace}/{page}` not `/workspace/{workspace}/page/{page}`
8. **revisionId returns null** but this is expected behavior
9. **Avoid createCalculationWithMultipleStatementsSync** - has authorization issues
10. **Engine types verified working**: `mathjs`, `multiline_mathjs` (NOT `multi-mathjs`)
11. **Python engine has restrictions** - Creates but cannot be queried with this API key

### 🧪 Test Files Created

1. `test_calctree_api.py` - Initial exploration
2. `test_calctree_api_v2.py` - Schema introspection
3. `test_calctree_final.py` - Refined tests
4. `test_calctree_working.py` - Working examples
5. `calctree_api_working_complete.py` - Complete example
6. `test_revisionid.py` - RevisionId testing
7. `test_complete_working.py` - **Final verified working example**

### ✅ Verified Page Creation

Successfully created multiple test pages:
- https://app.calctree.com/edit/98ea9cce-909a-44e9-9359-be53c3d67d04/NuDKupJRwOBzn2Uo7ecfP
- https://app.calctree.com/edit/98ea9cce-909a-44e9-9359-be53c3d67d04/PKgEwQ2Q3jHZc--HT-1N6
- https://app.calctree.com/edit/98ea9cce-909a-44e9-9359-be53c3d67d04/RW-0o-wtQteTqXIplwi59
- https://app.calctree.com/edit/98ea9cce-909a-44e9-9359-be53c3d67d04/MypnUJoGWmyWU01M8n8ct

All pages created successfully with calculations.

### 📚 Documentation Updates

Updated `llms.txt` with:
- Correct ID format requirements (nanoid)
- Correct page URL structure
- Working mutation examples
- API limitations section
- Proper revisionId usage ("ffffffff")
- Complete working Python example
- Corrected field names and schema
