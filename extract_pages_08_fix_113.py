
import re
from pypdf import PdfReader, PdfWriter

def main():
    pdf_path = 'etc/split_vol07/part_08.pdf'
    output_pdf_path = 'etc/split_vol07/extract_08_page113.pdf'
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    found = False
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        # Search for Page 113 signature
        # "แนวคาวินิจฉัยของศาลปกครอง ๑๑๓" (note: might be encoded differently)
        # Using "๑๑๓" and "แนว" as strong indicators.
        if "๑๑๓" in text and "แนว" in text:
             print(f"Index {i}: Found Page 113")
             writer.add_page(page)
             found = True
             break # Expecting only one page
    
    if found:
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)
        print(f"Successfully extracted Page 113 to {output_pdf_path}")
    else:
        print("Error: Page 113 not found in PDF")

if __name__ == "__main__":
    main()
