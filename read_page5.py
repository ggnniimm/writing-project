import pdfplumber

pdf_path = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_57.pdf"

print(f"Reading Page 5 of {pdf_path}...")

with pdfplumber.open(pdf_path) as pdf:
    if len(pdf.pages) >= 5:
        page = pdf.pages[4] # Index 4 is Page 5
        text = page.extract_text()
        print(text)
