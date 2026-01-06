import os
import re
import glob

BASE_DIR = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08"

def to_thai_numerals(text):
    thai_numerals = "๐๑๒๓๔๕๖๗๘๙"
    arabic_numerals = "0123456789"
    trans = str.maketrans(arabic_numerals, thai_numerals)
    return text.translate(trans)

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    new_lines = []
    changed = False
    
    for line in lines:
        # Safeguards: Don't convert if line looks like a URL or English footer
        if "http" in line or "TRUST" in line or "Information" in line:
            new_lines.append(line)
            continue
            
        # Check if line contains Arabic numerals
        if re.search(r"[0-9]", line):
            # Convert
            new_line = to_thai_numerals(line)
            # If conversion happened but we want to double check we didn't break something...
            # For now, simplistic global replace per line is requested strategy
            new_lines.append(new_line)
            changed = True
        else:
            new_lines.append(line)
            
    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    files = sorted(glob.glob(os.path.join(BASE_DIR, "part_*.md")))
    print(f"🔄 Scanning {len(files)} files for numeral fixes...")
    
    count = 0
    for file_path in files:
        if process_file(file_path):
            print(f"   Fixed numerals in: {os.path.basename(file_path)}")
            count += 1
            
    print(f"✅ Auto-corrected numerals in {count} files.")

if __name__ == "__main__":
    main()
