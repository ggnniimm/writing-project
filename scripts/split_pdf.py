
import sys
import os
from pypdf import PdfReader, PdfWriter

def split_pdf_chunks(input_path, output_dir, chunk_size=20):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    
    num_chunks = (total_pages + chunk_size - 1) // chunk_size
    
    print(f"Splitting {total_pages} pages into {num_chunks} parts of ~{chunk_size} pages each.")

    for i in range(num_chunks):
        start_page = i * chunk_size
        end_page = min((i + 1) * chunk_size, total_pages)
        
        writer = PdfWriter()
        for p in range(start_page, end_page):
            writer.add_page(reader.pages[p])
            
        part_num = i + 1
        output_filename = f"part_{part_num:02d}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        # print(f"Created {output_filename} ({start_page+1}-{end_page})")

    print(f"✅ Successfully split into {num_chunks} parts in {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 split_pdf.py <input_pdf> <output_dir> [chunk_size]")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_directory = sys.argv[2]
    
    chunk_s = 20
    if len(sys.argv) > 3:
        chunk_s = int(sys.argv[3])
    
    split_pdf_chunks(input_pdf, output_directory, chunk_s)
