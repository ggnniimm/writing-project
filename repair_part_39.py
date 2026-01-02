
import re

def parse_extracted_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    tables = []
    current_table = []
    
    # Heuristic to detect table start/end or just process all lines
    # The file has visual tables.
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Regex for Order Line
        # Matches: "36/2567   137" or "อ. 43/2568 (ประชุมใหญ่)   451"
        # We need to capture the Order No and Page No.
        
        # Pattern:
        # (Prefix)? (Number/Year) (Note)? (Whitespace) (PageNumbers)
        
        # Example: "๑๕๔/๒๕๖๘ (ประชุมใหญ่)                               219"
        # Example: "๕๐๑/๒๕๖๗                                                 110"
        # Example: "๙๑๒-๙๑๓/๒๕๖๗                                    100"
        # Example: "๑๐๙๑/๒๕๖๗                                     49, 58, 62, 161"
        
        # We look for lines that end with digits (and commas/spaces for multiple pages)
        # And contain a "/" followed by Year (๒๕๖๗ or ๒๕๖๘).
        
        match = re.search(r'^(.*?/๒๕๖[๗๘].*?)\s+([0-9, ]+|bo|mo|bon)$', line)
        if not match:
            # Try to catch cases where OCR of page number is weird, but we have extracted text which seems clean (digits)
            # The extracted text had "110", "63", "60".
            # So looking for \d+ at end should work for 99% of valid extracted lines.
            match = re.search(r'^(.*?/๒๕๖[๗๘].*?)\s+([0-9, ]+)$', line)
        
        if match:
            order_col = match.group(1).strip()
            page_col = match.group(2).strip()
            
            # Normalize Thai Numerals in Order Col (They are already Thai in extracted text)
            # Normalize Arabic Numerals in Page Col to Thai
            
            page_thai = to_thai_numerals(page_col)
            
            # Identify which year/table it belongs to?
            # We can just output a list and then manually reconstruct the blocks or 
            # try to detect the headers in the text file.
            
            tables.append(f"| {order_col} | | {page_thai} |")

    return tables

def to_thai_numerals(arabic_str):
    mapping = {
        '0': '๐', '1': '๑', '2': '๒', '3': '๓', '4': '๔',
        '5': '๕', '6': '๖', '7': '๗', '8': '๘', '9': '๙'
    }
    res = ""
    for char in arabic_str:
        res += mapping.get(char, char)
    return res

if __name__ == "__main__":
    extracted_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_v14_2569_40/part_39_extracted.txt"
    rows = parse_extracted_file(extracted_path)
    for row in rows:
        print(row)
