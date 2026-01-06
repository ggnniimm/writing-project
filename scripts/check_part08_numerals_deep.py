from pypdf import PdfReader
import re

# 1. Read MD file lines
md_path = "etc/split_vol07/part_08.md"
with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

target_indices = [123, 156, 193] # 0-indexed for lines 124, 157, 194

print("--- MD File Content Check ---")
for idx in target_indices:
    if 0 <= idx < len(lines):
        print(f"Line {idx+1}: {lines[idx].strip()}")
    else:
        print(f"Line {idx+1}: [Out of bounds]")

# 2. Check PDF Content
print("\n--- PDF Content Check ---")
pdf_path = "etc/split_vol07/part_08.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

def normalize(t):
    return re.sub(r'\s+', '', t)

norm_text = normalize(full_text)

# Snippets to find
# Line 124: โฉนดที่ดินเลขที่...
# Line 157: จำนวน...ชุด
# Line 194: พวกรวม...คน

search_pairs = [
    ("โฉนดที่ดินเลขที่", "ตำบลจระเข้หิน"),
    ("จำนวน", "ชุดกับบริษัทS"),
    ("พวกรวม", "คนร่วมกระทำความผิด"),
]

for start_marker, end_marker in search_pairs:
    print(f"\nSearching for context between '{start_marker}' and '{end_marker}'...")
    start_idx = norm_text.find(start_marker)
    if start_idx != -1:
        # Find potential end
        end_idx = norm_text.find(end_marker, start_idx)
        if end_idx != -1:
            snippet = norm_text[start_idx:end_idx+len(end_marker)]
            print(f"Found: {snippet}")
        else:
            print(f"Found start but not end. Context: {norm_text[start_idx:start_idx+50]}")
    else:
        print("Start marker not found.")
