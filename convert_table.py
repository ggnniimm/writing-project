
import re
import sys

def convert_to_table(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    
    # Header for the file
    # Only keep the specific headers that appear at the top, but we will insert them as found.
    
    current_table = []
    is_in_table = False
    
    # Helper to flush table
    def flush_table(out_list, table_rows):
        if not table_rows:
            return
        out_list.append("\n| คำพิพากษา/คำสั่งศาลปกครองสูงสุดที่ | พ.ศ. ๒๕๖๗/๒๕๖๘ | หน้า |\n")
        out_list.append("| :--- | :--- | :--- |\n")
        out_list.extend(table_rows)
        out_list.append("\n")
        table_rows.clear()

    # Regex for case lines: "  CaseNo/Year  Page"
    # Examples:
    # ๓๖/๒๕๖๗ 137
    # ๑๙๒/๒๕๖๗ 198
    # ๘๐๕/๒๕๖๗ 57
    # ๘๙๗/๒๕๖๗ 132, 156, 166
    # ๙๑๒-๙๑๓/๒๕๖๗ 100
    # อร. ๔๓/๒๕๖๘ (ประชุมใหญ่) 451
    # Also sometimes leading spaces
    
    # Regex explanation:
    # Start: Optional whitespace
    # Part 1 Case: Can handle "อร. 43/2568" or "36/2567" or "912-913/2567"
    # Part 2 Page: Last token(s) composed of digits and commas
    
    table_rows = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Detect if this is a "footer" or "header" line causing interruption
        # If it's a pagination line or URL, we output it as raw text
        if "bit.ly" in stripped or "สายด่วนศาลปกครอง" in stripped or "ระบบงานคดีปกครอง" in stripped or "แนวคำวินิจฉัย" in stripped:
             if table_rows:
                 flush_table(output_lines, table_rows)
             output_lines.append(f"{line}") # Keep original indentation/spacing
             continue
        
        # Check if line looks like a table row content
        # It must end with page numbers (digits, maybe commas)
        # And must have a slash / for year
        
        # Regex for valid row:
        # starts with optional text, has /256[78], ends with digits/commas
        
        match = re.search(r'^(.*?)(/๒๕๖[๗๘])(.*?)\s+([0-9, ]+)$', stripped)
        
        # Alternative regex for cases without prefix text (just numbers)
        # 36/2567 137
        
        # Let's try to split by spaces from right side to get page numbers
        # But page numbers can have spaces: "132, 156, 166"
        
        # Heuristic: split line. If last parts are all numbers/commas, valid page.
        # The '/' must exist in the first part.
        
        if '/' not in stripped:
            # Not a table row
            if table_rows:
                 flush_table(output_lines, table_rows)
            output_lines.append(f"{line}")
            continue

        # Attempt to parse
        # Find the last occurrence of a gap between "Case/Year" and "Page"
        # Usually there is a large gap or at least one space.
        
        # If line contains "ประชุมใหญ่", that is part of the Case column usually.
        
        parts = stripped.rsplit(None, 1) 
        # But this only splits the very last token. "132, 156, 166" would split only "166".
        # We need to handle multiple page numbers.
        
        # Regex to find the page part at end of line
        # Page part: digits, commas, spaces.
        # Must be preceded by some whitespace.
        page_pattern = r'\s+([0-9, ]+)$'
        pm = re.search(page_pattern, stripped)
        
        if pm:
            page_text = pm.group(1).strip()
            # Verify page_text only chars allowed: 0-9 , space
            if not re.match(r'^[0-9, ]+$', page_text):
                 # Maybe not a page number?
                 # If fail, treat as text
                 if table_rows:
                     flush_table(output_lines, table_rows)
                 output_lines.append(f"{line}")
                 continue

            case_text = stripped[:pm.start()].strip()
            
            # Convert page_text arabic to Thai numerals for consistency?
            # User wants "Gemini style". Gemini tables in part_39 used Thai numerals for pages.
            # Extracted text has Arabic for pages.
            # I should convert Arabic pages to Thai pages.
            
            thai_digits = str.maketrans("0123456789", "๐๑๒๓๔๕๖๗๘๙")
            page_thai = page_text.translate(thai_digits)
            
            # case_text might contain /2567 or /2568. 
            # We want to split Case and Year if possible?
            # The previous table had 3 columns: Case, Year, Page.
            # Or formatted as: Case (including /Year) | "" | Page?
            # In step 509: 
            # Col 1: อร. ๔๓/๒๕๖๘ (ประชุมใหญ่)
            # Col 2: (Empty?)
            # Col 3: ๔๕๑
            
            # Check step 509 content again.
            # | อร. ๔๓/๒๕๖๘ (ประชุมใหญ่) | | ๔๕๑ |
            # So Col 2 was empty? Or maybe the Year was in Col 1?
            # Header says "พ.ศ. ๒๕๖๘" in Col 2.
            # But the row leaves it empty.
            
            # Simpler: Just 2 columns? Or 3?
            # Let's start with 2: Case (full text) | Page
            # OR replicate the 3 cols.
            # If I put the full text in Col 1, and leave Col 2 empty, that matches.
            
            # row: | {case_text} | | {page_thai} |
            table_rows.append(f"| {case_text} | | {page_thai} |\n")
            
        else:
            # Fallback
            if table_rows:
                 flush_table(output_lines, table_rows)
            output_lines.append(f"{line}")
            
    # Flush remaining
    flush_table(output_lines, table_rows)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

if __name__ == "__main__":
    convert_to_table(sys.argv[1], sys.argv[2])
