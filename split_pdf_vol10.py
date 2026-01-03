import os
from pypdf import PdfReader, PdfWriter

# Config
input_pdf = "raw_pdfs/Academic_281020_102051.pdf"
output_dir = "etc/Academic_281020_102051_parts"
chunk_size = 20

def split_pdf():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    print(f"Total Pages: {total_pages}")
    
    part_num = 1
    for i in range(0, total_pages, chunk_size):
        writer = PdfWriter()
        end_page = min(i + chunk_size, total_pages)
        
        for page_idx in range(i, end_page):
            writer.add_page(reader.pages[page_idx])
            
        output_filename = f"Academic_281020_102051_part_{part_num:02d}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, "wb") as out_f:
            writer.write(out_f)
            
        print(f"Created {output_filename} (Pages {i+1}-{end_page})")
        part_num += 1

if __name__ == "__main__":
    split_pdf()
