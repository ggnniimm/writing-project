
import re

file_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07/part_38.md"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

cleaned_lines = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    original_line = line
    line = line.strip()
    
    # 1. Remove "TRUST" lines
    # Patterns: "TRUST ศาลปกครอง...", "ศาลปกครอง... TRUST", "TRUST"
    if "TRUST" in line or "ศาลปกครองแห่งความเชื่อมั่น" in line:
        continue
    
    # 2. Fix Header/Page Number
    # Pattern: "แนวคำวินิจฉัยของศาลปกครอง ๗๒๕" -> "๗๒๕ แนวคำวินิจฉัยของศาลปกครอง"
    match_a = re.match(r"^(แนวคำวินิจฉัยของศาลปกครอง)\s+([๐-๙]+)$", line)
    if match_a:
        cleaned_lines.append(f"{match_a.group(2)} {match_a.group(1)}")
        continue
        
    # 3. Handle broken footnote definitions (The markers)
    # We see lines with just "๑๑", "๑๒-๑๔", "๑๕-๑๖", "๑๗-๑๘", "๑๗-๑ ๘" etc.
    # Regex for just Thai numerals/ranges, identifying them as likely footnote headers if they are short and isolated.
    # Note: Sometimes there might be whitespace or "-".
    
    # Check if line is just footnote number(s)
    # Allow whitespace around dash
    is_footnote_def = re.match(r"^([๐-๙]+)(?:\s*-\s*([๐-๙]+))?$", line)
    
    if is_footnote_def and i + 1 < len(lines):
        # Look ahead to see if it's followed by text (likely the definition content)
        next_line = lines[i+1].strip()
        if next_line and not re.match(r"^[๐-๙]+$", next_line): # Ensure next line isn't just a page number
             # It is a footnote definition header.
             # Merge it with next line and wrap in <sup>
             ft_marker = line.replace(" ", "") # Remove internal spaces like in 17-1 8 if any, though regex above handles standard cases.
             # Actually, let's keep the dash clean.
             ft_marker = re.sub(r'\s', '', line)
             
             merged = f"<sup>{ft_marker}</sup> {next_line}"
             cleaned_lines.append(merged)
             skip_next = True
             continue

    # 4. Remove standalone page break markers if any
    if line == "---":
        continue

    # Keep original indentation or strip?
    # Original file has indentation. Let's try to preserve relative layout if meaningful, 
    # but based on previous cleanups, stripping and re-paragraphing or just keeping non-empty lines is better.
    # The previous script stripped. Let's strip to avoid weird spaces, but maybe keep paragraph breaks.
    
    cleaned_lines.append(original_line.rstrip())

# Join content
content = "\n".join(cleaned_lines)
content = re.sub(r'\n{3,}', '\n\n', content) # Max 2 newlines

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Cleanup complete.")
