
import os
import re

def to_thai_numerals(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    trans = str.maketrans(arabic_digits, thai_digits)
    return text.translate(trans)

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to convert Arabic nums to Thai nums in text content.
    # But we should be careful about URL or specific English terms if any.
    # Looking at the files, they are Thai legal text. URLs usually aren't there.
    # Even if there are footnote markers <sup>50</sup>, ideally they should be Thai too based on previous context 
    # (previous turns debated this, but generally this project prefers Thai everywhere).
    # BUT, the verification script flags "Arabic numeral in Thai context".
    
    # Let's simple translate ALL Arabic digits to Thai digits found in the text.
    # Exception: Markdown link definitions [link]: http://... might break?
    # These files don't seem to have external links.
    
    new_content = to_thai_numerals(content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Fixed {os.path.basename(filepath)}")
    else:
        print(f"no changes in {os.path.basename(filepath)}")

def main():
    base_dir = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07"
    files = [f"part_{i}.md" for i in range(47, 57)]
    
    for filename in files:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            fix_file(filepath)
        else:
            print(f"File not found: {filename}")

if __name__ == "__main__":
    main()
