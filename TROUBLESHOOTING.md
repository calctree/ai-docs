# CalcTree API Troubleshooting

Common issues and solutions when using the CalcTree GraphQL API.

## Top 2 Most Common Mistakes

### #1: Page Not Appearing in Page Tree

**Problem:** You created a page with `createPageSync` but it doesn't show up in the CalcTree UI.

**Cause:** Missing `addPageNode` mutation call.

**Solution:** Always call `addPageNode` immediately after `createPageSync`:

```python
# Step 1: Create page
page_id = generate()
execute_query("""
    mutation CreatePage($workspaceId: ID!, $input: CreatePageInput!) {
      createPageSync(workspaceId: $workspaceId, input: $input) { id }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {"id": page_id, "title": "My Page", "workspaceId": WORKSPACE_ID}
})

# Step 2: Add to tree (REQUIRED!)
execute_query("""
    mutation AddPageNode($workspaceId: ID!, $input: AddPageNodeInput!) {
      addPageNode(workspaceId: $workspaceId, input: $input) { newPageId }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "input": {"pageId": page_id}
})
```

---

### #2: Calculation Not Showing on Page

**Problem:** Calculation was created successfully but doesn't appear on the page.

**Cause:** Missing `pageId` in the `data` field.

**Solution:** Always include `data.pageId` when creating calculations:

```python
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
    "withStatements": [...],
    "data": {
        "pageId": page_id,  # CRITICAL - must include this!
        "id": generate(),
        "cursor": "0",
        "timestamp": int(time.time() * 1000)
    }
})
```

---

## Formula Syntax Errors

### Wrong MathJS Syntax

**Problem:** Formula doesn't work or displays incorrectly.

**Cause:** Missing variable assignment.

❌ **Wrong:**
```python
"formula": "10 m"  # Missing variable name
```

✅ **Correct:**
```python
"formula": "beam_length = 10 m"  # Includes variable assignment
```

**Rule:** MathJS formulas MUST use the format: `variable_name = value units`

---

## ID Format Errors

### UUID Instead of nanoid

**Problem:** API returns errors about invalid ID format.

**Cause:** Using UUIDs instead of nanoid format.

❌ **Wrong:**
```python
import uuid
page_id = str(uuid.uuid4())  # Returns: "550e8400-e29b-41d4-a716-446655440000"
```

✅ **Correct:**
```python
from nanoid import generate
page_id = generate()  # Returns: "gxZe018G5BDFM6fpizSgS"
```

**Installation:**
```bash
pip install nanoid
```

---

## Python Statement Issues

### "Not Authorised!" When Querying Python Calculations

**Problem:** Query returns authorization error for calculations with Python statements.

**Example:**
```json
{
  "errors": [{
    "message": "Not Authorised!",
    "path": ["calculation"],
    "extensions": {"code": "DOWNSTREAM_SERVICE_ERROR"}
  }]
}
```

**Cause:** API query limitation for Python statements.

**Solution:** This is expected behavior. The statement IS created successfully - verify by checking the page URL in your browser.

**Workaround:** Skip the query verification step for Python statements, just check the UI.

---

### Python Statement Not Appearing

**Problem:** Python statement created successfully via API but doesn't show in UI.

**Cause:** Missing `userId` in the `data` field.

**Solution:** Include `userId` when creating Python statements:

```python
USER_ID = "your-user-id"  # Get from network trace

execute_query("""
    mutation CreateCalculation($workspaceId: ID!, $calculationId: ID!, $withStatement: CreateStatementInput!, $data: JSON) {
      createCalculation(
        workspaceId: $workspaceId
        calculationId: $calculationId
        withStatement: $withStatement
        data: $data
      ) {
        calculationId
      }
    }
""", {
    "workspaceId": WORKSPACE_ID,
    "calculationId": page_id,
    "withStatement": {
        "statementId": generate(),
        "title": "Python Code",
        "engine": "python",
        "formula": "print('Hello')"
    },
    "data": {
        "id": generate(),
        "cursor": "",
        "timestamp": int(time.time() * 1000),
        "statementId": stmt_id,
        "userId": USER_ID  # REQUIRED for Python
    }
})
```

**How to get userId:** Check the network trace in browser DevTools when manually creating a Python block.

---

## Variable Scoping Issues

### Variable Not Found

**Problem:** Formula references a variable but gets "not found" error.

**Cause:** Variable is in a different calculation scope.

**Solution:** All variables must be in the same calculation (same `calculationId`):

✅ **Correct:**
```python
# All statements use the SAME calculationId
calculationId = page_id

statements = [
    {"formula": "length = 10 m"},
    {"formula": "width = 5 m"},
    {"formula": "area = length * width"}  # Can reference length and width
]
```

❌ **Wrong:**
```python
# Different calculationIds = different scopes
calc1: {"formula": "length = 10 m"}
calc2: {"formula": "area = length * width"}  # ERROR: length not found!
```

---

