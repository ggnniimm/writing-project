#!/usr/bin/env python3
"""
Verify each Gemini-generated part against its source PDF part for Volume 11 (Academic_291121_112321)
"""

import os
import sys
import re
import glob
from collections import Counter
import pdfplumber

def extract_thai_numerals(text):
    """Extract Thai numerals from text."""
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def verify_part(md_path, pdf_path):
    """Verify a single MD part against its PDF source."""
    
    # Read MD
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        return {'error': 'MD file not found'}
    
    md_numerals = extract_thai_numerals(md_content)
    md_counts = Counter(md_numerals)
    
    # Read PDF
    pdf_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_text += page_text
                except Exception as e:
                    print(f"Warning: Error extracting text from page in {os.path.basename(pdf_path)}: {e}")
    except Exception as e:
        return {'error': f'PDF error: {e}'}
    
    pdf_numerals = extract_thai_numerals(pdf_text)
    pdf_counts = Counter(pdf_numerals)
    
    # Compare
    all_nums = set(md_counts.keys()) | set(pdf_counts.keys())
    discrepancies = []
    
    for num in all_nums:
        md_c = md_counts.get(num, 0)
        pdf_c = pdf_counts.get(num, 0)
        if md_c != pdf_c:
            discrepancies.append((num, md_c, pdf_c, pdf_c - md_c))
            
    # Check for empty content
    is_empty = len(md_content.strip()) == 0
    
    # Check for broken Thai characters (with spaces)
    broken_thai = len(re.findall(r'[\u0E00-\u0E7F]\s+[\u0E31-\u0E3A\u0E47-\u0E4E]', md_content))
    
    return {
        'md_path': md_path,
        'pdf_path': pdf_path,
        'md_lines': len(md_content.splitlines()),
        'md_numeral_count': len(md_numerals),
        'pdf_numeral_count': len(pdf_numerals),
        'discrepancies': len(discrepancies),
        'broken_thai': broken_thai,
        'is_empty': is_empty,
        'top_discrepancies': sorted(discrepancies, key=lambda x: abs(x[3]), reverse=True)[:10]
    }

def main():
    parts_dir = "etc/Academic_291121_112321_parts"
    
    # Specific check for part 01 if requested, otherwise check all
    target_part = "01"
    
    md_file = os.path.join(parts_dir, f"Academic_291121_112321_part_{target_part}.md")
    pdf_file = os.path.join(parts_dir, f"Academic_291121_112321_part_{target_part}.pdf")
    
    print("="*80)
    print(f"VERIFICATION REPORT: Part {target_part}")
    print("="*80)
    
    if not os.path.exists(md_file):
        print(f"❌ MD File not found: {md_file}")
        return
    if not os.path.exists(pdf_file):
        print(f"❌ PDF File not found: {pdf_file}")
        return
        
    result = verify_part(md_file, pdf_file)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return

    print(f"📄 File: {os.path.basename(md_file)}")
    print(f"   Lines: {result['md_lines']}")
    print(f"   Numerals: MD={result['md_numeral_count']}   PDF={result['pdf_numeral_count']}")
    
    diff = result['md_numeral_count'] - result['pdf_numeral_count']
    if diff == 0:
        print(f"   ✅ Numeral Count Match")
    else:
        print(f"   ⚠️  Numeral Count Diff: {diff:+d}")
        
    print(f"   Broken Thai Characters: {result['broken_thai']}")
    if result['broken_thai'] == 0:
         print(f"   ✅ No broken Thai characters detected")
    else:
         print(f"   ❌ Found broken Thai characters!")

    if result['discrepancies'] > 0:
        print(f"\n🔍 Detailed Numeral Discrepancies ({result['discrepancies']} types found):")
        print(f"   {'Numeral':<20} {'MD':<5} {'PDF':<5} {'Diff':<5}")
        print(f"   {'-'*40}")
        for num, md, pdf, diff in result['top_discrepancies']:
            print(f"   {num:<20} {md:<5} {pdf:<5} {diff:<5}")
    else:
        print("\n✅ Accurate Numerals: No discrepancies found.")

if __name__ == "__main__":
    main()
