
path = 'etc/Academic_281020_102051_parts/Academic_281020_102051_part_18.md'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "พื้นที่ดังกล่าวเป็นที่ดอน" in line or "เป็นที่ดอน" in line:
        print(f"Match 362 at line {i+1}: {line.strip()}")
        
    if "๙" in line and "๑๐" in line:
        print(f"Match 358 at line {i+1}: {line.strip()}")
