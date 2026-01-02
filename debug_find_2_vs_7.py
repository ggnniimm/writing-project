import re
import sys

def extract_thai_numerals(text):
    return re.findall(r'[๐-๙]+', text)

def main(md_path, txt_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_text = f.read()

    md_nums = extract_thai_numerals(md_text)
    txt_nums = extract_thai_numerals(txt_text)
    
    LIMIT = min(len(md_nums), len(txt_nums))
    i = 0
    j = 0
    
    print(f"Scanning for MD=2 vs TXT=7 mismatch...")
    
    while i < len(md_nums) and j < len(txt_nums):
        m = md_nums[i]
        t = txt_nums[j]
        
        # Skip Artifacts
        if t == '๑๑๓๓๕๕๕๕':
            j += 1
            print(f"Skipping artifact at TXT {j-1}")
            continue
            
        if m == t:
            i += 1
            j += 1
            continue
            
        # Mismatch found
        if m == '๒' and t == '๗':
            print(f"FOUND 2 vs 7 Mismatch!")
            print(f"MD Index {i}: {m}")
            print(f"TXT Index {j}: {t}")
            print(f"MD Context: {md_nums[i-5:i+6]}")
            print(f"TXT Context: {txt_nums[j-5:j+6]}")
            return # Found it!
            
        # Try to resync
        print(f"Mismatch at {i}/{j}: MD={m} TXT={t}")
        # Simple heuristic: advance both? or advance one?
        # If we just advance one, we might drift.
        # But we are looking for substitution 2->7.
        # So likely they align here.
        
        i += 1
        j += 1

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
