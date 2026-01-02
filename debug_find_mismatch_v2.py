
import re
import difflib

md_path = 'etc/split_v14_2569_40/part_20.md'
pdf_text_path = 'part_20_extracted.txt'

def extract_numerals(text):
    return re.findall(r'[๐-๙\d]+', text)

with open(md_path, 'r', encoding='utf-8') as f:
    md_lines = f.readlines()

with open(pdf_text_path, 'r', encoding='utf-8') as f:
    pdf_lines = f.readlines()

# Normalize: remove empty lines and whitespace
md_lines_norm = [l.strip() for l in md_lines if l.strip()]
pdf_lines_norm = [l.strip() for l in pdf_lines if l.strip()]

# Use difflib to find matching blocks
matcher = difflib.SequenceMatcher(None, md_lines_norm, pdf_lines_norm)

for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == 'replace':
        for i in range(i1, i2):
            md_line = md_lines_norm[i]
            # Try to find corresponding line in pdf block [j1:j2]
            # Simple heuristic: best match
            best_ratio = 0
            best_pdf_line = ""
            for j in range(j1, j2):
                pdf_line = pdf_lines_norm[j]
                ratio = difflib.SequenceMatcher(None, md_line, pdf_line).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_pdf_line = pdf_line
            
            if best_ratio > 0.8: # High confidence match
                md_nums = extract_numerals(md_line)
                pdf_nums = extract_numerals(best_pdf_line)
                if md_nums != pdf_nums:
                    print(f"MISMATCH:")
                    print(f"MD : {md_line}")
                    print(f"PDF: {best_pdf_line}")
                    print(f"     MD nums: {md_nums} vs PDF nums: {pdf_nums}")
                    print("-" * 20)
