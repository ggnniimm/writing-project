
import sys
import os
from pypdf import PdfReader, PdfWriter

def split_pdf(input_path):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    # Split into 2 chunks
    chunk_size = total_pages // 2 + (total_pages % 2) # e.g. 20 -> 10, 11
    
    base_name = os.path.splitext(input_path)[0]
    
    start = 0
    end = chunk_size
    
    # Chunk 1
    writer1 = PdfWriter()
    for i in range(start, min(end, total_pages)):
        writer1.add_page(reader.pages[i])
    
    output1 = f"{base_name}_part1.pdf"
    with open(output1, "wb") as f:
        writer1.write(f)
    print(f"Created {output1}")
        
    # Chunk 2
    writer2 = PdfWriter()
    for i in range(end, total_pages):
        writer2.add_page(reader.pages[i])
        
    output2 = f"{base_name}_part2.pdf"
    with open(output2, "wb") as f:
        writer2.write(f)
    print(f"Created {output2}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 split_pdf.py <input_pdf>")
        sys.exit(1)
    
    split_pdf(sys.argv[1])
