
from pypdf import PdfReader, PdfWriter

def extract_pages(source_path, start_page, end_page, output_path):
    reader = PdfReader(source_path)
    writer = PdfWriter()
    
    # pypdf pages are 0-indexed
    # User wants page 452 (physically?)
    # Let's extract a range around expected numbers
    # We suspect physical page 452 maps to content page 452?
    # Usually there is a preamble (ToC) so physical page > content page.
    # Let's extract physical pages 450 to 500 first.
    
    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])

    with open(output_path, "wb") as f:
        writer.write(f)

source = "raw_pdfs/Academic_230317_084750-2.pdf"
extract_pages(source, 450, 500, "temp_check_pages.pdf")
