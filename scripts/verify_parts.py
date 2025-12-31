
import os
import re
import subprocess
import json

def extract_text_from_pdf(pdf_path, output_txt_path):
    try:
        subprocess.run(["pdftotext", "-layout", pdf_path, output_txt_path], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to extract text from {pdf_path}")
        return False

def normalize_thai_digits(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    trans = str.maketrans(thai_digits, arabic_digits)
    return text.translate(trans)

def check_numerals(md_path, txt_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    # Normalize for comparison
    md_norm = normalize_thai_digits(md_content)
    txt_norm = normalize_thai_digits(txt_content)

    discrepancies = []

    # Check for case citations (Year mismatches)
    # Pattern: CaseType. Number/Year e.g., อ. 123/2564
    # We look for years in the TXT that differ in MD for the same case number?
    # Or just gather all citations and compare sets.
    
    citation_pattern = re.compile(r"(?:อ\.|อผ\.|อร\.)\s*[\d,]+/(\d{4})")
    
    txt_citations = citation_pattern.findall(txt_norm)
    md_citations = citation_pattern.findall(md_norm)

    # Simplified check: Just report years found in TXT but not in MD (might indicate typo in MD)
    # But context matters.
    # Better: Scan specific years known to be problematic (2564 vs 2568)
    
    # Check for 2564 in MD where TXT has 2568 (common OCR error due to shape)
    if "2564" in md_norm and "2568" in txt_norm:
         # Rough check
         pass

    return discrepancies

def main():
    base_dir = "etc/split_v14_2569_40"
    report = {}

    for i in range(23, 40):
        part_name = f"part_{i:02d}"
        pdf_path = os.path.join(base_dir, f"{part_name}.pdf")
        md_path = os.path.join(base_dir, f"{part_name}.md")
        txt_path = os.path.join(base_dir, f"{part_name}_extracted.txt")

        if not os.path.exists(md_path):
            print(f"⚠️ {part_name}.md not found (generation incomplete?). Skipping.")
            continue

        print(f"🔍 Verifying {part_name}...")
        
        # 1. Extract Text
        if not os.path.exists(txt_path):
            extract_text_from_pdf(pdf_path, txt_path)

        # 2. Heuristic Checks
        # Specific check for 2564 vs 2568
        with open(md_path, 'r', encoding='utf-8') as f:
             md_content = f.read()
        
        matches_2564 = re.findall(r"(?:อ\.|อผ\.|อร\.)\s*[\d,]+/๒๕๖๔", md_content)
        if matches_2564:
             print(f"   ⚠️ Found potential year 2564 errors in {part_name}: {matches_2564}")
             report[part_name] = matches_2564

    print("\n--- Report ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
