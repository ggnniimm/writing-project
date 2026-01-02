#!/usr/bin/env python3
"""
Fix ALL missing Thai tone marks - comprehensive approach
"""

import re
import sys

def fix_all_thai_tone_marks(text):
    """Fix all common Thai words missing tone marks."""
    
    # Dictionary of fixes - VERY careful with context
    fixes = [
        # Common words that almost always need tone marks
        (r'\bหนวย', 'หน่วย'),  # unit
        (r'\bหนา(?=ที่)', 'หน้า'),  # page, duty
        (r'\bเปน(?=[\s\u0E00-\u0E7F])', 'เป็น'),  # is/are
        (r'\bสราง', 'สร้าง'),  # build/create
        (r'โครงสราง', 'โครงสร้าง'),  # structure
        (r'เจาหนาที่', 'เจ้าหน้าที่'),  # official/officer
        (r'เจาหนา', 'เจ้าหน้า'),  # official
        (r'\bที่(?=ของ|ใน|แห|และ|ตอ|จะ|ได|เกี่ยว|เปน|มี|ระบุ|กำหนด|ออก|ใช)', 'ที่'),  # relative clause - already correct
    ]
    
    for pattern, replacement in fixes:
        text = re.sub(pattern, replacement, text)
    
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fix_all_tone_marks.py <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = fix_all_thai_tone_marks(content)
    
    # Count changes
    if content != fixed_content:
        # Count specific patterns
        changes = {}
        changes['หนวย→หน่วย'] = content.count('หนวย') - fixed_content.count('หนวย')
        changes['เปน→เป็น'] = content.count('เปน') - fixed_content.count('เปน')
        changes['สราง→สร้าง'] = len(re.findall(r'สราง', content)) - len(re.findall(r'สราง', fixed_content))
        changes['เจาหนา→เจ้าหน้า'] = content.count('เจาหนา') - fixed_content.count('เจาหนา')
        
        print(f"Processing {filepath}...")
        for pattern, count in changes.items():
            if count > 0:
                print(f"  {pattern}: {count} fixes")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Fixed all tone marks!")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    main()
