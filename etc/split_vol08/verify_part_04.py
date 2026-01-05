import re
import unicodedata

def normalize_thai(text):
    # Remove zero width spaces and other invisible chars
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    return text

def read_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

def compare_files(raw_path, md_path):
    raw_lines = read_lines(raw_path)
    md_lines = read_lines(md_path)

    # Filter out headers/footers from RAW
    clean_raw = []
    for line in raw_lines:
        s = line.strip()
        if not s: continue
        # Skip form feed
        if '\x0c' in line:
            line = line.replace('\x0c', '')
            s = line.strip()
            if not s: continue
        
        # Skip headers/footers pattern
        if "ข้อมูลฉับไว" in s or "สายด่วนศาลปกครอง" in s or "TRUST" in s:
            continue
        # Skip page numbers
        if re.match(r'^\d+$', s) or re.match(r'^หน้า \d+$', s):
            continue
        
        clean_raw.append(normalize_thai(s).replace(" ", ""))

    clean_md = []
    for line in md_lines:
        s = line.strip()
        if not s: continue
        # MD also has headers/footers
        if "ข้อมูลฉับไว" in s or "สายด่วนศาลปกครอง" in s or "TRUST" in s:
            continue
        # Skip markdown headers
        if s.startswith('#'):
            continue
            
        clean_md.append(normalize_thai(s).replace(" ", ""))

    # Compare content
    raw_text = "".join(clean_raw)
    md_text = "".join(clean_md)
    
    if raw_text == md_text:
        print("PERFECT MATCH (ignoring whitespace and recognized footers)")
    else:
        print(f"Mismatch! RAW len: {len(raw_text)}, MD len: {len(md_text)}")
        print(f"Difference: {abs(len(raw_text) - len(md_text))} characters")

if __name__ == "__main__":
    compare_files(
        '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_04_raw.txt',
        '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_04.md'
    )
