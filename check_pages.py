
import re
import sys

def get_page_numbers(filename):
    pages = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Match 3-4 digit Thai or Arabic number at start
            m = re.match(r'^([๐-๙]{3,4}|[0-9]{3,4})', line)
            if m:
                pages.append(m.group(1))
    return pages

md_pages = get_page_numbers('etc/Academic_230317_084750-2_parts/part_37.md')
pdf_pages = get_page_numbers('part_37_pdf.txt')

print(f"MD Pages ({len(md_pages)}): {md_pages}")
print(f"PDF Pages ({len(pdf_pages)}): {pdf_pages}")
