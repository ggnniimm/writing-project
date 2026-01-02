#!/usr/bin/env python3
"""
Comprehensive verification script for Gemini-generated MD against source PDF
"""

import os
import sys
import re
from collections import Counter
import pdfplumber

def extract_thai_numerals(text):
    """Extract Thai numerals from text."""
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def verify_combined_md(md_path, pdf_path):
    """Verify the combined MD file against source PDF."""
    
    print("="*60)
    print("COMPREHENSIVE VERIFICATION")
    print("="*60)
    
    # 1. Basic file stats
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        md_lines = md_content.splitlines()
    
    print(f"\n📄 Markdown File: {os.path.basename(md_path)}")
    print(f"   Lines: {len(md_lines):,}")
    print(f"   Size: {len(md_content):,} bytes ({len(md_content)/1024/1024:.2f} MB)")
    
    # 2. Extract Thai numerals from MD
    print(f"\n🔢 Extracting Thai numerals from MD...")
    md_numerals = extract_thai_numerals(md_content)
    md_numeral_counts = Counter(md_numerals)
    print(f"   Unique numerals: {len(md_numeral_counts)}")
    print(f"   Total numerals: {len(md_numerals)}")
    
    # 3. Extract text and numerals from PDF
    print(f"\n📖 Extracting text from PDF: {os.path.basename(pdf_path)}")
    pdf_text = ""
    page_count = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text + "\n"
    
    print(f"   Pages: {page_count}")
    print(f"   Extracted text: {len(pdf_text):,} characters")
    
    pdf_numerals = extract_thai_numerals(pdf_text)
    pdf_numeral_counts = Counter(pdf_numerals)
    print(f"   Unique numerals: {len(pdf_numeral_counts)}")
    print(f"   Total numerals: {len(pdf_numerals)}")
    
    # 4. Compare numeral counts
    print(f"\n🔍 Comparing Thai numerals...")
    all_numerals = set(md_numeral_counts.keys()) | set(pdf_numeral_counts.keys())
    
    
    discrepancies = []
    for num in all_numerals:
        md_count = md_numeral_counts.get(num, 0)
        pdf_count = pdf_numeral_counts.get(num, 0)
        if md_count != pdf_count:
            discrepancies.append((num, md_count, pdf_count, pdf_count - md_count))
    
    # Sort by absolute difference (biggest discrepancies first)
    discrepancies.sort(key=lambda x: abs(x[3]), reverse=True)
    
    if discrepancies:
        print(f"   ⚠️  Found {len(discrepancies)} numeral discrepancies:")
        print(f"\n   {'Numeral':<15} {'MD Count':<12} {'PDF Count':<12} {'Difference'}")
        print(f"   {'-'*55}")
        for num, md_c, pdf_c, diff in discrepancies[:20]:
            print(f"   {num:<15} {md_c:<12} {pdf_c:<12} {diff:+d}")
        if len(discrepancies) > 20:
            print(f"   ... and {len(discrepancies) - 20} more")
    else:
        print(f"   ✅ No numeral discrepancies found!")
    
    # 5. Check for common issues
    print(f"\n🔎 Checking for common issues...")
    
    # Check for footer artifacts
    footer_pattern = r'ระบบงานคดีปกครองอิเล็กทรอนิกส์'
    footer_count = len(re.findall(footer_pattern, md_content))
    print(f"   Footer instances: {footer_count}")
    
    # Check for page markers
    page_marker_count = len(re.findall(r'แนวคำวินิจฉัยของศาลปกครอง\s+[๐-๙]+', md_content))
    print(f"   Page number headers: {page_marker_count}")
    
    # Check for broken Thai characters (with spaces)
    broken_thai = len(re.findall(r'[\u0E00-\u0E7F]\s+[\u0E31-\u0E3A\u0E47-\u0E4E]', md_content))
    print(f"   Broken Thai characters: {broken_thai}")
    
    # 6. Summary
    print(f"\n{'='*60}")
    print(f"VERIFICATION SUMMARY")
    print(f"{'='*60}")
    print(f"✅ File extracted successfully: {page_count} pages → {len(md_lines):,} lines")
    print(f"{'✅' if not discrepancies else '⚠️'}  Numeral accuracy: {len(discrepancies)} discrepancies")
    print(f"✅ Thai text quality: {broken_thai} broken characters")
    print(f"ℹ️  Footer instances: {footer_count}")
    
    return len(discrepancies) == 0

if __name__ == "__main__":
    md_path = "etc/Academic_280125_142653_parts/Academic_280125_142653_combined.md"
    pdf_path = "raw_pdfs/Academic_280125_142653.pdf"
    
    success = verify_combined_md(md_path, pdf_path)
    sys.exit(0 if success else 1)
