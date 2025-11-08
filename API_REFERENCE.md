# CalcTree GraphQL API Reference

Complete reference for the CalcTree GraphQL API.

**Endpoint:** `https://graph.calctree.com/graphql`

## Authentication

All requests require an API key in the `x-api-key` header:

```python
import requests

headers = {
    "Content-Type": "application/json",
    "x-api-key": "YOUR_API_KEY"
}

response = requests.post(
    "https://graph.calctree.com/graphql",
    headers=headers,
    json={"query": "...", "variables": {...}}
)
```

Get your API key from CalcTree workspace settings.

## Get Current User

Use this query to get your user ID (required for Python statements):

```graphql
query GetCurrentUser {
  currentUser {
    id
    email
    fullName
    workspaces {
      id
      name
      role
    }
  }
}
```

**Returns:**
```json
{
  "data": {
    "currentUser": {
      "id": "4d83c852-69a7-4744-8b7c-92d0335386c3",
      "email": "user@example.com",
      "fullName": "John Doe",
      "workspaces": [...]
    }
  }
}
```

**Note:** The `id` field is your `userId` - save this for creating Python statements.

## ID Format Requirements

**CRITICAL:** CalcTree uses **nanoid format** for all IDs, NOT UUIDs.

```python
from nanoid import generate

page_id = generate()  # Returns: "gxZe018G5BDFM6fpizSgS" (21 chars)
```

**Characteristics:**
- 21 characters long
- Alphanumeric + underscore (`_`) or hyphen (`-`)
- Example: `9Ui8lEJAc6rXv3dS0P-s0`

**Installation:**
```bash
pip install nanoid
```

## Core Mutations

### 1. Create Page

Creates a new page in the workspace.

```graphql
mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
  createPageSync(workspaceId: $workspaceId, input: $input) {
    id
    title
  }
}
```

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "input": {
    "id": "gxZe018G5BDFM6fpizSgS",
    "title": "Beam Analysis",
    "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04"
  }
}
```

**Required Fields:**
- `id` (ID!) - nanoid format, you must generate
- `title` (String!) - page title
- `workspaceId` (ID!) - same as mutation parameter

**Returns:** `{ id, title }`

---

### 2. Add Page to Tree

**CRITICAL:** This must be called after `createPageSync` or the page won't appear in the page tree.

```graphql
mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
  addPageNode(workspaceId: $workspaceId, input: $input) {
    newPageId
    parentId
  }
}
```

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "input": {
    "pageId": "gxZe018G5BDFM6fpizSgS"
  }
}
```

**Required Fields:**
- `pageId` (ID!) - the page ID from createPageSync

**Optional Fields:**
- `parentId` (ID) - parent page ID (omit for root level)

**Returns:** `{ newPageId, parentId }`

---

### 3. Create Calculation (Single Statement)

Creates a calculation with one statement.

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

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "calculationId": "gxZe018G5BDFM6fpizSgS",
  "withStatement": {
    "statementId": "stmt_nanoid_here",
    "title": "beam_length",
    "engine": "mathjs",
    "formula": "beam_length = 10 m"
  },
  "data": {
    "pageId": "gxZe018G5BDFM6fpizSgS",
    "id": "data_nanoid_here",
    "cursor": "",
    "timestamp": 1234567890123
  }
}
```

**Required Parameters:**
- `workspaceId` (ID!) - workspace ID
- `calculationId` (ID!) - usually same as pageId
- `withStatement` (CreateStatementInput!) - the statement to create
- `data` (JSON!) - **MUST include `pageId`** to link to page

**Returns:** `{ calculationId, revisionId }`

---

### 4. Create/Update Calculation (Multiple Statements)

**RECOMMENDED:** Use this for creating calculations with multiple statements at once.

```graphql
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
```

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "calculationId": "gxZe018G5BDFM6fpizSgS",
  "withStatements": [
    {
      "statementId": "stmt1_nanoid",
      "title": "length",
      "engine": "mathjs",
      "formula": "length = 10 m"
    },
    {
      "statementId": "stmt2_nanoid",
      "title": "width",
      "engine": "mathjs",
      "formula": "width = 5 m"
    },
    {
      "statementId": "stmt3_nanoid",
      "title": "area",
      "engine": "mathjs",
      "formula": "area = length * width"
    }
  ],
  "data": {
    "pageId": "gxZe018G5BDFM6fpizSgS",
    "id": "data_nanoid_here",
    "cursor": "0",
    "timestamp": 1234567890123
  }
}
```

**Required Parameters:**
- `workspaceId` (ID!)
- `calculationId` (ID!) - set to pageId
- `withStatements` ([CreateStatementInput!]!) - array of statements
- `data` (JSON!) - **MUST include `pageId`**

