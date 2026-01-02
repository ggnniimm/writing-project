#!/usr/bin/env python3
"""
Verify each Gemini-generated part against its source PDF part for Volume 12 (Academic_120324_111151)
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
            try:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text
            except Exception as e:
                print(f"Warning: Error extracting text from page in {os.path.basename(pdf_path)}: {e}")
    
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
        'top_discrepancies': sorted(discrepancies, key=lambda x: abs(x[3]), reverse=True)[:5]
    }

def main():
    parts_dir = "etc/Academic_120324_111151_parts"
    
    # Find all MD and PDF parts
    md_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_120324_111151_part_*.md")))
    pdf_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_120324_111151_part_*.pdf")))
    
    print("="*80)
    print("VOLUME 12 PART-BY-PART VERIFICATION")
    print("="*80)
    print(f"Found {len(md_files)} MD parts and {len(pdf_files)} PDF parts\n")
    
    results = []
    issues = []
    
    # Verify we have matching pairs
    md_basenames = set(os.path.basename(f).replace('.md', '') for f in md_files)
    pdf_basenames = set(os.path.basename(f).replace('.pdf', '') for f in pdf_files)
    
    common = sorted(list(md_basenames.intersection(pdf_basenames)))
    missing_md = pdf_basenames - md_basenames
    missing_pdf = md_basenames - pdf_basenames
    
    if missing_md:
        print(f"❌ Missing MD files for: {', '.join(missing_md)}")
    if missing_pdf:
        print(f"❌ Missing PDF files for: {', '.join(missing_pdf)}")
        
    for name in common:
        md_file = os.path.join(parts_dir, f"{name}.md")
        pdf_file = os.path.join(parts_dir, f"{name}.pdf")
        
        print(f"📄 Checking {name}...", end=" ")
        sys.stdout.flush()
        
        result = verify_part(md_file, pdf_file)
        results.append(result)
        
        status = []
        if result['is_empty']: status.append("EMPTY")
        if result['broken_thai'] > 0: status.append(f"BROKEN THAI({result['broken_thai']})")
        if abs(result['md_numeral_count'] - result['pdf_numeral_count']) > 20: status.append(f"NUM DIFF({result['md_numeral_count']}/{result['pdf_numeral_count']})")
        
        if status:
            print(f"⚠️  Issues: {', '.join(status)}")
            issues.append(result)
        else:
            print(f"✅ OK (Nums: {result['md_numeral_count']}/{result['pdf_numeral_count']})")
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    total_parts = len(results)
    clean_parts = total_parts - len(issues)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total parts verified: {total_parts}")
    print(f"   ✅ Clean parts: {clean_parts}")
    print(f"   ⚠️  Parts with potential issues: {len(issues)}")
    
    if issues:
        print(f"\n⚠️  Parts with Significant Issues:")
        print(f"\n{'Part':<40} {'Numerals (MD/PDF)':<20} {'Broken Thai':<15} {'Status'}")
        print("-"*90)
        
        for issue in issues:
            part_name = os.path.basename(issue['md_path']).replace('.md', '')
            num_str = f"{issue['md_numeral_count']}/{issue['pdf_numeral_count']}"
            
            status = "⚠️ CHECK"
            if issue['is_empty']: status = "❌ EMPTY"
            
            print(f"{part_name:<40} {num_str:<20} {issue['broken_thai']:<15} {status}")
            
    # Save detailed report
    with open("vol12_verification_report.txt", "w", encoding="utf-8") as f:
        f.write("VOLUME 12 VERIFICATION REPORT\n")
        f.write("="*60 + "\n\n")
        for res in results:
            f.write(f"Part: {os.path.basename(res['md_path'])}\n")
            f.write(f"  Lines: {res['md_lines']}\n")
            f.write(f"  Numerals: MD={res['md_numeral_count']} PDF={res['pdf_numeral_count']}\n")
            f.write(f"  Broken Thai Chars: {res['broken_thai']}\n")
            if res['top_discrepancies']:
                f.write("  Top Numeral Discrepancies:\n")
                for num, md, pdf, diff in res['top_discrepancies']:
                    f.write(f"    {num}: MD={md} PDF={pdf} (Diff={diff})\n")
            f.write("-" * 40 + "\n")

    return True

if __name__ == "__main__":
    main()
