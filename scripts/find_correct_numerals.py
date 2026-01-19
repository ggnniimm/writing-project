import re
import difflib

def normalize(s):
    return re.sub(r'\s+', '', s)

# Load MD lines
md_lines = {
    186: "หมู่ที่ 5 บ้านหาดรั่ว",
    188: "อ่างเก็บน้ำห้วยทรายขาวหมู่ที่ 5",
    378: "ข้อ 5 อาคารสิ่งปลูกสร้าง",
    606: "ผิวจราจร 5 ช่อง",
    633: "ร้อยละ 7.5 ต่อปี"
}

# Load PDF text
with open('part_37_vol8.txt', 'r', encoding='utf-8') as f:
    pdf_content = f.read()

# Split PDF by lines (or phrases) for matching
pdf_lines = pdf_content.splitlines()

print("--- Searching for Matches ---")

for line_num, target in md_lines.items():
    print(f"\nTarget (Line {line_num}): {target}")
    best_match = None
    best_ratio = 0
    
    # Pre-clean target removing the number to find the text context
    # actually, keep the number, but look for Thai equivalent
    # "หมู่ที่ 5" -> match against "หมู่ที่ ๕"
    
    target_clean = normalize(target).replace('5', '.*').replace('7.5', '.*')
    
    for pdf_line in pdf_lines:
        cleaning_pdf = normalize(pdf_line)
        # Check if contains the text (ignoring the specific number)
        # Simple fuzzy search
        ratio = difflib.SequenceMatcher(None, normalize(target), cleaning_pdf).ratio()
        
        # If the PDF line contains the Thai equivalent context
        if ratio > 0.4: # Low threshold, then inspect
             # Check if it has Thai numerals
             if re.search(r'[๕-๙]', pdf_line):
                 if ratio > best_ratio:
                     best_ratio = ratio
                     best_match = pdf_line

    if best_match:
        print(f"✅ Found Candidate in PDF: {best_match.strip()}")
    else:
        print("❌ No good match found.")

print("\n--- Direct Context Search ---")
# Try searching for specific keywords around the number
keywords = {
    "หมู่ที่": r"หมู่\s*ที่\s*([๕-๙5-9])",
    "ข้อ": r"ข้อ\s*([๕-๙5-9])",
    "ร้อยละ": r"ร้อย\s*ละ\s*([๗-๙7-9])"
}

normalized_pdf = normalize(pdf_content)

for kw, pattern in keywords.items():
    match = re.search(pattern, normalized_pdf)
    if match:
        print(f"Keyword '{kw}': Found '{match.group(0)}' -> Numeral: {match.group(1)}")
    else:
        print(f"Keyword '{kw}': Not found with simple regex")
