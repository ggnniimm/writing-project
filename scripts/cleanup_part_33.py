
import re

def to_thai_digits(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    trans = str.maketrans(arabic_digits, thai_digits)
    return text.translate(trans)

file_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07/part_33.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern 1: Arabic Page Number at Start of Line followed by "แนวคำวินิจฉัย..."
# Example: "618 แนวคำวินิจฉัย..."
content = re.sub(r"^(\d+)\s+(แนวคำวินิจฉัยของศาลปกครอง)", lambda m: f"{to_thai_digits(m.group(1))} {m.group(2)}", content, flags=re.MULTILINE)

# Pattern 2: "แนวคำวินิจฉัย..." followed by Arabic Page Number
# Example: "แนวคำวินิจฉัย... 619"
content = re.sub(r"(แนวคำวินิจฉัยของศาลปกครอง)\s+(\d+)$", lambda m: f"{to_thai_digits(m.group(2))} {m.group(1)}", content, flags=re.MULTILINE)

# Pattern 3: Standalone numbers that might be loose page numbers, but be careful not to hit content.
# The previous verify_md_content identified specific lines.
# "Line 29: Arabic numeral '618' found..." -> already handled by Pattern 1?
# Let's handle TRUST lines too.
content = re.sub(r"ศาลปกครองแห่งความเชื่อมั่น TRUST", "TRUST ศาลปกครองแห่งความเชื่อมั่น", content)
content = re.sub(r"TRUST ศาลปกครองแห่งความเชื่อมั่น TRUST", "TRUST ศาลปกครองแห่งความเชื่อมั่น", content)

# Normalize Thai/Arabic in header context explicitly if missed
def fix_header_line(match):
    # match group 1 is page number (arabic)
    return f"{to_thai_digits(match.group(1))} แนวคำวินิจฉัยของศาลปกครอง"

# Fix "620 แนว..."
content = re.sub(r"^(\d{3})\s+แนวคำวินิจฉัยของศาลปกครอง", lambda m: f"{to_thai_digits(m.group(1))} แนวคำวินิจฉัยของศาลปกครอง", content, flags=re.MULTILINE)

# Also fix the "TRUST" position to be before the page number line if needed, or ensure blank line.
# For now, just fixing numerals is the priority.

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Cleanup complete.")
