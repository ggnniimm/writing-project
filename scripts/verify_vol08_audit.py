import os
import re
import glob

# Constants
BASE_DIR = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08"
START_PART = 5
END_PART = 55

def check_file_pair(part_num):
    base_name = f"part_{part_num:02d}"
    pdf_path = os.path.join(BASE_DIR, f"{base_name}.pdf")
    md_path = os.path.join(BASE_DIR, f"{base_name}.md")
    
    if not os.path.exists(pdf_path):
        return f"❌ Missing PDF for part {part_num}"
    if not os.path.exists(md_path):
        return f"❌ Missing MD for part {part_num}"
    
    pdf_size = os.path.getsize(pdf_path)
    md_size = os.path.getsize(md_path)
    
    if pdf_size == 0:
        return f"❌ Empty PDF for part {part_num}"
    
    ratio = md_size / pdf_size
    # Explicitly flag if ratio is suspiciously low (Part 04 was ~13% when broken, ~22% when fixed)
    if ratio < 0.15: 
        return f"⚠️  Low Content Ratio ({ratio:.1%}) for part {part_num} (PDF: {pdf_size // 1024}KB, MD: {md_size // 1024}KB)"
        
    return None

def check_page_continuity(part_num):
    base_name = f"part_{part_num:02d}"
    md_path = os.path.join(BASE_DIR, f"{base_name}.md")
    
    if not os.path.exists(md_path):
        return []

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Regex to find page headers like "๒๘ แนวคำวินิจฉัยของศาลปกครอง" OR "แนวคำวินิจฉัยของศาลปกครอง ๒๙"
    # Capture group 1: Left number, Capture group 2: Right number
    headers = re.findall(r"(?:^([๐-๙]+)\s+แนวคำวินิจฉัย)|(?:แนวคำวินิจฉัย.*?([๐-๙]+)$)", content, re.MULTILINE)
    
    if not headers:
        return [f"⚠️  No page headers found in part {part_num}"]

    thai_numerals = "๐๑๒๓๔๕๖๗๘๙"
    arabic_numerals = "0123456789"
    trans = str.maketrans(thai_numerals, arabic_numerals)
    
    page_nums = []
    for h in headers:
        # h is a tuple (left_num, right_num). One will be empty string.
        num_str = h[0] if h[0] else h[1]
        if num_str:
            page_nums.append(int(num_str.translate(trans)))
    
    # Sort just in case, though they should be in order
    # page_nums.sort() # Don't sort, we want to check reading order continuity
    
    issues = []
    
    # Check sequences
    for i in range(len(page_nums) - 1):
        curr = page_nums[i]
        next_val = page_nums[i+1]
        
        if next_val != curr + 1:
            if next_val == curr:
                 issues.append(f"⚠️  Duplicate page {curr} in part {part_num}")
            else:
                 issues.append(f"❌ GAP: Page {curr} -> {next_val} (Missing {next_val - curr - 1} pages) in part {part_num}")

    return issues

def check_numerals(part_num):
    base_name = f"part_{part_num:02d}"
    md_path = os.path.join(BASE_DIR, f"{base_name}.md")
    
    if not os.path.exists(md_path):
        return []
        
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    issues = []
    for i, line in enumerate(lines):
        # Ignore English footers/headers or timestamps in logs if any
        if "TRUST" in line or "Information" in line:
            continue
            
        # Regex to find stray Arabic numerals [0-9]
        # Allow numbers if they are clearly part of an English reference like "v14" or "2024-..." but typically this corpus is Thai
        matches = re.findall(r'[0-9]', line)
        if matches:
             # Heuristic: Fail if we see Arabic numerals in a Thai sentence context
             if re.search(r'[ก-ฮ]', line):
                 issues.append(f"⚠️  Arabic Numeral on line {i+1}: '{line.strip()[:60]}...'")
                 if len(issues) > 3: # Cap errors
                     issues.append("... (more numeral errors)")
                     break
    return issues

def main():
    print(f"🔎 Auditing Vol 08 Parts {START_PART:02d} - {END_PART:02d}...\n")
    
    all_issues = []
    
    for i in range(START_PART, END_PART + 1):
        pair_issue = check_file_pair(i)
        if pair_issue:
            print(pair_issue)
            all_issues.append(pair_issue)
            continue # Skip deep content check if basic file check fails
            
        continuity_issues = check_page_continuity(i)
        for issue in continuity_issues:
            print(issue)
            all_issues.append(issue)
            
        numeral_issues = check_numerals(i)
        for issue in numeral_issues:
            print(f"part_{i:02d}: {issue}")
            all_issues.append(f"part_{i:02d}: {issue}")
            
    print("\n" + "="*50)
    print(f"Audit Complete. Found {len(all_issues)} issues.")
    if not all_issues:
        print("✅ No critical issues found across all checked files.")

if __name__ == "__main__":
    main()
