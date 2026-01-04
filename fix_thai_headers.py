
import os
import re

def fix_content(content):
    # 1. Fix Sara AA + Nikhahit -> Sara AM
    # \u0e32 = Sara AA, \u0e4d = Nikhahit
    # Wrong order: AA + Nikhahit
    content = content.replace('\u0e32\u0e4d', '\u0e33')
    
    # 2. Fix Nikhahit + Sara AA -> Sara AM (Standardize decomposition to composed char)
    content = content.replace('\u0e4d\u0e32', '\u0e33')

    # 3. Fix specific corrupted header: "แนวคำวินิจฉัย..."
    # The corrupted version seen: แนวคาํ วนิ ิจฉยั ของศาลปกครอง ๒๖๑
    # Regex to capture the number and the position
    # Patterns:
    # A. Text ... Number
    # B. Number ... Text
    
    # We look for lines containing "แนว" and "ศาลปกครอง"
    lines = content.split('\n')
    new_lines = []
    
    header_pattern = re.compile(r'(.*)(แนว.*ศาลปกครอง)(.*)')
    
    for line in lines:
        if 'แนว' in line and 'ศาลปกครอง' in line:
            # Check if it looks like the header
            match = header_pattern.match(line)
            if match:
                prefix = match.group(1).strip()
                suffix = match.group(3).strip()
                
                # Identify page number in prefix or suffix
                page_num = ""
                # Check suffix first (e.g. " ๒๖๑")
                s_num = re.search(r'([๐-๙0-9]+)', suffix)
                p_num = re.search(r'([๐-๙0-9]+)', prefix)
                
                clean_header = "แนวคำวินิจฉัยของศาลปกครอง"
                
                if s_num:
                    # Format: Text Number
                    # Preserve the number
                    num = s_num.group(1)
                    # Reconstruct
                    new_line = f"{clean_header} {num}"
                    new_lines.append(new_line)
                elif p_num:
                    # Format: Number Text
                    num = p_num.group(1)
                    new_line = f"{num} {clean_header}"
                    new_lines.append(new_line)
                else:
                    # No number found? Just normalize the text part?
                    # If it's the header line without number (unlikely for this doc), 
                    # or maybe number is lost.
                    # We'll just fix the text part in the line.
                    new_line = line.replace(match.group(2), clean_header)
                    # Apply unicode fix again just in case
                    new_line = new_line.replace('\u0e32\u0e4d', '\u0e33').replace('\u0e4d\u0e32', '\u0e33')
                    # Fix 'วนิ ิจฉยั' -> 'วินิจฉัย'
                    new_line = new_line.replace('วนิ ิจฉยั', 'วินิจฉัย') 
                    # Actually better to just replace the matched text region.
                    new_lines.append(new_line)
            else:
                 new_lines.append(line)
        else:
            new_lines.append(line)
            
    content = '\n'.join(new_lines)
    
    # 4. General Fixes for "วนิ ิจฉยั" matching text body if any
    content = content.replace('วนิ ิจฉยั', 'วินิจฉัย')
    content = content.replace('คาํ', 'คำ')

    return content

src_dir = 'etc/Academic_281020_102051_parts'
files = sorted([f for f in os.listdir(src_dir) if f.endswith('.md')])

# Add the source text file to the list
files.append('../../pdf_extracted_text.txt')

count = 0
for fname in files:
    if fname.endswith('.txt'):
        path = os.path.join(src_dir, fname) # This will be wrong relative path
        # Fix path construction
        path = os.path.abspath(os.path.join(src_dir, fname))
    else:
        path = os.path.join(src_dir, fname)

    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()
    
    modified = fix_content(original)
    
    if original != modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(modified)
        print(f"Fixed {fname}")
        count += 1

print(f"Total files fixed: {count}")
