import re

filepath = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_57.md"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

patterns = [
    r"สายด่วนศาลปกครอง ๑๓๕๕",
    r"ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน",
    r"^TRUST$",
    r"^แนวคำวินิจฉัยของศาลปกครอง \d+",
    r"^ดัชนีคำสั่งศาลปกครองสูงสุด พ.ศ. \d+",
    r"^\|\s*คำสั่งศาลปกครองสูงสุดที่\s*\|\s*พ.ศ. \d+\s*\|\s*หน้า\s*\|",
    r"^\|\s*:[-]+\s*\|\s*:[-]+\s*\|\s*:[-]+\s*\|"
]

cleaned_lines = []
for line in lines:
    strip_line = line.strip()
    match = False
    for p in patterns:
        if re.search(p, strip_line):
           match = True
           break
    if not match:
        cleaned_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(cleaned_lines)

print(f"Cleaned {len(lines) - len(cleaned_lines)} lines.")
