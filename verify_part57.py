import pdfplumber
import re
import os

# Define paths
base_dir = "etc/Academic_291121_112321_parts"
md_path = os.path.join(base_dir, "Academic_291121_112321_part_57.md")
pdf_path = os.path.join(base_dir, "Academic_291121_112321_part_57.pdf")

def normalize_thai_numerals(text):
    """Normalize Thai numerals to Arabic for easier comparison, or keep as is."""
    # This function is just for cleaning text before extraction if needed
    return text

def extract_numerals(text):
    """Extract all Thai numeral sequences from text."""
    return re.findall(r'[๐-๙]+', text)

def get_context(text, numeral, occur_index, window=30):
    """Find the context of the Nth occurrence of a numeral."""
    count = -1
    start = 0
    while True:
        idx = text.find(numeral, start)
        if idx == -1:
            return None
        count += 1
        if count == occur_index:
            s = max(0, idx - window)
            e = min(len(text), idx + len(numeral) + window)
            return text[s:e].replace('\n', ' ')
        start = idx + 1

print(f"Verifying {md_path} against {pdf_path}...")

# 1. Read Markdown
try:
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
except FileNotFoundError:
    print(f"Error: MD file not found at {md_path}")
    exit(1)

md_numerals = extract_numerals(md_content)

# 2. Read PDF
pdf_text = ""
try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extract = page.extract_text()
            if extract:
                pdf_text += extract + "\n"
except Exception as e:
    print(f"Error reading PDF: {e}")
    exit(1)

pdf_numerals = extract_numerals(pdf_text)

# 3. Compare
print(f"MD Numerals: {len(md_numerals)}")
print(f"PDF Numerals: {len(pdf_numerals)}")
print(f"Diff: {len(md_numerals) - len(pdf_numerals)}")

# 4. Analyze Discrepancies
from collections import Counter
md_counts = Counter(md_numerals)
pdf_counts = Counter(pdf_numerals)

all_nums = set(md_counts.keys()) | set(pdf_counts.keys())
diffs = {}
for num in all_nums:
    diff = md_counts[num] - pdf_counts[num]
    if diff != 0:
        diffs[num] = diff

print("\nTop Discrepancies:")
sorted_diffs = sorted(diffs.items(), key=lambda x: abs(x[1]), reverse=True)
for num, d in sorted_diffs[:20]:
    print(f"   {num}: MD={md_counts[num]} PDF={pdf_counts[num]} Diff={d}")

# 5. Missing/Excess Context
print("\n--- Detailed Context for Top 3 Missing/Excess ---")
for num, d in sorted_diffs[:3]:
    if d < 0: # Missing in MD
        print(f"\nMissing '{num}' (PDF has {pdf_counts[num]}, MD has {md_counts[num]}):")
        # Find context in PDF for occurrences NOT in MD (simple approximation)
        # This is hard to do perfectly without alignment, but we can print first few PDF contexts
        start_idx = 0
        for i in range(min(3, pdf_counts[num])):
            idx = pdf_text.find(num, start_idx)
            if idx != -1:
                print(f"   PDF Occur #{i+1}: ...{pdf_text[idx-20:idx+20].replace(chr(10), ' ')}...")
                start_idx = idx + 1
    elif d > 0: # Excess in MD
        print(f"\nExcess '{num}' (MD has {md_counts[num]}, PDF has {pdf_counts[num]}):")
        start_idx = 0
        for i in range(min(3, md_counts[num])):
            idx = md_content.find(num, start_idx)
            if idx != -1:
                print(f"   MD Occur #{i+1}: ...{md_content[idx-20:idx+20].replace(chr(10), ' ')}...")
                start_idx = idx + 1