**Returns:** `{ calculationId, revisionId }`

---

### 5. Add Statement to Calculation

Adds a statement to an existing calculation.

```graphql
mutation AddStatement($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
  addStatementToCalculation(
    workspaceId: $workspaceId
    calculationId: $calculationId
    revisionId: $revisionId
    withStatement: $withStatement
    data: $data
  ) {
    calculationId
    revisionId
  }
}
```

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "calculationId": "gxZe018G5BDFM6fpizSgS",
  "revisionId": "ffffffff",
  "withStatement": {
    "statementId": "stmt_nanoid_here",
    "title": "load",
    "engine": "mathjs",
    "formula": "load = 5 kN"
  },
  "data": {
    "id": "data_nanoid_here",
    "cursor": "",
    "timestamp": 1234567890123,
    "statementId": "stmt_nanoid_here"
  }
}
```

**Required Parameters:**
- `workspaceId` (ID!)
- `calculationId` (ID!)
- `revisionId` (ID!) - use `"ffffffff"` even though API returns null
- `withStatement` (CreateStatementInput!)
- `data` (JSON)

**Note:** For Python statements, include `userId` in `data` field.

**Returns:** `{ calculationId, revisionId }`

---

## CreateStatementInput Type

```graphql
input CreateStatementInput {
  statementId: ID!      # nanoid format
  title: String!        # Display name (appears in UI sidebar)
  engine: String!       # "mathjs", "multiline_mathjs", or "python"
  formula: String!      # The formula (see CALCULATION_GUIDE.md for syntax)
}
```

**Engine Types:**
- `"mathjs"` - Single statement with units
- `"multiline_mathjs"` - Multiple statements (use `\n` separator)
- `"python"` - Python code

**Formula Syntax:**
- MathJS: `variable_name = value units` (e.g., `beam_length = 10 m`)
- Multiline MathJS: `var1 = value1\nvar2 = value2\nvar3 = var1 * var2`
- Python: Standard Python code

See [CALCULATION_GUIDE.md](CALCULATION_GUIDE.md) for detailed syntax rules.

---

## Common Queries

### Get Calculation

```graphql
query GetCalc($workspaceId: ID!, $calculationId: ID!, $revisionId: ID!) {
  calculation(
    workspaceId: $workspaceId
    calculationId: $calculationId
    revisionId: $revisionId
  ) {
    statements {
      title
      engine
      formula
      value
      error
    }
  }
}
```

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "calculationId": "gxZe018G5BDFM6fpizSgS",
  "revisionId": "ffffffff"
}
```

**Note:** Queries with Python statements may return "Not Authorised!" errors, but the statements ARE created successfully.

---

### Get Current User

```graphql
query {
  currentUser {
    id
    email
    name
  }
}
```

---

### Get Workspace

```graphql
query GetWorkspace($workspaceId: ID!) {
  workspace(workspaceId: $workspaceId) {
    id
    name
    pages {
      id
      title
    }
  }
}
```

---

## Data Field Structure

The `data` field is JSON with these common patterns:

### For createCalculation / createOrUpdateCalculation:
```json
{
  "pageId": "page_nanoid",         // CRITICAL - links to page
  "id": "data_nanoid",             // unique nanoid
  "cursor": "0",                   // "0" for new, or previous revision
  "timestamp": 1234567890123       // Unix timestamp in milliseconds
}
```

### For addStatementToCalculation:
```json
{
  "id": "data_nanoid",
  "cursor": "",                    // empty string
  "timestamp": 1234567890123,
  "statementId": "stmt_nanoid"     // same as withStatement.statementId
}
```

### For Python statements (additional field):
```json
{
  "id": "data_nanoid",
  "cursor": "",
  "timestamp": 1234567890123,
  "statementId": "stmt_nanoid",
  "userId": "user_id_here"         // REQUIRED for Python
}
```

---

## Page URLs

After creating a page, the URL format is:

```
https://app.calctree.com/edit/{workspaceId}/{pageId}
```

---

## Error Handling

Common errors and solutions:

### "Not Authorised!"
- For Python statement queries: This is expected - statements ARE created successfully
- For other operations: Check API key permissions

### Page not appearing in tree
- **Solution:** Call `addPageNode` after `createPageSync`

### Calculation not showing on page
- **Solution:** Include `data: { pageId }` when creating calculation

### Invalid ID format
- **Solution:** Use nanoid format, not UUIDs

### revisionId is null
- **Expected behavior** - use `"ffffffff"` for operations

---

## File Management

### Upload File to Workspace

