#!/usr/bin/env python3
"""
Re-verify Part 18 and 57
"""
import os
import sys
import re
from collections import Counter
import pdfplumber

def extract_thai_numerals(text):
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def verify_part(part_num):
    parts_dir = "etc/Academic_291121_112321_parts"
    md_file = os.path.join(parts_dir, f"Academic_291121_112321_part_{part_num}.md")
    pdf_file = os.path.join(parts_dir, f"Academic_291121_112321_part_{part_num}.pdf")
    
    print(f"Checking Part {part_num}...")
    
    # MD
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_text = f.read()
    except:
        print("MD not found")
        return
        
    md_nums = extract_thai_numerals(md_text)
    
    # PDF
    pdf_text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text: pdf_text += text
    except:
        print("PDF error")
        return

    pdf_nums = extract_thai_numerals(pdf_text)
    
    print(f"  MD Numerals: {len(md_nums)}")
    print(f"  PDF Numerals: {len(pdf_nums)}")
    print(f"  Diff: {len(pdf_nums) - len(md_nums)}")
    print("-" * 30)

verify_part("18")
verify_part("57")
