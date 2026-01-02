
import os

extracted_path = '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/part_05_extracted.txt'
md_path = '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_v14_2569_40/part_05.md'

with open(extracted_path, 'r', encoding='utf-8') as f:
    extracted_lines = f.readlines()

# Extract lines 521 to 605 (1-based), which is index 520 to 605 (exclusive)
source_content = extracted_lines[520:605]

with open(md_path, 'r', encoding='utf-8') as f:
    md_lines = f.readlines()

# Replace lines 522 to 531 (1-based)
# Index 521 corresponds to line 522.
# Index 531 corresponds to line 532 (which is (6)... and should be kept).
# So we want to replace md_lines[521:531]
start_idx = 521
end_idx = 531

print(f"Replacing lines {start_idx+1}-{end_idx} in {md_path}")
print(f"Original content start: {md_lines[start_idx].strip()}")
print(f"Original content end: {md_lines[end_idx-1].strip()}")
print(f"Next line (should be (6)...): {md_lines[end_idx].strip()}")

new_md_lines = md_lines[:start_idx] + source_content + md_lines[end_idx:]

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(new_md_lines)

print("Patch applied successfully.")
