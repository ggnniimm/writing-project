
import fitz  # PyMuPDF
import sys
import re

def check_numerals(pdf_path):
    doc = fitz.open(pdf_path)
    arabic_numerals = set()
    thai_numerals = set()
    
    print(f"Checking {pdf_path}...")
    
    hits = []

    for page_num, page in enumerate(doc):
        text = page.get_text()
        # Search for specific context strings found in markdown to verify the number in PDF
        
        # Line 85: "พวกรวม 5 คน"
        contexts = [
            ("พวกรวม", "คน"), # Expect 5 or ๕ in between
            ("กำหนด", "เดือน"), # Line 246: "กำหนด 5 เดือน"
            ("พัสดุระดับ", "ที่") # Line 285: "พัสดุระดับ 5 ที่"
        ]
        
        for prefix, suffix in contexts:
            # simple regex to find number between prefix and suffix
            # allowing for some spacing or newline
            pattern = f"{prefix}\s*([0-9]|[\u0e50-\u0e59])\s*{suffix}"
            matches = re.findall(pattern, text)
            for m in matches:
                hits.append(f"Page {page_num+1}: Found '{m}' between '{prefix}' and '{suffix}'")

    for hit in hits:
        print(hit)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_numerals(sys.argv[1])
    else:
        print("Usage: python check_pdf_numerals.py <pdf_path>")
