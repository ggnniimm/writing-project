import re
import sys
from collections import Counter

def extract_thai_numerals(text):
    # Match Thai numerals with optional commas or periods for decimals/thousands
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def compare(md_path, txt_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    pattern = r'(?<=[\u0E00-\u0E7F])[ \t]+(?=[\u0E00-\u0E7F])'
    md_text = re.sub(pattern, '', md_text)
    md_nums = extract_thai_numerals(md_text)
    
    # Debug specific numbers
    for i, n in enumerate(md_nums):
        if n in ['๒๕๖๓๗', '๓๒๓๗']:
            print(f"DEBUG: Found {n} at index {i} (Approx pos)")

    
    with open(txt_path, 'r', encoding='utf-8') as f:
        ref_text = f.read()
    
    ref_text = re.sub(pattern, '', ref_text)
    ref_nums = extract_thai_numerals(ref_text)
    
    print(f"MD Thai Numerals count: {len(md_nums)}")
    print(f"Ref TXT Thai Numerals count: {len(ref_nums)}")
    
    # Simple frequency count
    md_counts = Counter(md_nums)
    ref_counts = Counter(ref_nums)
    
    all_nums = set(md_nums) | set(ref_nums)
    discrepancies = []
    for num in sorted(all_nums):
        if md_counts[num] != ref_counts[num]:
            discrepancies.append((num, md_counts[num], ref_counts[num]))
    
    if discrepancies:
        print("\nDiscrepancies found (Num, MD count, Ref TXT count):")
        for d in discrepancies[:50]: # Show first 50
            print(f"{d[0]}: MD={d[1]}, Ref={d[2]}")
    else:
        print("\nNo frequency discrepancies found for detected patterns.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_numerals_txt.py <md_path> <txt_path>")
        sys.exit(1)
    md_path = sys.argv[1]
    txt_path = sys.argv[2]
    compare(md_path, txt_path)
