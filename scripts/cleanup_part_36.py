
import re
import os

def thai_to_arabic(text):
    thai = "๐๑๒๓๔๕๖๗๘๙"
    arabic = "0123456789"
    trans = str.maketrans(thai, arabic)
    return text.translate(trans)

path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07/part_36.md"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    sline = line.strip()
    
    # 1. Remove TRUST noise lines entirely
    if "TRUST" in sline and "ศาลปกครอง" in sline:
        continue
        
    # 2. Fix Header (Header + PageNum -> PageNum + Header)
    # Example: "แนวคำวินิจฉัยของศาลปกครอง ๖๗๗"
    if "แนวคำวินิจฉัยของศาลปกครอง" in sline:
        # Check if number is at the END
        if re.search(r"[๐-๙\d]+$", sline):
             match = re.search(r"^(.*)\s+([๐-๙\d]+)$", sline)
             if match:
                 text_part = match.group(1).strip()
                 num_part = match.group(2).strip()
                 # Only swap if text comes first
                 if text_part.startswith("แนวคำวินิจฉัย"):
                     new_lines.append(f"{num_part} {text_part}\n")
                     continue

    # 3. Detect Loose Footnote Numbers (Thai numerals 1-3 digits, optionally range)
    # Range example: ๑๙-๒๐
    foot_match = re.match(r"^([๐-๙]{1,3}(-[๐-๙]{1,3})?)$", sline)
    if foot_match:
        # Found standalone footnote number
        # Peek next line to see if it's the definition body
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            # If next line is not empty and not another number/header
            if next_line and not re.match(r"^[๐-๙]+$", next_line):
                # Merge
                num_raw = foot_match.group(1)
                num_arabic = thai_to_arabic(num_raw)
                merged_line = f"<sup>{num_arabic}</sup> {next_line}\n"
                new_lines.append(merged_line)
                skip_next = True
                continue

    new_lines.append(line)

# Write back
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Cleanup complete for {path}")
