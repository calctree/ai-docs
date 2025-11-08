#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate CalcTree documentation structure"""

import os
import json
import sys
from pathlib import Path

# Ensure UTF-8 encoding for output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

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
    assert len(config['rules']) >= 10
    print(f"✓ context7.json valid with {len(config['rules'])} rules")

def test_cross_references():
    """Test internal links in README"""
    with open('README.md', encoding='utf-8') as f:
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
