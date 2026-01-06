#!/usr/bin/env python3
"""
Add page headers back to part_04.md based on content matching with raw PDF
"""

# Page headers from raw PDF
page_headers = [
    ("แนวคําวินิจฉัยของศาลปกครอง ๒๑", "## แนวคำวินิจฉัยของศาลปกครอง ๒๑"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๒๓", "## แนวคำวินิจฉัยของศาลปกครอง ๒๓"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๒๕", "## แนวคำวินิจฉัยของศาลปกครอง ๒๕"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๒๗", "## แนวคำวินิจฉัยของศาลปกครอง ๒๗"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๒๙", "## แนวคำวินิจฉัยของศาลปกครอง ๒๙"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๓๑", "## แนวคำวินิจฉัยของศาลปกครอง ๓๑"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๓๓", "## แนวคำวินิจฉัยของศาลปกครอง ๓๓"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๓๕", "## แนวคำวินิจฉัยของศาลปกครอง ๓๕"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๓๗", "## แนวคำวินิจฉัยของศาลปกครอง ๓๗"),
    ("แนวคําวินิจฉัยของศาลปกครอง ๓๙", "## แนวคำวินิจฉัยของศาลปกครอง ๓๙"),
]

# Corresponding text snippets from raw PDF that appear after each page header
next_line_markers = [
    "มี คํ า วิ นิ จ ฉั ย ยกอุ ท ธรณ",  # After page 21
    "วรรคสอง ของระเบี ย บสํ านั ก นายกรั ฐ มนตรี",  # After page 23
    "ขอใหศาลมีคําพิพากษาหรือคําสั่งเพิกถอนหนังสือดังกลาว นั้น",  # After page 25
    "หรื อ มี ผ ลกระทบต อ สถานภาพของสิ ท ธิ ห รื อ หน า ที่ ข องบุ ค คล",  # After page 27
    "ที่อยูในอํานาจพิจารณาพิพากษาของศาลภาษีอากรตามมาตรา ๗ (๒) แหง",  # After page 29 - WRONG, checking raw
    "กับหลักเขตอุทยานแหงชาติภูพานในพื้นที่จริงดานทิศเหนือ",  # After page 31
    "พิจารณาทางปกครองเพื่อโตแยงคัดคานการรังวัดเพื่อออกหนังสือสําคัญ",  # After page 33
    "ตามพระราชบัญญัติตํารวจแหงชาติ พ.ศ. ๒๕๔๗",  # After page 35
    "๗) กรณีอื่น ๆ",  # After page 37
    "กรณีพิพาทเกี่ยวกับสัญญาทางปกครอง",  # After page 39
]

md_path = '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_04.md'

with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in MD: {len(lines)}")
print(f"Will add {len(page_headers)} page headers")

# Find each marker and insert page header before it
for idx, (raw_header, md_header) in enumerate(page_headers):
    marker = next_line_markers[idx] if idx < len(next_line_markers) else None
    if not marker:
        continue
    
    # Find the line containing the marker
    found = False
    for line_num, line in enumerate(lines):
        if marker in line or marker.replace(" ", "") in line.replace(" ", ""):
            # Insert page header before this line
            print(f"Found marker for page header '{md_header}' at line {line_num + 1}")
            lines.insert(line_num, f"\n{md_header}\n\n")
            found = True
            break
    
    if not found:
        print(f"Warning: Could not find marker for '{md_header}'")

# Write back
with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Updated {md_path}")
