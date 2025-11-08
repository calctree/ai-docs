# Testing the CalcTree API Documentation

How to verify that the documentation and Context7 integration are working correctly.

## 1. Test Documentation Locally

### Prerequisites

Install dependencies:
```bash
pip install requests nanoid
```

### Test the Reference Script

1. Edit [calctree_reference.py](calctree_reference.py) and set:
   ```python
   WORKSPACE_ID = "your-workspace-id"
   API_KEY = "your-api-key"
   ```

2. Run it:
   ```bash
   python calctree_reference.py
   ```

The script will:
1. Fetch your userId automatically using the currentUser query
2. Create a complete test page with all calculation types
3. Display the page URL

**Expected output:**
```
CalcTree API Reference Implementation
======================================================================
Workspace: 98ea9cce-909a-44e9-9359-be53c3d67d04
Endpoint: https://graph.calctree.com/graphql
======================================================================

[0/4] Fetching user ID...
[OK] User ID: 4d83c852-69a7-4744-8b7c-92d0335386c3

Creating page: abc123xyz...

[1/4] Creating page...
[OK] Page created: Complete Engineering Calculation

[2/4] Adding page to tree...
[OK] Page added to tree

[3/4] Creating calculation with multiple statements...
[OK] Calculation created with 5 statements

[4/4] Adding Python analysis statement...
[OK] Python analysis added

======================================================================
SUCCESS!
======================================================================

Page URL: https://app.calctree.com/edit/{workspace-id}/{page-id}

The page contains:
  • beam_length = 10 m
  • load = 5 kN
  • Section Properties (width, height, area)
  • moment = load * beam_length (cross-reference)
  • stress = moment / section_modulus (cross-reference)
  • Python analysis with safety factor check

Open the URL above in your browser to see the calculation!
```

**Verification:**
1. Open the page URL in your browser
2. Verify the page appears in the page tree (left sidebar)
3. Verify all statements appear in the calculation (right sidebar)
4. Check that cross-references work (moment uses load and beam_length)

---

## 2. Test Context7 Integration

### Option A: Using Context7 MCP Server

If you have Context7 installed as an MCP server:

1. Ask your AI assistant: "Show me how to create a CalcTree page with calculations"
2. The AI should reference the documentation and provide correct code
3. Verify it mentions the two critical requirements:
   - Call `addPageNode` after `createPageSync`
   - Include `data.pageId` in calculations

### Option B: Manual Testing via Context7.com

1. Go to https://context7.com
2. Search for "CalcTree API Documentation" (if published)
3. Verify the documentation appears and is indexed

### Option C: Simulate Context7 Indexing

Check what files would be indexed:

```bash
cd ai-docs

# List all files that WOULD be indexed
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.json" \) \
  | grep -v "tests/" \
  | grep -v "archive/" \
  | grep -v ".claude/" \
  | grep -v "test_"
```

**Expected output:**
```
./README.md
./API_REFERENCE.md
./CALCULATION_GUIDE.md
./PYTHON_GUIDE.md
./EXAMPLES.md
./TROUBLESHOOTING.md
./context7.json
./calctree_reference.py
```

**Verify excludes are working:**

```bash
# These should return nothing (excluded):
find . -path "./tests/*" -name "*.py" | head -5
find . -path "./archive/*" | head -5
```

---

## 3. Test Documentation Quality

### Check All Cross-References

Verify all internal links work:

```bash
cd ai-docs

# Extract all markdown links
grep -r "\[.*\](.*\.md)" *.md | grep -v "http"
```

**Verify each link exists:**
- README.md → API_REFERENCE.md ✓
- README.md → CALCULATION_GUIDE.md ✓
- README.md → PYTHON_GUIDE.md ✓
- README.md → EXAMPLES.md ✓
- README.md → TROUBLESHOOTING.md ✓
- (and reverse links)

### Validate JSON Schema

```bash
# Validate context7.json
python -m json.tool context7.json > /dev/null && echo "✓ Valid JSON" || echo "✗ Invalid JSON"
```

---

## 4. Test Documentation Completeness

### Verify Critical Topics Covered

Check each file has required content:

**README.md:**
```bash
grep -q "Quick Start" README.md && echo "✓ Quick Start"
grep -q "#1.*addPageNode" README.md && echo "✓ Common Mistake #1"
grep -q "#2.*pageId" README.md && echo "✓ Common Mistake #2"
```

**API_REFERENCE.md:**
```bash
grep -q "createPageSync" API_REFERENCE.md && echo "✓ createPageSync"
grep -q "addPageNode" API_REFERENCE.md && echo "✓ addPageNode"
grep -q "createOrUpdateCalculation" API_REFERENCE.md && echo "✓ createOrUpdateCalculation"
grep -q "nanoid" API_REFERENCE.md && echo "✓ nanoid format"
```

**CALCULATION_GUIDE.md:**
```bash
grep -q "variable_name = value" CALCULATION_GUIDE.md && echo "✓ MathJS syntax"
grep -q "multiline_mathjs" CALCULATION_GUIDE.md && echo "✓ Multiline engine"
grep -q "scope" CALCULATION_GUIDE.md && echo "✓ Variable scoping"
```

**PYTHON_GUIDE.md:**
```bash
grep -q "numpy" PYTHON_GUIDE.md && echo "✓ NumPy"
grep -q "anaStruct" PYTHON_GUIDE.md && echo "✓ Engineering libraries"
grep -q "26+" PYTHON_GUIDE.md && echo "✓ Library count"
grep -q "userId" PYTHON_GUIDE.md && echo "✓ userId requirement"
```

