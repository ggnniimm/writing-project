import sys
from pypdf import PdfReader, PdfWriter

input_pdf = sys.argv[1]
# Split into 10 pages chunks
reader = PdfReader(input_pdf)
total_pages = len(reader.pages)
chunk_size = 10

for i in range(0, total_pages, chunk_size):
    writer = PdfWriter()
    end_page = min(i + chunk_size, total_pages)
    for p in range(i, end_page):
        writer.add_page(reader.pages[p])
    
    output_filename = input_pdf.replace(".pdf", f"_part_{i//chunk_size + 1}.pdf")
    with open(output_filename, "wb") as f:
        writer.write(f)
    print(f"Created {output_filename}")
