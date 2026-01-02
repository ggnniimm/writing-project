#!/usr/bin/env python3
"""
Fix common OCR errors in Thai text - missing mai taikhu (์) and other characters
"""

import re
import sys

def fix_thai_ocr_errors(text):
    """Fix common Thai OCR errors."""
    
    # Dictionary of common misspellings
    fixes = {
        # Missing ์ (mai taikhu)
        r'ผลิตภัณฑ(?!์)': 'ผลิตภัณฑ์',
        r'โทรศัพท(?!์)': 'โทรศัพท์',
        r'โทรทัศน(?!์)': 'โทรทัศน์',
        r'สัญญาณ(?! )โ': 'สัญญาณโ',  # Remove space before โ
        
        # Fix specific patterns
        r'ผลิตภัณฑ Pre': 'ผลิตภัณฑ์ Pre',
        r'ผลิตภัณฑ \(': 'ผลิตภัณฑ์ (',
    }
    
    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text)
    
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fix_thai_ocr.py <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = fix_thai_ocr_errors(content)
    
    # Count changes
    changes = sum(1 for old, new in zip(content, fixed_content) if old != new)
    if len(fixed_content) != len(content):
        changes += abs(len(fixed_content) - len(content))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"Processing {filepath}...")
    print(f"Fixed {changes} characters.")

if __name__ == "__main__":
    main()
