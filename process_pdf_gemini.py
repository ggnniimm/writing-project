#!/usr/bin/env python3
"""
Master script to process PDF through complete Gemini extraction workflow:
1. Split PDF into max 20-page parts
2. Extract each part using Gemini 2.5 Flash
3. Verify Thai numerals in each part
4. Combine all parts into single MD file

Usage: python3 process_pdf_gemini.py <input_pdf>
"""

import os
import sys
import subprocess
import glob
import re

def run_command(cmd, description):
    """Run a shell command and return success status."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def extract_numerals(text):
    """Extract Thai numerals from text."""
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def verify_part(md_file, pdf_file):
    """Verify Thai numerals between MD and PDF files."""
    print(f"\n🔍 Verifying: {os.path.basename(md_file)}")
    
    # Extract from MD
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    md_numerals = extract_numerals(md_content)
    
    # Extract from PDF using pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_file) as pdf:
            pdf_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text
        pdf_numerals = extract_numerals(pdf_text)
    except Exception as e:
        print(f"  ⚠️  Could not verify with pdfplumber: {e}")
        return True  # Don't fail, just warn
    
    # Compare counts
    from collections import Counter
    md_counts = Counter(md_numerals)
    pdf_counts = Counter(pdf_numerals)
    
    discrepancies = []
    all_nums = set(md_counts.keys()) | set(pdf_counts.keys())
    
    for num in all_nums:
        md_count = md_counts.get(num, 0)
        pdf_count = pdf_counts.get(num, 0)
        if md_count != pdf_count:
            discrepancies.append(f"  {num}: MD={md_count}, PDF={pdf_count}")
    
    if discrepancies:
        print(f"  ⚠️  Found {len(discrepancies)} numeral discrepancies:")
        for disc in discrepancies[:10]:  # Show first 10
            print(disc)
        if len(discrepancies) > 10:
            print(f"  ... and {len(discrepancies) - 10} more")
        return False
    else:
        print(f"  ✅ No numeral discrepancies found")
        return True

def process_pdf_gemini(input_pdf):
    """Main workflow to process PDF."""
    
    if not os.path.exists(input_pdf):
        print(f"❌ Error: File not found: {input_pdf}")
        return False
    
    # Get base paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_name = os.path.splitext(os.path.basename(input_pdf))[0]
    
    # Create work directory
    work_dir = os.path.join(base_dir, "etc", f"{pdf_name}_parts")
    os.makedirs(work_dir, exist_ok=True)
    
    print(f"\n🚀 Starting Gemini PDF Extraction Workflow")
    print(f"📁 Input: {input_pdf}")
    print(f"📂 Work Directory: {work_dir}")
    
    # Step 1: Split PDF
    if not run_command(
        f"python3 {os.path.join(base_dir, 'split_pdf.py')} \"{input_pdf}\" \"{work_dir}\"",
        "Step 1: Splitting PDF into parts"
    ):
        print("❌ PDF splitting failed")
        return False
    
    # Step 2: Extract each part with Gemini
    pdf_parts = sorted(glob.glob(os.path.join(work_dir, f"{pdf_name}_part_*.pdf")))
    
    if not pdf_parts:
        print("❌ No PDF parts found after splitting")
        return False
    
    print(f"\n📚 Found {len(pdf_parts)} parts to process")
    
    md_files = []
    for i, pdf_part in enumerate(pdf_parts, 1):
        part_name = os.path.basename(pdf_part)
        print(f"\n{'='*60}")
        print(f"📄 Processing Part {i}/{len(pdf_parts)}: {part_name}")
        print(f"{'='*60}")
        
        # Extract with Gemini
        expected_md = os.path.join(work_dir, f"{os.path.splitext(part_name)[0]}.md")
        
        if not run_command(
            f"python3 {os.path.join(base_dir, 'extract_pdf_simple.py')} \"{pdf_part}\" \"{expected_md}\"",
            f"Extracting with Gemini 2.5 Flash"
        ):
            print(f"⚠️  Warning: Extraction failed for {part_name}")
            continue
        
        # Verify the file was created
        if os.path.exists(expected_md):
            md_files.append(expected_md)
            print(f"  ✅ Created: {os.path.basename(expected_md)}")
            
            # Verify numerals
            verify_part(expected_md, pdf_part)
        else:
            print(f"  ⚠️  Expected MD file not found: {expected_md}")
    
    # Step 3: Combine all parts
    if not md_files:
        print("\n❌ No MD files to combine")
        return False
    
    print(f"\n{'='*60}")
    print(f"🔗 Step 3: Combining {len(md_files)} parts")
    print(f"{'='*60}")
    
    combined_file = os.path.join(work_dir, f"{pdf_name}_combined.md")
    
    with open(combined_file, 'w', encoding='utf-8') as outfile:
        for i, md_file in enumerate(sorted(md_files), 1):
            print(f"  📎 Adding part {i}/{len(md_files)}: {os.path.basename(md_file)}")
            with open(md_file, 'r', encoding='utf-8') as infile:
                outfile.write(infile.read())
                outfile.write('\n')  # Separator between parts
    
    # Count lines
    with open(combined_file, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    
    file_size_mb = os.path.getsize(combined_file) / (1024 * 1024)
    
    print(f"\n{'='*60}")
    print(f"✨ WORKFLOW COMPLETE!")
    print(f"{'='*60}")
    print(f"📄 Combined file: {combined_file}")
    print(f"📊 Lines: {line_count:,}")
    print(f"💾 Size: {file_size_mb:.2f} MB")
    print(f"📂 All files saved in: {work_dir}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process_pdf_gemini.py <input_pdf>")
        print("Example: python3 process_pdf_gemini.py raw_pdfs/Academic_280125_142653.pdf")
        sys.exit(1)
    
    success = process_pdf_gemini(sys.argv[1])
    sys.exit(0 if success else 1)
