
import re
from pypdf import PdfReader, PdfWriter

def main():
    pdf_path = 'etc/split_vol07/part_07.pdf'
    output_pdf_path = 'etc/split_vol07/extract_07_page105.pdf'
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    found = False
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        # Search for unique header/footer signature of Page 105
        # Based on previous dump: "แนวคาวินิจฉัยของศาลปกครอง ๑๐๕"
        # Note: 'คาวินิจฉัย' might be 'คำวินิจฉัย' in PDF text depending on extraction, 
        # but '๑๐๕' at the end of a line is a good signal.
        if "๑๐๕" in text and "ศาลปกครอง" in text:
             # Double check it's not some other page with 105 in text
             # The page number usually appears at the top or bottom right.
             # Let's trust the combination of 105 and the header phrase.
             print(f"Index {i}: Found Page 105")
             writer.add_page(page)
             found = True
             break # Expecting only one page 105
    
    if found:
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)
        print(f"Successfully extracted Page 105 to {output_pdf_path}")
    else:
        print("Error: Page 105 not found in PDF")

if __name__ == "__main__":
    main()
