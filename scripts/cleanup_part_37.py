
import re

file_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07/part_37.md"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

cleaned_lines = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    line = line.strip()
    
    # 1. Remove "TRUST" lines
    if "TRUST" in line or "ศาลปกครองแห่งความเชื่อมั่น" in line:
        continue
    
    # 2. Fix Header/Page Number
    # Pattern: "แนวคำวินิจฉัยของศาลปกครอง ๖๙๗" -> "๖๙๗ แนวคำวินิจฉัยของศาลปกครอง"
    # Or keep "๖๙๗ แนวคำวินิจฉัยของศาลปกครอง" (Standard seems to be Page then Header?)
    # Validating against part_36: It was "๖๘๑ แนวคำวินิจฉัยของศาลปกครอง"
    # So we want "NUM Header".
    
    # CASE A: Header NUM (e.g. แนวคำวินิจฉัยของศาลปกครอง ๖๙๗)
    match_a = re.match(r"^(แนวคำวินิจฉัยของศาลปกครอง)\s+([๐-๙]+)$", line)
    if match_a:
        line = f"{match_a.group(2)} {match_a.group(1)}"
    
    # CASE B: NUM Header (e.g. ๖๙๘ แนวคำวินิจฉัยของศาลปกครอง) - Already correct
    
    # 3. Remove "---" lines (page breaks from extraction)
    if line == "---":
        continue
        
    cleaned_lines.append(line)

# Join and fix whitespace
content = "\n".join(cleaned_lines)
content = re.sub(r'\n{3,}', '\n\n', content)

# 4. Handle broken footnote definitions
# Find lines that are just Thai/Arabic numerals, possibly with range e.g. "๑", "๖-๗"
# And next line is text.
# We want to merge them: "๑\nText" -> "<sup>๑</sup> Text"

def merge_footnotes(text):
    lines = text.split('\n')
    output = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Regex for strictly digits or digit-digit
        # Thai digits: ๐-๙
        # Arabic: 0-9
        if re.match(r"^([๐-๙]+|[0-9]+)(?:-([๐-๙]+|[0-9]+))?$", line):
            # Check if next line exists
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if next_line:
                    # Convert Arabic to Thai if needed
                    # Actually, let's keep it simple first. The user wants Thai.
                    # We'll use a conversion helper later if needed, but if the source is already Thai "๑", it's fine.
                    # If it's "1", we might want to convert.
                    def to_thai(m):
                        tr = str.maketrans("0123456789", "๐๑๒๓๔๕๖๗๘๙")
                        return m.translate(tr)
                    
                    ft_num = to_thai(line)
                    merged = f"^{ft_num}^ {next_line}" # Temporary format, we'll replace to <sup> later or keep ^
                    # actually user requested <sup>๑</sup> format in part 36.
                    merged = f"<sup>{ft_num}</sup> {next_line}"
                    output.append(merged)
                    i += 2 # Skip next line
                    continue
        output.append(line)
        i += 1
    return "\n".join(output)

content = merge_footnotes(content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Cleanup complete.")
