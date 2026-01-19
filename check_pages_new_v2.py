
import re
import sys

def get_page_numbers(filename):
    pages = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                
                # Format 1: Number at start (Left Page) e.g., "๗๑๒ แนวคำวินิจฉัย..."
                # Format 2: Number at end (Right Page) e.g., "...ของศาลปกครอง ๗๑๑"
                
                # Check for specific header-like lines only to avoid false positives
                if 'แนวคำวินิจฉัยของศาลปกครอง' in line or 'ศาลปกครองสูงสุด' in line:
                     # Match number at start
                    m_start = re.match(r'^([๐-๙]{3,4}|[0-9]{3,4})', line)
                    if m_start:
                        pages.append(m_start.group(1))
                        continue
                    
                    # Match number at end
                    m_end = re.search(r'([๐-๙]{3,4}|[0-9]{3,4})$', line)
                    if m_end:
                        pages.append(m_end.group(1))
    except FileNotFoundError:
        print(f"File not found: {filename}")
    return pages

md_file = 'etc/Academic_310717_154727-2_parts/part_37.md'
pdf_txt = 'part_37_new_pdf.txt'

md_pages = get_page_numbers(md_file)
pdf_pages = get_page_numbers(pdf_txt)

print(f"MD Pages ({len(md_pages)}): {md_pages}")
print(f"PDF Pages ({len(pdf_pages)}): {pdf_pages}")
