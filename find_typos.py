
import re

path = 'etc/Academic_281020_102051_parts/Academic_281020_102051_part_17.md'

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

targets = [
    '๒๔๙๕',
    '๒๙๙๗',
    '๔๖๖',
    '๔๙๕๐',
    'พุทธศักราช ๒๕๕๐ ที่ใช้บัง' 
]

for i, line in enumerate(lines):
    for t in targets:
        if t in line:
            print(f"Line {i+1}: {line.strip()}")
