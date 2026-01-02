#!/usr/bin/env python3
"""
Verify each Gemini-generated part against its source PDF part
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
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    md_numerals = extract_thai_numerals(md_content)
    md_counts = Counter(md_numerals)
    
    # Read PDF
    with pdfplumber.open(pdf_path) as pdf:
        pdf_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text
    
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
    
    # Check for issues
    broken_thai = len(re.findall(r'[\u0E00-\u0E7F]\s+[\u0E31-\u0E3A\u0E47-\u0E4E]', md_content))
    
    return {
        'md_path': md_path,
        'pdf_path': pdf_path,
        'md_lines': len(md_content.splitlines()),
        'md_numeral_count': len(md_numerals),
        'pdf_numeral_count': len(pdf_numerals),
        'discrepancies': len(discrepancies),
        'broken_thai': broken_thai,
        'top_discrepancies': sorted(discrepancies, key=lambda x: abs(x[3]), reverse=True)[:5]
    }

def main():
    parts_dir = "etc/Academic_280125_142653_parts"
    
    # Find all MD and PDF parts
    md_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_280125_142653_part_*.md")))
    pdf_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_280125_142653_part_*.pdf")))
    
    print("="*80)
    print("PART-BY-PART VERIFICATION")
    print("="*80)
    print(f"Found {len(md_files)} MD parts and {len(pdf_files)} PDF parts\n")
    
    results = []
    issues = []
    
    for md_file, pdf_file in zip(md_files, pdf_files):
        part_name = os.path.basename(md_file).replace('.md', '')
        print(f"📄 Checking {part_name}...", end=" ")
        
        result = verify_part(md_file, pdf_file)
        results.append(result)
        
        if result['discrepancies'] > 0 or result['broken_thai'] > 0:
            print(f"⚠️  Issues found")
            issues.append(result)
        else:
            print(f"✅ OK")
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    total_parts = len(results)
    clean_parts = total_parts - len(issues)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total parts: {total_parts}")
    print(f"   ✅ Clean parts: {clean_parts}")
    print(f"   ⚠️  Parts with issues: {len(issues)}")
    
    if issues:
        print(f"\n⚠️  Parts with Issues:")
        print(f"\n{'Part':<40} {'Numerals':<15} {'Broken Thai':<15} {'Discrepancies'}")
        print("-"*80)
        
        for issue in issues:
            part_name = os.path.basename(issue['md_path']).replace('.md', '')
            numeral_diff = issue['pdf_numeral_count'] - issue['md_numeral_count']
            print(f"{part_name:<40} {numeral_diff:>+5} ({issue['md_numeral_count']}/{issue['pdf_numeral_count']})  {issue['broken_thai']:<15} {issue['discrepancies']}")
        
        print(f"\n📋 Top Discrepancies by Part:")
        for issue in issues[:5]:  # Show top 5 problematic parts
            if issue['discrepancies'] > 0:
                part_name = os.path.basename(issue['md_path']).replace('.md', '')
                print(f"\n   {part_name}:")
                for num, md_c, pdf_c, diff in issue['top_discrepancies']:
                    print(f"      {num}: MD={md_c}, PDF={pdf_c} (diff: {diff:+d})")
    
    print(f"\n{'='*80}")
    print(f"Verification {'PASSED ✅' if not issues else 'FAILED ⚠️'}")
    print(f"{'='*80}")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
