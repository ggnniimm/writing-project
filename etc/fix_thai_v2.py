#!/usr/bin/env python3
"""
Fix Thai character encoding issues in the document.
This script replaces corrupted Thai vowel/tone mark patterns with correct ones.
"""

import re
import sys
from pathlib import Path

# Dictionary of character replacements
# Pattern: (corrupted, correct)
REPLACEMENTS = [
    # Common patterns with ป + vowel/tone corruption
    ("บปาน", "บ้าน"),
    ("แลปว", "แล้ว"),
    ("ยปาย", "ย้าย"),
    ("รปอน", "ร้อน"),
    ("หปา", "ห้า"),
    ("ปตว", "ป่วย"),
    ("ฟภง", "ฟัง"),
    ("ชบอง", "ช่อง"),
    ("ปลบอย", "ปล่อย"),
    ("เชบา", "เช่า"),
    ("ตปอน", "ต้อน"),
    ("เขต่าง", "เขตบาง"),  # เขตบางขุนเทียน
    ("ปถอง", "ป้อง"),
    ("ผบา", "ผ่า"),
    ("หมบอม", "หม่อม"),
    ("สูบ", "สู่"),
    ("ซปาย", "ซ้าย"),
    ("คุปม", "คุ้ม"),
    ("ดบาน", "ด่าน"),
    ("เรปอย", "เรียบร้อย"),
    ("เรียบรปอย", "เรียบร้อย"),
    ("แบปง", "แบ่ง"),
    ("สลากกินแบปง", "สลากกินแบ่ง"),
    ("งดเวปน", "งดเว้น"),
    ("มบ ", "ม์ "),
    ("เชียงใหมบ", "เชียงใหม่"),
    ("กรุงเทพมหานครบ", "กรุงเทพมหานคร"),
    ("ทำทบา", "ท่าเรือ"),  # การทำท่าเรือ
    ("เจ้าทบา", "เจ้าท่า"),
    ("ทบาช้าง", "ท่าช้าง"),
    ("การทบา", "การท่า"),
    ("เทบา", "เท่า"),
    ("นบา", "น่า"),
    ("พอลิเมอรพ", "พอลิเมอร์"),
    ("อุปกรณพ", "อุปกรณ์"),
    ("แพทยศาสตรพ", "แพทยศาสตร์"),
    ("วิศวกรรมศาสตรพ", "วิศวกรรมศาสตร์"),
    ("คณะสงฆพ", "คณะสงฆ์"),
    ("ศรีสงครามพ", "ศรีสงคราม"),
    ("ธานีพ", "ธานี"),
    ("สุราษฎรพ", "สุราษฎร์"),
    ("คมนาคมพ", "คมนาคม"),
    ("พาณิชยพ", "พาณิชย์"),
    ("มหาวิทยาลัยพ", "มหาวิทยาลัย"),
    ("บุรีรัมยพ", "บุรีรัมย์"),
    ("กุมภาพันธพ", "กุมภาพันธ์"),
    ("มีนาคมพ", "มีนาคม"),
    ("เมษายนพ", "เมษายน"),
    ("พฤษภาคมพ", "พฤษภาคม"),
    ("พฤศจิกายนพ", "พฤศจิกายน"),
    ("ธันวาคมพ", "ธันวาคม"),
    ("เบญจลักษพ", "เบญจลักษณ์"),
    ("พิสูจนพ", "พิสูจน์"),
    ("อุทธรณพ", "อุทธรณ์"),
    ("ยุติธรรมพ", "ยุติธรรม"),
    ("เผยแพรบ", "เผยแพร่"),
    ("เว็บไซตพ", "เว็บไซต์"),
    ("ไกลบ", "ไกล่"),
    ("ขับไลบ", "ขับไล่"),
    ("รถไฟฟ้า ร.ฟ.ทบ", "รถไฟฟ้า ร.ฟ.ท."),
    ("ไทยบ", "ไทย"),
    ("แมปว่า", "แม้ว่า"),
    ("แมปจะ", "แม้จะ"),
    ("แมปผู้", "แม้ผู้"),
    ("แมปเป็น", "แม้เป็น"),
    ("แมป", "แม้"),
    ("นบาจะ", "น่าจะ"),
    ("ถบาย", "ถ่าย"),
    ("สหกรณพ", "สหกรณ์"),
    ("เอ็นพ", "เอ็น"),
    ("การเงินพ", "การเงิน"),
    ("ในอันที่พ", "ในอันที่"),
    ("กฎหมายพ", "กฎหมาย"),
    ("รัมยพ", "รัมย์"),
    ("มหิดลพ", "มหิดล"),
    ("เทียนพ", "เทียน"),
    ("ขุนเทียนพ", "ขุนเทียน"),
    ("ปทุมธานีพ", "ปทุมธานี"),
    ("บดีพ", "บดี"),
]

# Additional regex patterns
REGEX_REPLACEMENTS = [
    # Fix พ at end of Thai words that should be ์
    (r'(\w)พ(\s|$|\.)', r'\1์\2'),
]

def fix_file(filepath: str) -> tuple[int, int]:
    """
    Fix Thai encoding issues in a file.
    Returns (total_replacements, lines_changed)
    """
    path = Path(filepath)
    content = path.read_text(encoding='utf-8')
    original = content
    
    total_replacements = 0
    
    # Apply simple string replacements
    for corrupted, correct in REPLACEMENTS:
        count = content.count(corrupted)
        if count > 0:
            content = content.replace(corrupted, correct)
            total_replacements += count
            print(f"  Replaced '{corrupted}' → '{correct}' ({count} times)")
    
    # Apply regex replacements
    for pattern, replacement in REGEX_REPLACEMENTS:
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            print(f"  Regex pattern: {pattern} ({matches} matches)")
            total_replacements += matches
    
    if content != original:
        path.write_text(content, encoding='utf-8')
        lines_changed = sum(1 for a, b in zip(original.split('\n'), content.split('\n')) if a != b)
        return total_replacements, lines_changed
    
    return 0, 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_thai_v2.py <filepath>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"Fixing Thai encoding in: {filepath}")
    
    replacements, lines = fix_file(filepath)
    
    if replacements > 0:
        print(f"\n✓ Applied {replacements} replacements across {lines} lines")
    else:
        print("\n✓ No replacements needed")

if __name__ == "__main__":
    main()
