
import re

def find_page_number(text_file, search_string):
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return "File not found"
    
    # Split by form feed (page break)
    pages = content.split('\f')
    
    for i, page_text in enumerate(pages):
        # normalize spaces
        clean_text = re.sub(r'\s+', ' ', page_text)
        search_clean = re.sub(r'\s+', ' ', search_string)
        
        if search_clean in clean_text:
            return i + 1  # 1-based page number
            
    return None

source_file = "master_text.txt"

# Part 25 Start
# Text: ผู้ถูกฟ้องคดีที่ ๒ ในฐานะรัฐมนตรีผู้รักษาการตามพระราชบัญญัติ
p25_start = find_page_number(source_file, "ผู้ถูกฟ้องคดีที่ ๒ ในฐานะรัฐมนตรีผู้รักษาการตามพระราชบัญญัติ")
print(f"Part 25 starts around page: {p25_start}")

# Part 26 Start
# Text: ๑๓๐๕ แห่งประมวลกฎหมายแพ่งและพาณิชย์
# Note: PDF might have superscripts like 1305^2
p26_start = find_page_number(source_file, "๑๓๐๕") 
# Try to be more specific if possible, but 1305 is fairly specific in this context with P.P.P.
# Let's try searching for the header "แนวคำวินิจฉัยของศาลปกครอง ๔๗๓" (Part 26 Line 1)
# Note: PDF header might be "แนวคาวินิจฉัยของศาลปกครอง ๔๗๓"
p26_header = find_page_number(source_file, "แนวคาวินิจฉัยของศาลปกครอง ๔๗๓")
print(f"Part 26 starts (header check) around page: {p26_header}")
