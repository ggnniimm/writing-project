import os
import re
import sys
import glob

def clean_content(text):
    lines = text.splitlines()
    new_lines = []
    
    # Compilation of regex patterns for garbage lines
    patterns = [
        re.compile(r'^แนวคำวินิจฉัยของศาลปกครอง\s+[๐-๙]+$'), # Header with page number suffix
        re.compile(r'^[๐-๙]+\s+แนวคำวินิจฉัยของศาลปกครอง$'), # Header with page number prefix
        re.compile(r'^ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน$'), # Footer slogan
        re.compile(r'^สายด่วนศาลปกครอง ๑๓๕๕$'), # Footer hotline
        re.compile(r'^TRUST$'), # Footer text
        re.compile(r'^--- Page \d+ ---$'), # Common OCR artifact
        re.compile(r'^\(Page \d+ is blank\)$'), # Blank page marker
    ]

    for line in lines:
        stripped = line.strip()
        is_garbage = False
        for p in patterns:
            if p.match(stripped):
                is_garbage = True
                break
        
        if not is_garbage:
            new_lines.append(line)

    # Normalize blank lines: Max 1 consecutive blank line
    final_lines = []
    blank_count = 0
    for line in new_lines:
        if not line.strip():
            blank_count += 1
            if blank_count <= 1: # Allow only 1 blank line
                final_lines.append(line)
        else:
            blank_count = 0
            final_lines.append(line)
            
    return "\n".join(final_lines)

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        cleaned_content = clean_content(content)
        
        # Ensure file ends with exactly one newline
        cleaned_content = cleaned_content.strip() + "\n"

        if cleaned_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    target_dir = "etc/Academic_281020_102051_parts"
    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        sys.exit(1)

    # Find all part_XX.md files
    files = glob.glob(os.path.join(target_dir, "Academic_281020_102051_part_*.md"))
    files.sort()

    print(f"Found {len(files)} files to check/standardize.")
    
    modified_count = 0
    for file in files:
        if process_file(file):
            print(f"Cleaned: {os.path.basename(file)}")
            modified_count += 1
    
    print(f"\nDone. {modified_count} files were updated.")

if __name__ == "__main__":
    main()
