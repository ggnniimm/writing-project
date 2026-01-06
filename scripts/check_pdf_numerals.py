import re
from pypdf import PdfReader

pdf_path = "etc/split_vol07/part_01.pdf"
reader = PdfReader(pdf_path)

print("--- Extracting first 3 pages relative to 'เล่มที่' ---")

# Search in first few pages where Preface usually is
for i in range(min(5, len(reader.pages))):
    page = reader.pages[i]
    text = page.extract_text()
    if text:
        # Look for the context "เล่มที่"
        lines = text.split('\n')
        for line in lines:
            if "เล่มที่" in line:
                print(f"Page {i+1}: {line}")
