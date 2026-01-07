
import re

def find_page_numbers(text_file, start_marker, end_marker):
    with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    pages = content.split('\f')
    
    start_page = -1
    end_page = -1
    

    # Create regex pattern that allows optional spaces between chars
    def make_fuzzy_regex(text):
        # Escape special chars first
        escaped = re.escape(text)
        # Allow spaces between any characters
        # This is expensive, so maybe just replace spaces in text with \s*
        # Better: remove spaces from both source and target for comparison
        return text.replace(" ", "")

    print(f"Searching for Start (fuzzy)...")
    
    clean_start_marker = marker_start.replace(" ", "")
    clean_end_marker = end_marker.replace(" ", "")

    for i, page_text in enumerate(pages):
        # Remove all whitespace from page text for comparison
        page_nospace = re.sub(r'\s+', '', page_text)
        
        if start_page == -1 and clean_start_marker in page_nospace:
            print(f"Found Start on Page {i+1}")
            # print snippet
            print(f"Snippet: {page_text[:100]}...")
            start_page = i + 1
        
        if clean_end_marker in page_nospace:
            print(f"Found End on Page {i+1}")
            end_page = i + 1

            
    return start_page, end_page

# Markers from Part 25 start and Part 26 start
marker_start = "ผู้ถูกฟ้องคดีที่ ๒ ในฐานะรัฐมนตรีผู้รักษาการตามพระราชบัญญัติประกันวินาศภัย"
# Part 26 starts with "๑๓๐๕" but let's use a sentence
marker_end = "๑๓๐๕" 
marker_end_context = "แห่งประมวลกฎหมายแพ่งและพาณิชย์"

# Combine for end marker? No, 1305 might be separated.
# Let's search for "แนวคำวินิจฉัยของศาลปกครอง ๔๗๓" (Part 26 Header)
# Be careful of spelling "คาวินิจฉัย" in PDF
header_marker = "แนวคาวินิจฉัยของศาลปกครอง ๔๗๓"

find_page_numbers("master.txt", marker_start, header_marker)
