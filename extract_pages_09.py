import re
from pypdf import PdfReader, PdfWriter

def main():
    pdf_path = 'etc/split_vol07/part_09.pdf'
    output_pdf_path = 'etc/split_vol07/extract_09_missing.pdf'
    
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    
    # We suspect pages around 153-159 are missing based on text dump.
    # The last MD text is "แต่ต่อมาผู้ถูกฟ้องคดีได้มีหนังสือ"
    # This text appears in the PDF text dump around line 718 (Page 154 header nearby?)
    # Let's extract a safe range.
    
    # We will search for the specific anchor text to be sure of the start page.
    start_text_anchor = "แต่ต่อมาผู้ถูกฟ้องคดีได้มีหนังสือ"
    
    pages_found = []
    
    start_index = -1
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if start_text_anchor in text:
            start_index = i
            print(f"Found start anchor on index {i}")
            break
            
    if start_index != -1:
        # Extract from start_index to end of file (since MD ends there)
        # But wait, does part_09 END at that point? The user says it's missing ~9%.
        # Does the PDF go on for many more pages?
        # Let's just extract EVERYTHING from start_index to the end of the PDF file.
        # Part 09 is one of many parts, so the PDF itself (part_09.pdf) might check out.
        
        print(f"Extracting from index {start_index} to end ({len(reader.pages)})")
        for i in range(start_index, len(reader.pages)):
            writer.add_page(reader.pages[i])
            pages_found.append(i)
            
    if pages_found:
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)
        print(f"✅ Created {output_pdf_path} with {len(pages_found)} pages.")
    else:
        print("❌ Could not find anchor text.")

if __name__ == "__main__":
    main()
