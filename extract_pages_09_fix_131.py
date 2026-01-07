import re
from pypdf import PdfReader, PdfWriter

def main():
    pdf_path = 'etc/split_vol07/part_09.pdf'
    output_pdf_path = 'etc/split_vol07/extract_09_page131_133.pdf'
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    # We want pages 131, 132, 133.
    # Page 131 index?
    # Based on previous run:
    # Page 132 was index 6.
    # So Page 131 is likely index 5.
    
    # Let's verify with text search.
    
    pages_to_extract = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if "๑๓๑" in text and "แนว" in text:
            print(f"Index {i}: Found Page 131")
            pages_to_extract.append(i)
        elif "๑๓๒" in text and "แนว" in text:
            print(f"Index {i}: Found Page 132")
            pages_to_extract.append(i)
        elif "๑๓๓" in text and "แนว" in text:
            print(f"Index {i}: Found Page 133")
            pages_to_extract.append(i)
            
    # Add unique sorted pages
    pages_to_extract = sorted(list(set(pages_to_extract)))
    
    if not pages_to_extract:
         print("❌ No pages found.")
         return

    print(f"Extracting indices: {pages_to_extract}")
    for i in pages_to_extract:
        writer.add_page(reader.pages[i])
        
    with open(output_pdf_path, 'wb') as f:
        writer.write(f)
    print(f"✅ Created {output_pdf_path}")

if __name__ == "__main__":
    main()
