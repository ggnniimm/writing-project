import pdfplumber

pdf_path = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_57.pdf"

print(f"Reading Page 1 of {pdf_path}...")

with pdfplumber.open(pdf_path) as pdf:
    if len(pdf.pages) > 0:
        page = pdf.pages[0]
        text = page.extract_text()
        print(text)
