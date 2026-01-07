
from pypdf import PdfReader, PdfWriter

def extract_pages(source_path, start_page, end_page, output_path):
    reader = PdfReader(source_path)
    writer = PdfWriter()
    
    for i in range(start_page - 1, end_page):
        writer.add_page(reader.pages[i])

    with open(output_path, "wb") as f:
        writer.write(f)

source = "raw_pdfs/Academic_230317_084750-2.pdf"
# Target Content 452 -> Physical ~487
# Target Content 473 -> Physical ~508
extract_pages(source, 480, 520, "temp_check_pages_2.pdf")