## Multiline MathJS Issues

### Newlines Not Working

**Problem:** Multiline formula appears as single line or doesn't parse correctly.

**Cause:** Using literal `\n` string instead of actual newline character.

❌ **Wrong:**
```python
"formula": "width = 300 mm\\nheight = 500 mm"  # Escaped backslash
```

✅ **Correct:**
```python
"formula": "width = 300 mm\nheight = 500 mm"  # Actual newline character
```

Or use triple quotes:
```python
"formula": """width = 300 mm
height = 500 mm
area = width * height"""
```

---

## RevisionId Issues

### Null RevisionId

**Problem:** API returns `revisionId: null`.

**Cause:** This is expected behavior.

**Solution:** Use `"ffffffff"` as revisionId for operations:

```python
execute_query("""
    mutation AddStatement(..., $revisionId: ID!, ...) {
      addStatementToCalculation(
        ...
        revisionId: $revisionId
        ...
      ) {
        calculationId
      }
    }
""", {
    ...
    "revisionId": "ffffffff",  # Use this even though API returns null
    ...
})
```

---

## Import Errors

### Python Library Not Found

**Problem:** `ImportError: No module named 'xyz'`

**Cause:** Library not pre-installed in CalcTree's Python environment.

**Solution:** Only use pre-installed libraries. See [PYTHON_GUIDE.md](PYTHON_GUIDE.md) for complete list:

✅ **Available:**
- numpy, scipy, pandas, matplotlib, seaborn
- anaStruct, OpenSeesPy, PyNite, sectionproperties
- handcalcs, SymPy, Scikit-learn
- (26+ total libraries)

❌ **Not available:**
- Custom packages not in the pre-installed list

---

## Unit Errors

### Incompatible Units

**Problem:** Error about incompatible units in MathJS.

**Example:** `10 m + 5 kg` → ERROR

**Cause:** MathJS prevents mathematically invalid unit operations.

**Solution:** Ensure unit compatibility:

✅ **Correct:**
```javascript
length1 = 10 m
length2 = 500 cm
total = length1 + length2  // Works - both are lengths
```

❌ **Wrong:**
```javascript
length = 10 m
mass = 5 kg
invalid = length + mass  // ERROR - can't add length and mass
```

**Unit conversion:**
```javascript
length_m = 3 m + 200 cm  // Returns: 5 m (auto converts)
length_ft = length_m to ft  // Explicit conversion
```

---

## Timestamp Issues

### Invalid Timestamp

**Problem:** Data field timestamp rejected.

**Cause:** Wrong timestamp format.

✅ **Correct:** Unix timestamp in milliseconds
```python
import time
timestamp = int(time.time() * 1000)  # 1234567890123
```

❌ **Wrong:** Unix timestamp in seconds
```python
timestamp = int(time.time())  # 1234567890 (too short)
```

---

## Authentication Errors

### Invalid API Key

**Problem:** `401 Unauthorized` or similar error.

**Solution:**
1. Verify API key in workspace settings
2. Check header format:
   ```python
   headers = {
       "Content-Type": "application/json",
       "x-api-key": "YOUR_API_KEY"  # Not "Authorization"
   }
   ```

---

## Debugging Tips

### 1. Check the Browser

Always verify pages in the CalcTree UI:
```
https://app.calctree.com/edit/{workspaceId}/{pageId}
```

### 2. Use Network Trace

Open browser DevTools → Network tab when manually creating items to see exact API calls.

### 3. Check Response

Always check the API response for errors:
```python
response = execute_query(query, variables)
if "errors" in response:
    print("Errors:", response["errors"])
else:
    print("Success:", response["data"])
```

### 4. Verify IDs

Print IDs to ensure they're nanoid format:
```python
page_id = generate()
print(f"Page ID: {page_id} (length: {len(page_id)})")  # Should be 21
```

### 5. Test Incrementally

Build up complexity:
1. First: Create page + addPageNode
2. Then: Add simple mathjs statement
3. Then: Add cross-referencing statements
4. Finally: Add python/multiline statements

---

## Still Having Issues?

1. Check [EXAMPLES.md](EXAMPLES.md) for verified working code
2. Review [API_REFERENCE.md](API_REFERENCE.md) for parameter requirements
3. See [CALCULATION_GUIDE.md](CALCULATION_GUIDE.md) for syntax rules
4. For Python: See [PYTHON_GUIDE.md](PYTHON_GUIDE.md) for library list

## Quick Checklist

Before submitting an issue, verify:

- [ ] Called `addPageNode` after `createPageSync`
- [ ] Included `data.pageId` in calculation
- [ ] Using nanoid format for all IDs
- [ ] MathJS formulas include variable assignment (`var = value`)
- [ ] RevisionId is `"ffffffff"` (not `null`)
- [ ] Timestamp is in milliseconds
- [ ] Python statements include `userId` in data
- [ ] Only using pre-installed Python libraries
- [ ] Checked page URL in browser to verify