**EXAMPLES.md:**
```bash
# Count examples
grep -c "^## Example" EXAMPLES.md
# Should be 6 or more
```

**TROUBLESHOOTING.md:**
```bash
grep -q "### #1:" TROUBLESHOOTING.md && echo "✓ Top mistake #1"
grep -q "### #2:" TROUBLESHOOTING.md && echo "✓ Top mistake #2"
grep -q "Not Authorised" TROUBLESHOOTING.md && echo "✓ Python auth error"
```

---

## 5. Test with AI Assistant

### Test Case 1: Simple Page Creation

Ask your AI: "Using the CalcTree API, create a simple page with one calculation"

**Expected behavior:**
- AI mentions calling `addPageNode`
- AI includes `data.pageId`
- AI uses correct formula syntax: `variable = value units`
- AI uses nanoid for IDs

### Test Case 2: Multi-Statement Calculation

Ask: "Create a CalcTree page with multiple calculations that reference each other"

**Expected behavior:**
- AI uses `createOrUpdateCalculation` with `withStatements` array
- AI demonstrates variable cross-referencing
- AI explains scope (all statements share same calculationId)

### Test Case 3: Python Statement

Ask: "Add a Python statement to a CalcTree calculation"

**Expected behavior:**
- AI mentions `userId` requirement
- AI only uses pre-installed libraries
- AI warns about query authorization errors

### Test Case 4: Troubleshooting

Ask: "My CalcTree page isn't appearing in the page tree, what's wrong?"

**Expected behavior:**
- AI immediately suggests checking `addPageNode` call
- AI identifies this as "#1 most common mistake"

---

## 6. Automated Testing Script

Create a simple validation script:

```python
#!/usr/bin/env python3
"""Validate CalcTree documentation structure"""

import os
import json
from pathlib import Path

def test_structure():
    """Test that all required files exist"""
    required_files = [
        'README.md',
        'API_REFERENCE.md',
        'CALCULATION_GUIDE.md',
        'PYTHON_GUIDE.md',
        'EXAMPLES.md',
        'TROUBLESHOOTING.md',
        'context7.json',
        'calctree_reference.py'
    ]

    for file in required_files:
        assert Path(file).exists(), f"Missing: {file}"
        print(f"✓ {file}")

def test_context7_json():
    """Test context7.json is valid"""
    with open('context7.json') as f:
        config = json.load(f)

    assert config['projectTitle'] == "CalcTree API Documentation"
    assert 'tests' in config['excludeFolders']
    assert 'archive' in config['excludeFolders']
    assert len(config['rules']) >= 18
    print(f"✓ context7.json valid with {len(config['rules'])} rules")

def test_cross_references():
    """Test internal links in README"""
    with open('README.md') as f:
        content = f.read()

    links = [
        'API_REFERENCE.md',
        'CALCULATION_GUIDE.md',
        'PYTHON_GUIDE.md',
        'EXAMPLES.md',
        'TROUBLESHOOTING.md'
    ]

    for link in links:
        assert link in content, f"README missing link to {link}"
        print(f"✓ README links to {link}")

if __name__ == '__main__':
    print("Testing CalcTree Documentation Structure")
    print("=" * 50)
    test_structure()
    test_context7_json()
    test_cross_references()
    print("=" * 50)
    print("✓ All tests passed!")
```

Run it:
```bash
python validate_docs.py
```

---

## 7. Final Checklist

Before publishing/committing:

- [ ] Run `calctree_reference.py` and verify page creates successfully
- [ ] Check all verified example URLs still work
- [ ] Validate `context7.json` is valid JSON
- [ ] Verify no test files in root directory
- [ ] Check all cross-references in documentation work
- [ ] Ensure archive and tests folders are excluded
- [ ] Test that AI assistant can access and use the docs
- [ ] Verify all 18 rules in context7.json are accurate
- [ ] Check that Python library list (26+) is complete
- [ ] Confirm common mistakes (#1 and #2) are prominent

---

## Expected Results

### What Should Work

✅ Creating pages with calculations via API
✅ Multi-statement calculations with cross-references
✅ MathJS with units and unit conversions
✅ Multiline MathJS blocks
✅ Python statements (with userId)
✅ All verified example page URLs

### What Should Be Documented

✅ Two-step page creation requirement
✅ data.pageId requirement
✅ Correct MathJS syntax (variable = value)
✅ Variable scoping rules
✅ nanoid ID format
✅ Pre-installed Python libraries (26+)
✅ Common errors and solutions

### What Context7 Should Index

✅ All markdown documentation files
✅ calctree_reference.py
✅ context7.json with 18 rules
❌ Test scripts (excluded)
❌ Archive files (excluded)
❌ .claude folder (excluded)

---

## Troubleshooting Tests

If tests fail, check:

1. **calctree_reference.py fails:**
   - Verify API key is valid
   - Check workspace ID is correct
   - Ensure nanoid package is installed: `pip install nanoid requests`

2. **Example URLs don't work:**
   - Pages may have been deleted
   - Run calctree_reference.py to create new example

3. **Context7 not indexing:**
   - Verify context7.json is valid JSON
   - Check excludeFolders includes tests, archive
   - Ensure files are markdown or Python (supported formats)

4. **AI not using documentation:**
   - Verify AI has access to Context7
   - Check that repo is published/accessible
   - Try asking specifically: "According to the CalcTree documentation..."
