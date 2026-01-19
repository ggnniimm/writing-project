from pypdf import PdfReader
import re

reader = PdfReader("etc/Academic_310717_154727-2_parts/part_37.pdf")

def print_page_context(page_num, keywords):
    print(f"\n--- Page {page_num} ---")
    page = reader.pages[page_num] # 0-indexed
    text = page.extract_text()
    
    # Simple print of lines containing keywords
    for line in text.splitlines():
        if any(k in line for k in keywords):
             print(f"FOUND: {line.strip()}")

# Map estimated locations to PDF pages (approx)
# MD starts at Page 711 (Page 1 of PDF)
# Line 186 is roughly Page 5-6 (716-717)
# Line 378 is roughly Page 9-10 (720-721)
# Line 606 is roughly Page 17 (728)
# Line 633 is roughly Page 19 (729)

# Page 6 (Index 5) for หมู่ที่
print_page_context(5, ["หมู่", "บ้านหาด"])

# Page 10 (Index 9) or 11 (Index 10) for ข้อ 5
print_page_context(10, ["ข้อ"])

# Page 17 (Index 16) or 18 (Index 17) for ผิวจราจร
print_page_context(17, ["ผิวจราจร"])

# Page 19 (Index 18) for ร้อยละ
print_page_context(18, ["ร้อยละ"])
print_page_context(19, ["ร้อยละ"])
