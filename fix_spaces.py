
import re
import sys

def fix_spaces(file_path):
    print(f"Fixing spaces in {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Slogan
    # The clean version looks like: ยื่นฟ้องออนไลน์สะดวกรวดเร็วเป็นธรรม
    # We want: ยื่นฟ้องออนไลน์ สะดวก รวดเร็ว เป็นธรรม
    # Or strict replacement
    content = content.replace("ยื่นฟ้องออนไลน์สะดวกรวดเร็วเป็นธรรม", "ยื่นฟ้องออนไลน์ สะดวก รวดเร็ว เป็นธรรม")
    
    # Fix 2: Hotline
    # Clean: สายด่วนศาลปกครอง๑๓๕๕
    # Want: สายด่วนศาลปกครอง ๑๓๕๕
    # Using regex to capture the number part just in case
    content = re.sub(r'สายด่วนศาลปกครอง([๐-๙]+)', r'สายด่วนศาลปกครอง \1', content)

    # Fix 3: Header Page Number
    # Clean: แนวคำวินิจฉัยของศาลปกครอง๖๒๙
    # Want: แนวคำวินิจฉัยของศาลปกครอง ๖๒๙
    content = re.sub(r'แนวคำวินิจฉัยของศาลปกครอง([๐-๙]+)', r'แนวคำวินิจฉัยของศาลปกครอง \1', content)

    # Fix 4: Also "บทที่๓๓" -> "บทที่ ๓๓" type patterns?
    # Maybe too risky universally, but headers usually:
    # "บทที่ ๓๓" -> Cleaned to "บทที่๓๓"? YES.
    # Let's verify if "บทที่" needs fixing.
    content = re.sub(r'บทที่([๐-๙]+)', r'บทที่ \1', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        fix_spaces(arg)
