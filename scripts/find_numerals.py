import re

def normalize(text):
    return re.sub(r'\s+', '', text)

def find_context(pdf_path, search_phrases):
    with open(pdf_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Normalize heavily for search but print original context
    # This is tricky because we want the numeral.
    # Let's just Regex search with fuzzy spacing 
    
    results = {}
    for phrase in search_phrases:
        # Create regex: "ห\s*ม\s*ู\s*่\s*ท\s*ี\s*่" etc
        # Simplify: Just search for key parts
        if "หมู่ที่" in phrase:
            # Look for "หมู่ที่" followed by number
            # content might have "ห มู ่ ท ี ่"
             pattern = r'ห\s*ม\s*ู\s*่\s*ท\s*ี\s*่\s*([๕-๙5-9])'
        elif "ข้อ" in phrase:
             pattern = r'ข\s*้\s*อ\s*([๕-๙5-9])'
        elif "ร้อยละ" in phrase:
             pattern = r'ร\s*้\s*อ\s*ย\s*ล\s*ะ\s*([๗-๙7-9])\s*\.?\s*([๐-๙0-9]*)' 
        
        matches = re.finditer(pattern, content)
        found = []
        for m in matches:
            found.append(m.group(0))
        results[phrase] = found

    return results

print("--- Searching in part_37.txt ---")
# 'part_37.txt' seems to be the content dump.
# Note: User provided 'part_37.txt' length 145276.
# Let's try searching there.

with open('etc/Academic_310717_154727-2_parts/part_37.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

keywords = [
    "หมู่ที่", 
    "ข้อ",
    "ร้อยละ",
    "ผิวจราจร"
]

for kw in keywords:
    print(f"\nScanning for '{kw}' context:")
    # print context around keywords
    # Brute force scan
    indices = [m.start() for m in re.finditer(kw, text)]
    if not indices:
         # Try spaced version
         spaced = "".join([c + r"\s*" for c in kw])
         indices = [m.start() for m in re.finditer(spaced, text)]
    
    for idx in indices:
        start = max(0, idx - 10)
        end = min(len(text), idx + 30)
        snippet = text[start:end].replace('\n', ' ')
        # We are looking for numbers
        if any(c in snippet for c in "56789๕๖๗๘๙"):
            print(f"MATCH: ...{snippet}...")
