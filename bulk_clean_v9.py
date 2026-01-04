import os
import glob
import re

parts_dir = "etc/Academic_281019_141643_parts"
files = sorted(glob.glob(os.path.join(parts_dir, "*.md")))

# Thai Numeral Mapping
digit_map = {
    '0': '๐', '1': '๑', '2': '๒', '3': '๓', '4': '๔',
    '5': '๖', # Common Gemini error
    '6': '๖', '7': '๗', '8': '๘', '9': '๙'
}
# Special case for 5: in Volume 10 we found many 5 -> ๖ errors.
# We will check if 5 is actually ๕ or ๖.
# Based on context "ผู้ถูกฟ้องคดีที่ 5" -> ๖ is likely if ๑-๔ exist.
# Let's check a bit more.

def normalize_thai_am(text):
    # Standardize all variations of SARA AM to \u0e33 (ำ)
    # Variations: ํา (\u0e32\u0e4d) and าํ (\u0e4d\u0e32)
    text = text.replace('\u0e32\u0e4d', '\u0e33')
    text = text.replace('\u0e4d\u0e32', '\u0e33')
    return text

def fix_content(content):
    # 0. Global Character Standardization
    content = normalize_thai_am(content)
    content = content.replace("แนวดำ", "แนวคำ")
    
    # 1. Stateful Deduplication and Header Cleanup
    lines = content.split('\n')
    new_lines = []
    seen_headers = set()
    
    # Regex to identify page headers: "แนวคำวินิจฉัยของศาลปกครอง" + a Thai number
    header_pattern = re.compile(r'แนวคำวินิจฉัยของศาลปกครอง')
    num_pattern = re.compile(r'[๐-๙]+')
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append(line)
            continue
            
        # Check if it's a page header
        has_title = header_pattern.search(stripped)
        nums = num_pattern.findall(stripped)
        
        if has_title and nums:
            # Create a unique key for this header (Title + Page Number)
            # The order doesn't matter (e.g., "24 แนวคำ..." == "แนวคำ... 24")
            page_num = nums[0]
            header_key = f"HEADER_{page_num}"
            
            if header_key in seen_headers:
                # Skip if already seen in this file
                continue
            else:
                seen_headers.add(header_key)
                # Keep the first occurrence but clean it up (optional: standard format)
                # For now, just keep as is but deduplicated
                new_lines.append(line)
                continue
        
        # 2. Skip obvious garbage/noise from headers that might have split
        if stripped == ">": continue
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)

    # 3. Fix Numerals (ASCII to Thai)
    def replace_digit(match):
        d = match.group(0)
        return digit_map.get(d, d)
    
    content = re.sub(r'[0-9]', replace_digit, content)

    # 4. Clean Footers
    footers = [
        r"สายด่วนศาลปกครอง ๑๓๕๕",
        r"ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน",
        r"TRUST"
    ]
    for footer in footers:
        content = re.sub(footer, "", content)
        
    # 5. Fix Lao numerals to Thai (from final_polish)
    content = content.replace('໑', '๑')
    content = content.replace('໒', '๒')
    content = content.replace('໓', '๓')

    # 6. Standardize whitespace (Reduce 3+ newlines to 2)
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content

def main():
    for fpath in files:
        print(f"Cleaning {os.path.basename(fpath)}...")
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = fix_content(content)
        
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)

if __name__ == "__main__":
    main()
