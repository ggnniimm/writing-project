
import re

file_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07/part_36.md"

def arabic_to_thai(text_num):
    arabic = "0123456789"
    thai = "๐๑๒๓๔๕๖๗๘๙"
    trans = str.maketrans(arabic, thai)
    return text_num.translate(trans)

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Regex to find <sup>123</sup> and convert to <sup>๑๒๓</sup>
# Capture the digits inside <sup> and </sup>
def replace_func(match):
    num = match.group(1)
    return f"<sup>{arabic_to_thai(num)}</sup>"

new_content = re.sub(r"<sup>(\d+)</sup>", replace_func, content)

# Also handle ranges if they exist e.g. <sup>3-4</sup> -> <sup>๓-๔</sup>
def replace_range_func(match):
    num1 = match.group(1)
    num2 = match.group(2)
    return f"<sup>{arabic_to_thai(num1)}-{arabic_to_thai(num2)}</sup>"

new_content = re.sub(r"<sup>(\d+)-(\d+)</sup>", replace_range_func, new_content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Converted footnotes to Thai numerals in {file_path}")
