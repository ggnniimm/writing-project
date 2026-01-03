
import re

def extract_lines_with_char(path, char):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    extracted = []
    for i, line in enumerate(lines):
        if char in line:
            # Normalize to avoid spacing issues
            norm_line = re.sub(r'\s+', '', line.strip())
            extracted.append(norm_line)
    return extracted

pdf_lines = extract_lines_with_char("debug_clean_pdf.txt", "๖")
md_lines = extract_lines_with_char("/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_281020_102051_parts/Academic_281020_102051_part_05.md", "๖")

print(f"PDF Lines with ๖: {len(pdf_lines)}")
print(f"MD Lines with ๖: {len(md_lines)}")

# Find lines in PDF not in MD
print("\n--- In PDF but not in MD ---")
for pl in pdf_lines:
    if pl not in md_lines:
        print(f"Missing in MD: {pl[:100]}...")

# Find lines in MD not in PDF (extra?)
print("\n--- In MD but not in PDF ---")
for ml in md_lines:
    if ml not in pdf_lines:
        print(f"Extra in MD: {ml[:100]}...")
