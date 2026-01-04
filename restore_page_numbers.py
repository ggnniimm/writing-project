import re
import sys
import difflib
import os

def normalize(s):
    # Decompose SARA AM (U+0E33) to NIKHAHIT (U+0E4D) + SARA AA (U+0E32)
    s = s.replace('\u0e33', '\u0e4d\u0e32')
    # Remove all whitespace
    s = re.sub(r'\s+', '', s)
    return s

def main():
    if len(sys.argv) < 2:
        print("Usage: python restore_page_numbers.py <path_to_markdown_part>")
        sys.exit(1)

    md_path = sys.argv[1]
    
    # Derive the corresponding PDF file path
    # MD: .../parts/Academic_281020_102051_part_XX.md
    # PDF: .../parts/Academic_281020_102051_part_XX.pdf
    if not md_path.endswith('.md'):
         print("Error: Input file must be a .md file")
         sys.exit(1)
         
    pdf_path = md_path[:-3] + ".pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file {pdf_path} not found.")
        # Fallback: check current directory or raw_pdfs if needed, but strict pairing is safer
        sys.exit(1)

    print(f"Processing: {md_path}")
    print(f"Using source PDF: {pdf_path}")
    
    # Run pdftotext
    import subprocess
    try:
        # -layout preserves visual layout, but can cause spacing issues. 
        # For header extraction (single line), it's usually fine. 
        # -enc UTF-8 is default usually.
        cmd = ['pdftotext', '-layout', pdf_path, '-']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running pdftotext: {result.stderr}")
            sys.exit(1)
        full_text = result.stdout
    except Exception as e:
        print(f"Error executing pdftotext: {e}")
        sys.exit(1)

    # Parse headers from full_text
    # usage of \f (form feed) as page separator
    # Note: pdftotext output ends with \f usually
    pages = full_text.split('\f')
    
    headers = []
    
    for page_idx, page_text in enumerate(pages):
        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        if not lines: continue
        
        # Primary Heuristic: The first non-empty line of a page is the header.
        # This is very likely for this document type (Ruling).
        header_candidate = lines[0]
        
        # Filter: Header must usually contain "หน้า" or "เล่ม" or similar?
        # Or just accept it. If it matches text in MD, it's fine.
        # But we only want to insert it if it's MISSING in MD.
        
        # Anchor: The next significant text.
        anchor_candidate = ""
        if len(lines) > 1:
            anchor_candidate = lines[1]
            if len(lines) > 2 and len(anchor_candidate) < 10: 
                 # If anchor is very short, append next line too for better uniqueness
                 anchor_candidate += " " + lines[2]
        
        if header_candidate and anchor_candidate:
             headers.append((header_candidate, anchor_candidate))

    print(f"Total extracted pages/headers: {len(headers)}")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_lines = f.readlines()
    
    # Pre-compute normalized MD lines for faster lookups
    md_lines_norm = [normalize(line) for line in md_lines]
    
    new_md_lines = []
    current_md_idx = 0
    headers_inserted = 0
    
    # ... logic continues as before ...
    # We might need to adjust the fuzzy matching if pdftotext output is messy.
    
    for header, anchor in headers:
        # We need to insert 'header' BEFORE 'anchor' in MD.
        
        # 1. Normalize anchor
        anchor_norm = normalize(anchor)
        
        # 2. Search in MD
        found_idx = -1
        
        # Heuristic: Search from current position forward
        # For Parts 01-12, the content should be somewhat sequential, but since we are processing one part file 
        # against the WHOLE valid extracted text, we must be careful not to match anchors from other parts excessively early 
        # or miss meaningful matches.
        # However, since we are doing this per file, we should only look for anchors that actually exist in this file.
        # But wait, 'headers' contains ALL headers from the PDF.
        # We only want to insert headers that belong to THIS part.
        # So we should only advance current_md_idx if we actually found a match in THIS file.
        
        # We will search the ENTIRE remaining file for the anchor.
        # But to avoid false positives (short anchors matching elsewhere), we prefer matches closer to current_md_idx?
        # Actually, let's keep the scan limit but maybe make it larger if needed, or just scan to end of file if file is small.
        # Parts are ~20 pages, so ~600-1000 lines.
        
        scan_limit = len(md_lines) # Search entire remaining file
        
        # Try finding exact match of normalized string first
        for k in range(current_md_idx, scan_limit):
             if anchor_norm in md_lines_norm[k]:
                 found_idx = k
                 break
        
        # If not found, try fuzzy text match (using difflib) very loosely
        if found_idx == -1:
            for k in range(current_md_idx, scan_limit):
                # Check similarity
                ratio = difflib.SequenceMatcher(None, anchor_norm, md_lines_norm[k]).ratio()
                if ratio > 0.8: # 80% similarity
                    found_idx = k
                    break
                    
        # If found
        if found_idx != -1:
            # Append everything before found_idx
            new_md_lines.extend(md_lines[current_md_idx:found_idx])
            
            # Check if this header is already there
            if found_idx > 0 and normalize(md_lines[found_idx-1]) == normalize(header):
                pass
            
            # Additional Check: Is the header RELEVANT to the current file?
            # If we found matches, it implies it's relevant.
            # BUT, if we skipped a huge chunk of text (e.g. we matched an anchor from page 500 when we are at page 1),
            # that's a problem.
            # So, maybe we should enforce that 'found_idx' is not TOO far ahead of 'current_md_idx' 
            # UNLESS 'headers_inserted' is 0 (searching for first page of specific part).
            
            # Let's trust the uniqueness of anchors for now, but usually they are unique enough.
            
            else:
                 new_md_lines.append("\n" + header + "\n")
                 headers_inserted += 1
            
            current_md_idx = found_idx
        else:
            # If anchor not found in this file, it might simply be that this header belongs to another part.
            # We just ignore it and move to next header in global list.
            pass
            
    # Append rest of file
    new_md_lines.extend(md_lines[current_md_idx:])
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.writelines(new_md_lines)
        
    print(f"Done. Inserted {headers_inserted} headers.")

if __name__ == '__main__':
    main()