File uploads require a 3-step process: get presigned URL → upload to S3 → register file in workspace.

**Step 1: Get Presigned Upload URL**

```graphql
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
```

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "fileName": "beam_data.csv",
  "contentType": "text/csv"
}
```

**Common Content Types:**
- CSV: `text/csv`
- Excel: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- PDF: `application/pdf`
- Image: `image/png`, `image/jpeg`
- JSON: `application/json`

**Response:**
```json
{
  "data": {
    "createPresignedUploadPost": {
      "url": "https://s3.amazonaws.com/...",
      "fields": {
        "key": "workspace-id/file-key",
        "policy": "...",
        "signature": "..."
      },
      "key": "workspace-id/file-key"
    }
  }
}
```

**Step 2: Upload File to S3**

Use HTTP POST with the presigned URL and fields:

```python
import requests

# From step 1 response
presigned_data = response['data']['createPresignedUploadPost']
s3_url = presigned_data['url']
fields = presigned_data['fields']
file_key = presigned_data['key']

# Upload file
with open('beam_data.csv', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post(s3_url, data=fields, files=files)

# Check success (should be 204)
if upload_response.status_code in [200, 204]:
    print("✓ File uploaded to S3")
```

**Step 3: Register File in Workspace**

```graphql
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
```

**Variables:**
```json
{
  "workspaceId": "98ea9cce-909a-44e9-9359-be53c3d67d04",
  "key": "workspace-id/file-key",
  "fileName": "beam_data.csv",
  "contentType": "text/csv",
  "size": 12345
}
```

**Response:**
```json
{
  "data": {
    "addWorkspaceFile": {
      "id": "file_id_here",
      "fileName": "beam_data.csv",
      "url": "https://..."
    }
  }
}
```

---

### Get Page Files

Query files attached to a specific page:

```graphql
query GetPageFiles($workspaceId: ID!, $pageId: ID!) {
  pageFiles(workspaceId: $workspaceId, pageId: $pageId) {
    id
    fileName
    contentType
    size
    url
    createdAt
  }
}
```

---

### Get File Details

```graphql
query GetFile($id: ID!) {
  pageFile(id: $id) {
    id
    fileName
    contentType
    size
    url
    pageId
  }
}
```

---

### Access Files in Python

Once uploaded, files can be accessed in Python statements using `ct.open()`:

```python
# Read CSV file uploaded to workspace
data = ct.open('beam_data.csv', mode='r').read()

# Parse CSV with pandas
import pandas as pd
import io

csv_content = ct.open('beam_data.csv', mode='r').read()
df = pd.read_csv(io.StringIO(csv_content))

# Work with data
max_load = df['load'].max()
print(f'Maximum load: {max_load}')
```

**Note:** Files must be uploaded to the workspace before they can be accessed with `ct.open()`.

---

## Best Practices

1. **Always call addPageNode** after createPageSync
2. **Always include data.pageId** when creating calculations
3. **Use calculationId = pageId** to link calculation to page
4. **Generate all IDs with nanoid** before making requests
5. **Use createOrUpdateCalculation** for multi-statement calculations
6. **Use revisionId: "ffffffff"** for operations
7. **Include userId in data** for Python statements
8. **Verify in UI** when query returns authorization errors

---

## Complete Workflow

```python
from nanoid import generate
import requests
import time

WORKSPACE_ID = "your-workspace-id"
API_KEY = "your-api-key"
ENDPOINT = "https://graph.calctree.com/graphql"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

def execute(query, variables):
    return requests.post(ENDPOINT, headers=HEADERS,
                        json={"query": query, "variables": variables}).json()

# 1. Create page
page_id = generate()
execute("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) { id }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {"id": page_id, "title": "My Page", "workspaceId": WORKSPACE_ID}
})

# 2. Add to tree
execute("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) { newPageId }
    }
""", {"workspaceId": WORKSPACE_ID, "input": {"pageId": page_id}})

# 3. Create calculation
execute("""
    mutation CreateCalc($workspaceId: ID!, $calculationId: ID!, $withStatements: [CreateStatementInput!]!, $data: JSON) {
      createOrUpdateCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatements: $withStatements
        data: $data
      ) { calculationId }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatements": [
        {"statementId": generate(), "title": "length", "engine": "mathjs", "formula": "length = 10 m"}
    ],
    "data": {"pageId": page_id, "id": generate(), "cursor": "0", "timestamp": int(time.time() * 1000)}
})

print(f"https://app.calctree.com/edit/{WORKSPACE_ID}/{page_id}")
```

See [EXAMPLES.md](EXAMPLES.md) for more complete examples.
