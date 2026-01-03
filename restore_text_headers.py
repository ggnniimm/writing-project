import re

file_path = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_57.md"

# Format: (Trigger Line Content, Header To Insert)
# Trigger is the Table Header lines we inserted earlier.
# grep showed missing: 1151, 1153, 1155, 1157, 1159
# Page 7 (1151): Starts with คร.๒๖๐/๒๕๖๓
# Page 9 (1153): Starts with ฟผ.๑/๒๕๖๔
# Page 11 (1155): Starts with ๒๕๒/๒๕๖๔
# Page 13 (1157): Starts with คผ.๙/๒๕๖๔
# Page 15 (1159): Starts with คร.๘๖/๒๕๖๔

inserts = [
    ("| คร.๒๖๐/๒๕๖๓ |", "แนวคำวินิจฉัยของศาลปกครอง ๑๑๕๑\n\n"),
    ("| ฟผ.๑/๒๕๖๔ |", "แนวคำวินิจฉัยของศาลปกครอง ๑๑๕๓\n\n"),
    ("| ๒๕๒/๒๕๖๔ |", "แนวคำวินิจฉัยของศาลปกครอง ๑๑๕๕\n\n"),
    ("| คผ.๙/๒๕๖๔ |", "แนวคำวินิจฉัยของศาลปกครอง ๑๑๕๗\n\n"),
    ("| คร.๘๖/๒๕๖๔ |", "แนวคำวินิจฉัยของศาลปกครอง ๑๑๕๙\n\n")
]

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
# We need to look for the *Table Header block* preceding these rows.
# Currently the file looks like:
# | คำสั่ง... | หน้า |
# |---|---|
# | Case... | ... |

# We want to insert the Page Header *before* the Table Header block.
# Since we processed the file linearly, we can just look for the row (Case Number)
# and insert the header 2-3 lines *before* it?
# No, easier: Identify the "Case Number" line, go back 2 lines (before the table header), and insert there.
# But iterating backwards is tricky.

# Simpler: Iterate through lines.
# If we see the Case Number in `inserts`:
#   We know the previous 2 lines are table headers (inserted in previous step).
#   We should have inserted the "Page Header" BEFORE those table headers.
#   So we need to find where those table headers *are*.
#   Actually, in the previous step we inserted: "\n\n| คำสั่ง... | หน้า |\n|---|---|\n"
#   So we can look for that block followed by the Case Number?
#   Or just look for the Case Number, and if found, insert the Page Header *before* the previous 3 lines?

# Let's try a replace approach on the full string?
content = "".join(lines)

for trigger, header in inserts:
    # Trigger is the row e.g. "| คร.๒๖๐/๒๕๖๓ |"
    # The context in file is:
    # \n\n| คำสั่งศาลปกครองสูงสุดที่ | หน้า |\n|---|---|\n| คร.๒๖๐/๒๕๖๓ |
    
    # We want to change it to:
    # \n\nHeader 1151\n\n| คำสั่งศาลปกครองสูงสุดที่ | หน้า |\n|---|---|\n| คร.๒๖๐/๒๕๖๓ |
    
    # Construct the search block
    # Note: potential spacing issues.
    search_block = f"| คำสั่งศาลปกครองสูงสุดที่ | หน้า |\n|---|---|\n{trigger}"
    replace_block = f"{header}| คำสั่งศาลปกครองสูงสุดที่ | หน้า |\n|---|---|\n{trigger}"
    
    if search_block in content:
        content = content.replace(search_block, replace_block)
    else:
        print(f"Could not find block for {trigger}")

with open(file_path, 'w') as f:
    f.write(content)

print("Headers inserted.")
