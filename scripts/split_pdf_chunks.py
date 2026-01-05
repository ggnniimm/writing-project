import sys
import os
from pypdf import PdfReader, PdfWriter
import math

def split_pdf_chunks(input_path, output_dir, chunk_size=20):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    num_parts = math.ceil(total_pages / chunk_size)
    print(f"Splitting into {num_parts} parts (max {chunk_size} pages each)...")

    for i in range(num_parts):
        writer = PdfWriter()
        start_page = i * chunk_size
        end_page = min(start_page + chunk_size, total_pages)
        
        for p in range(start_page, end_page):
            writer.add_page(reader.pages[p])
        
        # Output filename format: part_01.pdf, part_02.pdf ...
        part_num = i + 1
        output_filename = f"part_{part_num:02d}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        print(f"Created {output_filename} (Pages {start_page+1}-{end_page})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 split_pdf_chunks.py <input_pdf> <output_dir>")
    else:
        split_pdf_chunks(sys.argv[1], sys.argv[2])
