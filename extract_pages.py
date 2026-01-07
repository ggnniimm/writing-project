import re
from pypdf import PdfReader, PdfWriter

def main():
    pdf_path = 'etc/split_vol07/part_12.pdf'
    output_pdf_path = 'etc/split_vol07/extract_204_205.pdf'
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    pages_found = []
    
    print(f"Total pages: {len(reader.pages)}")
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        # Look for the specific headers
        # "แนวคาวินิจฉัยของศาลปกครอง ๒๐๔" or similar
        # Note: extraction might be messy, so look for "204" and "Sakol" or "Guideline" components if needed, or just strict Thai.
        
        # Searching for "๒๐๔" near "แนว...วินิจฉัย"
        if "๒๐๔" in text and "วินิจฉัย" in text:
            print(f"Found Page 204 at index {i}")
            pages_found.append(i)
            writer.add_page(page)
            
        if "๒๐๕" in text and "วินิจฉัย" in text:
            print(f"Found Page 205 at index {i}")
            pages_found.append(i)
            writer.add_page(page)
            
    if pages_found:
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)
        print(f"✅ Created {output_pdf_path} with {len(pages_found)} pages.")
    else:
        print("❌ Could not find pages 204/205.")

if __name__ == "__main__":
    main()
