import re
import sys
import unicodedata

def normalize(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    return re.sub(r'\s+', '', text)

def extract_thai_numerals(text):
    # Normalize text first so characters like ำ are handled consistently
    text = unicodedata.normalize('NFKC', text)
    return re.findall(r'[๐-๙]+', text)

def compare_files(md_path, txt_path):
    print(f"Comparing {md_path} with {txt_path}\n")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    md_nums = extract_thai_numerals(md_content)
    txt_nums = extract_thai_numerals(txt_content)
    
    print(f"Thai Numeral Count - MD: {len(md_nums)}, PDF: {len(txt_nums)}")
    
    if len(md_nums) != len(txt_nums):
        print("\nNumeral differences:")
        limit = min(len(md_nums), len(txt_nums))
        for i in range(limit):
            if md_nums[i] != txt_nums[i]:
                print(f"Diff at index {i}: MD='{md_nums[i]}', PDF='{txt_nums[i]}'")
                # Show context in MD
                # Find the numeral in the content
                matches = list(re.finditer(f'({re.escape(md_nums[i])})', md_content))
                # This is tricky because one numeral might appear many times.
                # Let's just print a few before and after.
                break
        if len(md_nums) > len(txt_nums):
            print(f"Extra in MD: {md_nums[limit:]}")
        else:
            print(f"Extra in PDF: {txt_nums[limit:]}")

    ascii_digits = re.findall(r'[0-9]', md_content)
    if ascii_digits:
        print(f"⚠️ Found {len(ascii_digits)} ASCII digits in MD: {set(ascii_digits)}")
    else:
        print("✅ No ASCII digits found in MD.")

    # Check for specific footers that should be removed
    footers = ["สายด่วนศาลปกครอง ๑๓๕๕", "ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน"]
    for footer in footers:
        count = md_content.count(footer)
        if count > 0:
            print(f"⚠️ Found {count} instances of footer: {footer}")

if __name__ == "__main__":
    compare_files(sys.argv[1], sys.argv[2])
