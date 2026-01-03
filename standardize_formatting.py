import os
import glob
import re

# Directory path
base_dir = "etc/Academic_291121_112321_parts"

# Footer lines to remove (exact matches or containing specific phrases)
footer_markers = [
    "ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน",
    "สายด่วนศาลปกครอง ๑๓๕๕",
    "TRUST",
    # Decomposed/Alternative representations found in extraction
    "ขอ้ มลู ฉบั ไว ไขขอ้ ขอ้ งใจ ใสใ่ จประชาชน", 
    "สายดว่ นศาลปกครอง ๑๓๕๕",
    "ขอ้ มลู ฉบั ไว",
    "สายดว่ นศาลปกครอง"
]

# Regex patterns for indentation
# Note: matched groups preserve the text content
# We strip existing leading whitespace and apply fixed indentation
patterns = [
    # Level 0: "1. " -> Keep at 0 indentation
    (re.compile(r'^\s*([๐-๙]+\.\s.*)'), ""), 
    
    # Level 1: "1.1 " -> 4 spaces
    (re.compile(r'^\s*([๐-๙]+\.[๐-๙]+\s.*)'), "    "),
    
    # Level 2: "1.1.1 " -> 8 spaces
    (re.compile(r'^\s*([๐-๙]+\.[๐-๙]+\.[๐-๙]+\s.*)'), "        "),
    
    # Level 3: "1.1.1.1 " -> 12 spaces
    (re.compile(r'^\s*([๐-๙]+\.[๐-๙]+\.[๐-๙]+\.[๐-๙]+\s.*)'), "            "),
    
    # Level 1 with parenthesis: "1.4) " -> 4 spaces
    (re.compile(r'^\s*([๐-๙]+\.[๐-๙]+\)\s.*)'), "    "),
    
    # Level 2 with parenthesis: "1.4.1) " -> 8 spaces
    (re.compile(r'^\s*([๐-๙]+\.[๐-๙]+\.[๐-๙]+\)\s.*)'), "        "),
]

# Header Regex (e.g., "๑๐๐ แนว..." or "แนว... ๑๐๐")
# Broad match for "Classification/Guidelines ... of Administrative Court"
header_pattern = re.compile(r'^\s*(?:[๐-๙]+\s+)?แนว.*?ของศาลปกครอง(?:\s+[๐-๙]+)?\s*$')

def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    skipped_count = 0
    modified_count = 0
    header_isolation_count = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 1. Remove Footers
        is_footer = False
        for marker in footer_markers:
            if marker in stripped and len(stripped) < len(marker) + 10: 
                is_footer = True
                break
        
        if is_footer:
            skipped_count += 1
            continue

        # 2. Check for Page Header to isolate
        # Logic: If it's a header, ensure we have a blank line before (if not start) and after.
        # But we are building separate new_lines list, so we check new_lines[-1].
        
        is_header = header_pattern.match(line)
        
        final_line = line
        matched_indent = False
        
        # 3. Apply Indentation (only if not a Page Header)
        if not is_header and re.match(r'^\s*[๐-๙]', line):
             # Try patterns
             for pat, indent_str in patterns:
                 m = pat.match(line)
                 if m:
                     # Remove original indentation (which matched regex) and apply new
                     # Wait, regex captures the content including numerals. 
                     # \1 is the captured group "1.1 Content".
                     # We replace the whole line with "    " + group(1).
                     final_line = indent_str + m.group(1) + "\n"
                     matched_indent = True
                     break
        
        if matched_indent and final_line != line:
            modified_count += 1
            
        # Write logic with isolation
        if is_header:
            # Ensure blank line before
            if new_lines and new_lines[-1].strip() != "":
                new_lines.append("\n")
                header_isolation_count += 1
            
            new_lines.append(final_line.strip() + "\n") # Trim and newline
            
            # Ensure blank line after (we can't lookahead easily, but we can append an extra newline now)
            # Actually, let's just append it. If the next line is also blank, we might double up matching blank lines later?
            # A simple rule: Append "\n" after header.
            new_lines.append("\n")
            header_isolation_count += 1
        else:
            new_lines.append(final_line)

    if skipped_count > 0 or modified_count > 0 or header_isolation_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Processed {os.path.basename(file_path)}: Removed {skipped_count}, Indented {modified_count}, Isolated Headers {header_isolation_count} times.")

# Main execution
files = sorted(glob.glob(os.path.join(base_dir, "*.md")))
print(f"Found {len(files)} files.")
for file in files:
    clean_file(file)
