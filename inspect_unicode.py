
path = 'etc/Academic_281020_102051_parts/Academic_281020_102051_part_13.md'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line = lines[561] # 0-indexed, so 562 is index 561
print(f"Line 562 content: {line.strip()}")
print("Unicode dump:")
for char in line.strip():
    print(f"{char}: U+{ord(char):04X}")
