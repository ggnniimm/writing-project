import re
import os

filepath = "administrative_court_rulings_vol_09.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Lao numerals to Thai
content = content.replace('໑', '๑')
content = content.replace('໒', '๒')
content = content.replace('໓', '๓')

# 2. Trailing garbage in lines
lines = content.split('\n')
new_lines = []
for line in lines:
    clean_line = line.strip()
    if clean_line == ">": continue # Remove lines that are just '>'
    new_lines.append(line)

content = '\n'.join(new_lines)

# 3. Standardize whitespace
# Reduce 3+ newlines to 2
content = re.sub(r'\n{3,}', '\n\n', content)

# 4. Standardize page header format (optional but good)
# Ensure consistent spacing around chapters
content = re.sub(r'\n# บทที่', '\n\n# บทที่', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Final polish complete.")
