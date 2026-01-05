import re
import unicodedata
import difflib

def normalize_thai(text):
    # Remove zero width spaces and other invisible chars
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    # Replace some common PUA or weird chars if known, but NFKC handles many
    return text

def aggressive_clean(line):
    # Remove all whitespace
    line = re.sub(r'\s+', '', line)
    # Remove page numbers artifacts?
    # Maybe header/footer removal is needed first.
    return line

def read_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

def compare_files(raw_path, md_path):
    raw_lines = read_lines(raw_path)
    md_lines = read_lines(md_path)

    # Pre-process steps
    # 1. Join all lines into a big string to handle reflow
    # But wait, raw text has explicit newlines that might not match MD paragraphs exactly if MD is reflowed.
    # However, usually PDF raw extraction preserves lines.
    
    # Let's try to filter out page headers/footers from RAW first.
    # Raw often has: ^L (form feed) followed by line 1, 2 (headers), and last lines (footers).
    # Looking at raw file, lines 1, 2 are headers, lines 33,34 are footers (Page 1).
    # Page 2 starts at line 35.
    
    # Strategy: Remove lines that look like page numbers or known headers/footers in RAW.
    clean_raw = []
    for line in raw_lines:
        s = line.strip()
        # Skip empty
        if not s: continue
        # Skip obvious page breaks
        if '\x0c' in line:
            # removing form feed char but keeping text if any
            line = line.replace('\x0c', '')
            s = line.strip()
            if not s: continue
        
        # Skip headers/footers pattern
        if "ข้อมูลฉับไว" in s or "สายด่วนศาลปกครอง" in s or "TRUST" in s:
            continue
        # Skip page numbers if line is just digits
        if re.match(r'^\d+$', s) or re.match(r'^หน้า \d+$', s):
            continue
        
        # Also skip lines that are just "บทที่ ..." or "แนวคำวินิจฉัย..." if they are headers repeated?
        # Actually MD keeps headers.
        
        clean_raw.append(normalize_thai(s).replace(" ", ""))

    clean_md = []
    for line in md_lines:
        s = line.strip()
        if not s: continue
        # MD also has headers/footers in the file? 
        # Looking at file content:
        # Line 30: ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน
        # So MD has them too!
        if "ข้อมูลฉับไว" in s or "สายด่วนศาลปกครอง" in s or "TRUST" in s:
            continue
            
        clean_md.append(normalize_thai(s).replace(" ", ""))

    # Compare content
    # We'll use a set of strings for rapid check, or join them.
    
    raw_text = "".join(clean_raw)
    md_text = "".join(clean_md)
    
    # Now compare exact match
    if raw_text == md_text:
        print("PERFECT MATCH (ignoring whitespace and recognized footers)")
    else:
        print(f"Mismatch! RAW len: {len(raw_text)}, MD len: {len(md_text)}")
        # Find where they differ
        matcher = difflib.SequenceMatcher(None, raw_text, md_text)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                print(f"{tag} raw[{i1}:{i2}] vs md[{j1}:{j2}]")
                raw_snippet = raw_text[i1:i2]
                md_snippet = md_text[j1:j2]
                print(f"RAW: {raw_snippet!r}")
                print(f"MD : {md_snippet!r}")
                print("-" * 20)

if __name__ == "__main__":
    compare_files(
        '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_03_raw.txt',
        '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_03.md'
    )
