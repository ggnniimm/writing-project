import os
import re

rulings_dir = "references/rulings_court"
pdfs_dir = "references/raw_pdfs"

def normalize_thai_digits(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    translation_table = str.maketrans(thai_digits, arabic_digits)
    return text.translate(translation_table)

def scan_and_propose():
    print(f"{'CURRENT FILENAME':<40} | {'PROPOSED FILENAME':<40} | {'STATUS'}")
    print("-" * 100)
    
    for filename in sorted(os.listdir(rulings_dir)):
        if not filename.endswith(".md"):
            continue
            
        filepath = os.path.join(rulings_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(4000) # Read first 4000 chars
            
        normalized_content = normalize_thai_digits(content)
        
        # Look for Red Case Number
        # Pattern: คดีหมายเลขแดงที่ (optional prefix) NUMBER / YEAR
        match = re.search(r"คดีหมายเลขแดงที่\s*(?:(อ\.|อ|1\.)\s*)?([\d.,]+)\s*/\s*(\d+)", normalized_content)
        
        if match:
            prefix_raw = match.group(1)
            number_raw = match.group(2)
            year = match.group(3)
            
            # Logic: If explicitly "อ." OR starts with "1." (heuristic), use "o_"
            is_or_case = False
            
            if prefix_raw and ("อ" in prefix_raw or "1." in prefix_raw):
                is_or_case = True
            elif number_raw.startswith("1."): # Heuristic for 1.xxxx
                is_or_case = True
                number_raw = number_raw.replace("1.", "", 1)
            
            clean_number = re.sub(r"[^\d]", "", number_raw)
            
            new_prefix = "o_" if is_or_case else ""
            # If the original file already has "o_", keep it? Or strictly follow content?
            # Let's trust content > filename, but preserve existing "o_" if we can't find it in content?
            # actually if we find match, we use match.
            
            # For this specific task, User asked to "Add o". So we prefer adding it.
            # If we detect it's an "Or" case (Red Case starts with Or or 1.), we add o_.
            
            new_filename = f"ref_sac_{new_prefix}{clean_number}_{year}.md"
            
            if new_filename != filename:
                # Check if PDF exists
                pdf_old_name = filename.replace(".md", ".pdf")
                pdf_new_name = new_filename.replace(".md", ".pdf")
                
                pdf_status = "PDF Found" if os.path.exists(os.path.join(pdfs_dir, pdf_old_name)) else "No PDF"
                
                print(f"{filename:<40} | {new_filename:<40} | Rename ({pdf_status})")
            else:
                print(f"{filename:<40} | {new_filename:<40} | Keep")
        else:
            print(f"{filename:<40} | {'???':<40} | No Red Case found")

if __name__ == "__main__":
    scan_and_propose()
