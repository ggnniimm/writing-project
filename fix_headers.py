
import re

md_path = "etc/Academic_310717_154727-2_parts/part_08.md"

with open(md_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Fix corruption: ๑๓๑๕ -> ๑๒๕, ๑๓๑๗ -> ๑๒๗...
    # Regex: ๑๓๑([๕-๙]) -> ๑๒\1
    if "๑๓๑" in line:
        line = re.sub(r"๑๓๑([๕-๙])", r"๑๒\1", line)
    new_lines.append(line)

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Headers fixed.")

# Check Headers
headers = [l.strip() for l in new_lines if "แนวคำวินิจฉัย" in l]
print(f"\nFound {len(headers)} Headers:")
for h in headers:
    # Extract number
    num = re.search(r"[๑-๙]+", h)
    n = num.group(0) if num else "?"
    print(f"{n}: {h}")

