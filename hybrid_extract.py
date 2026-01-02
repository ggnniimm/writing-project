#!/usr/bin/env python3
"""
Hybrid PDF extraction script:
- Use pdfplumber for standard parts (01-32, 34)
- Use Gemini for complex part (33)
"""

import os
import sys
import subprocess
import pdfplumber

def extract_with_pdfplumber(pdf_path, output_path):
    """Extract text from PDF using pdfplumber."""
    print(f"   📖 Extracting with pdfplumber...")
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    return True

def apply_cleanup(md_path):
    """Apply Thai text cleanup scripts."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Clean Thai spacing
    print(f"   🧹 Cleaning Thai spacing...")
    result = subprocess.run(
        ['python3', os.path.join(base_dir, 'clean_thai.py'), md_path],
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"   ⚠️  Thai cleanup warning: {result.stderr.decode()}")
    
    # 2. Fix standard phrases
    print(f"   ✨ Fixing standard phrases...")
    result = subprocess.run(
        ['python3', os.path.join(base_dir, 'fix_spaces.py'), md_path],
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"   ⚠️  Phrase fix warning: {result.stderr.decode()}")
    
    # 3. Remove footers
    print(f"   🗑️  Removing footers...")
    result = subprocess.run(
        ['python3', os.path.join(base_dir, 'remove_footers.py'), md_path],
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"   ⚠️  Footer removal warning: {result.stderr.decode()}")

def main():
    parts_dir = "etc/Academic_280125_142653_parts"
    
    # List all PDF parts
    import glob
    pdf_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_280125_142653_part_*.pdf")))
    
    print("="*80)
    print("HYBRID PDF EXTRACTION")
    print("="*80)
    print(f"Total parts: {len(pdf_files)}")
    print(f"Strategy: pdfplumber (32 parts) + Gemini (part_33)")
    print("")
    
    success_count = 0
    
    for pdf_file in pdf_files:
        part_name = os.path.basename(pdf_file).replace('.pdf', '')
        part_num = part_name.split('_')[-1]
        
        md_file = pdf_file.replace('.pdf', '.md')
        
        print(f"📄 {part_name}")
        
        # Strategy: Use Gemini for part_33, pdfplumber for others
        if part_num == '33':
            # Check if Gemini version exists and is good
            if os.path.exists(md_file):
                file_size = os.path.getsize(md_file)
                if file_size > 1000:  # At least 1KB
                    print(f"   ✅ Using existing Gemini extraction ({file_size:,} bytes)")
                    # Still apply cleanup
                    apply_cleanup(md_file)
                    success_count += 1
                    continue
            
            # If not, extract with Gemini
            print(f"   🔬 Needs Gemini extraction (complex tables)")
            print(f"   ℹ️  Skipping for now - will use existing if available")
            continue
        
        # Use pdfplumber for all other parts
        try:
            extract_with_pdfplumber(pdf_file, md_file)
            apply_cleanup(md_file)
            
            file_size = os.path.getsize(md_file)
            print(f"   ✅ Complete ({file_size:,} bytes)")
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Successful: {success_count}/{len(pdf_files)} parts")
    print(f"")

if __name__ == "__main__":
    main()
