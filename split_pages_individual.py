import sys
import os
from pypdf import PdfReader, PdfWriter

def split_to_pages(pdf_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    reader = PdfReader(pdf_path)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    print(f"Splitting {base_name} ({len(reader.pages)} pages)...")
    
    generated_files = []
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        
        # 01, 02, ...
        page_num = f"{i+1:02d}"
        out_filename = f"{base_name}_page_{page_num}.pdf"
        out_path = os.path.join(output_dir, out_filename)
        
        with open(out_path, "wb") as f_out:
            writer.write(f_out)
        
        generated_files.append(out_path)
        
    print(f"✅ Created {len(generated_files)} pages in {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 split_pages_individual.py <pdf_path> <output_dir>")
        sys.exit(1)
        
    split_to_pages(sys.argv[1], sys.argv[2])
