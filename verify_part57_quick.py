import os
import sys
import re
from collections import Counter
import pdfplumber

def extract_thai_numerals(text):
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def verify_part_57():
    md_path = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_57.md"
    pdf_path = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_57.pdf"

    if not os.path.exists(md_path): print(f"MD Not Found: {md_path}"); return
    if not os.path.exists(pdf_path): print(f"PDF Not Found: {pdf_path}"); return

    with open(md_path, 'r', encoding='utf-8') as f: md_content = f.read()
    
    pdf_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: pdf_text += t

    md_nums = extract_thai_numerals(md_content)
    pdf_nums = extract_thai_numerals(pdf_text)

    print(f"MD Numerals: {len(md_nums)}")
    print(f"PDF Numerals: {len(pdf_nums)}")
    print(f"Diff: {len(pdf_nums) - len(md_nums)}")

    md_counts = Counter(md_nums)
    pdf_counts = Counter(pdf_nums)
    
    all_nums = set(md_counts.keys()) | set(pdf_counts.keys())
    discrepancies = []
    for n in all_nums:
        if md_counts[n] != pdf_counts[n]:
            discrepancies.append((n, md_counts[n], pdf_counts[n], pdf_counts[n] - md_counts[n]))
    
    discrepancies.sort(key=lambda x: abs(x[3]), reverse=True)
    for d in discrepancies[:10]:
        print(f"{d[0]}: MD={d[1]} PDF={d[2]} Diff={d[3]}")

if __name__ == "__main__":
    verify_part_57()
