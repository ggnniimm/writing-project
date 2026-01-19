
import re
import sys

def get_page_numbers(filename):
    pages = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Match 3-4 digit Thai or Arabic number at start
                m = re.match(r'^([๐-๙]{3,4}|[0-9]{3,4})', line)
                if m:
                    pages.append(m.group(1))
    except FileNotFoundError:
        print(f"File not found: {filename}")
    return pages

md_file = 'etc/Academic_310717_154727-2_parts/part_37.md'
pdf_txt = 'part_37_new_pdf.txt'

md_pages = get_page_numbers(md_file)
pdf_pages = get_page_numbers(pdf_txt)

print(f"MD Pages ({len(md_pages)}): {md_pages}")
print(f"PDF Pages ({len(pdf_pages)}): {pdf_pages}")
