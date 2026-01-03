import pdfplumber

pdf_path = "etc/Academic_291121_112321_parts/Academic_291121_112321_part_02.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total Pages in PDF: {total_pages}")
        
        # User said pages 17-20. Let's extract 16-21 (0-indexed: 15-20, or 16-21? User likely uses 1-based)
        # 1-based 17 is index 16.
        # Let's extract indices 16, 17, 18, 19 (Pages 17, 18, 19, 20)
        
        pages_to_extract = [16, 17, 18, 19]
        
        for idx in pages_to_extract:
            if idx < total_pages:
                page = pdf.pages[idx]
                text = page.extract_text()
                print(f"\n--- Page {idx + 1} Text ---\n")
                print(text)
            else:
                print(f"\n--- Page {idx + 1} Text ---\n(Page index out of range)")

except Exception as e:
    print(f"Error: {e}")
