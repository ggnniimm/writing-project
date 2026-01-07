import re
from pypdf import PdfReader, PdfWriter

def main():
    pdf_path = 'etc/split_vol07/part_09.pdf'
    output_pdf_path = 'etc/split_vol07/extract_09_gap.pdf'
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    pages_found = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        
        # Look for Page 132 and 133
        if "๑๓๒" in text and "แนว" in text:
            print(f"Found Page 132 at index {i}")
            writer.add_page(page)
            pages_found.append(i)
            
        elif "๑๓๓" in text and "แนว" in text:
            print(f"Found Page 133 at index {i}")
            writer.add_page(page)
            pages_found.append(i)
            
    if pages_found:
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)
        print(f"✅ Created {output_pdf_path} with {len(pages_found)} pages.")
    else:
        print("❌ Could not find pages 132/133.")

if __name__ == "__main__":
    main()
