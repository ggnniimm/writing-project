
import re

pdf_txt = 'part_37_pdf.txt'

with open(pdf_txt, 'r', encoding='utf-8') as f:
    text = f.read()

pages = text.split('\f')
target_page_index = -1

for i, page in enumerate(pages):
    # Check if page starts with 700 (allowing for some whitespace)
    if re.search(r'^\s*๗๐๐\s', page, re.MULTILINE):
        target_page_index = i + 1
        print(f"Found Page 700 at PDF Page Index: {target_page_index}")
        # Print first few lines to verify
        print("Page Content Start:")
        print('\n'.join(page.strip().split('\n')[:5]))
        break
    
    # Also try the other spelling of 700 in Thai numerals just in case (but regex above handles it)

if target_page_index == -1:
    print("Page 700 not found (regex check failed)")
