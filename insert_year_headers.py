import re

file_path = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_57.md"

table_header = "| คำสั่งศาลปกครองสูงสุดที่ | หน้า |"

with open(file_path, 'r') as f:
    content = f.read()

# Split content by the header
parts = content.split(table_header)

# parts[0] is content before first header (Page 1 top)
# parts[1] is content between header 1 and 2 (Page 1 body ... Page 2 top)
# ...
# We want to append the Year Line to the end of parts[0], parts[1]... parts[N-1]
# EXCEPT parts[0] might already have it (Page 1).
# Let's rebuild the content.

new_content = parts[0] # Start with pre-first-header

# Page 1 is already handled?
# Page 1 top has: ... พ.ศ. ๒๕๖๓ ... | Header | (so parts[0] ends with 2563 \n\n)
# Actually, checking Page 1 view:
# Line 4: พ.ศ. ๒๕๖๓
# Line 6: | คำสั่ง...
# So parts[0] includes Line 4. We don't need to add it there.

# Total occurrences should be 16 (Page 1-16).
# len(parts) should be 17.

print(f"Total parts: {len(parts)}")

# Occurrences 2 to 8 (Pages 2-8): 2563
# Occurrences 9 to 15 (Pages 9-15): 2564
# Occurrence 16 (Page 16): 2559

for i in range(1, len(parts)):
    # i represents the index of the header being inserted (1-based count of headers processed so far)
    # The loop processes parts[i].
    # But wait, we are reconstructing.
    # parts[0] + HEADER + parts[1] + HEADER ...
    
    # We want to insert Year BEFORE the header.
    # So we modify the end of parts[i-1].
    
    # i=1: Insert before Header 2 (Page 2). Year 2563.
    # i=2: Insert before Header 3 (Page 3). Year 2563.
    # ...
    # i=7: Insert before Header 8 (Page 8). Year 2563.
    # i=8: Insert before Header 9 (Page 9). Year 2564.
    # ...
    # i=14: Insert before Header 15 (Page 15). Year 2564.
    # i=15: Insert before Header 16 (Page 16). Year 2559.
    
    year_line = ""
    
    # Headers are at indices 1 to 15 (if 0-indexed matches)
    # i matches the loop index if we start loop at 1.
    # Header 1 is skipped (already in parts[0] end, untouched).
    
    if 1 <= i <= 7:
        year_line = "พ.ศ. ๒๕๖๓\n"
    elif 8 <= i <= 14:
        year_line = "พ.ศ. ๒๕๖๔\n"
    elif i == 15:
        year_line = "พ.ศ. ๒๕๕๙\n" # Page 16
        
    # Append the Header (which was consumed by split) and the next part
    # But we want to insert year_line BEFORE the header.
    # So actually: new_content += year_line + table_header + parts[i]
    
    new_content += year_line + table_header + parts[i]

with open(file_path, 'w') as f:
    f.write(new_content)

print("Year headers inserted.")
