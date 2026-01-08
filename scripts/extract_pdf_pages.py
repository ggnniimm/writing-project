import sys
from pypdf import PdfReader, PdfWriter

def extract_pages(input_path, start_page, end_page, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    # Validation
    if start_page < 0 or end_page > len(reader.pages) or start_page >= end_page:
        print(f"Invalid page range: {start_page}-{end_page} (Total: {len(reader.pages)})")
        return

    for i in range(start_page, end_page):
        writer.add_page(reader.pages[i])
        
    with open(output_path, "wb") as f:
        writer.write(f)
        
    print(f"Created {output_path} with pages {start_page} to {end_page-1} (indices)")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python extract_pdf_pages.py <input> <start_index> <end_index__exclusive> <output>")
        sys.exit(1)
        
    extract_pages(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
