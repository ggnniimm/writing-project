from pypdf import PdfReader, PdfWriter
import os

def extract_part01(input_path, output_path):
    print(f"📄 Extracting part 01 from {input_path}...")
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # Page 1 to 20 (index 0 to 19)
    for p in range(0, 20):
        if p < len(reader.pages):
            writer.add_page(reader.pages[p])
            
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"✅ Created {output_path}")

if __name__ == "__main__":
    input_pdf = "raw_pdfs/Academic_180319_152538-2.pdf"
    output_pdf = "etc/split_vol08/part_01.pdf"
    extract_part01(input_pdf, output_pdf)
