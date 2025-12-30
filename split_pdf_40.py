
import os
import math
from pypdf import PdfReader, PdfWriter

source_file = 'etc/ref_research_admin_court_rulings_digest_v14_2569.pdf'
output_dir = 'etc/split_v14_2569_40'
num_parts = 40

def split_pdf():
    if not os.path.exists(source_file):
        print(f"Error: Source file '{source_file}' not found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    reader = PdfReader(source_file)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")

    pages_per_part = math.ceil(total_pages / num_parts)
    print(f"Pages per part: {pages_per_part}")

    for i in range(num_parts):
        start_page = i * pages_per_part
        end_page = min(start_page + pages_per_part, total_pages)

        if start_page >= total_pages:
            break

        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        part_num = i + 1
        output_filename = os.path.join(output_dir, f"part_{part_num:02d}.pdf")

        with open(output_filename, 'wb') as out_f:
            writer.write(out_f)
        
        print(f"Wrote pages {start_page+1}-{end_page} to {output_filename}")

if __name__ == "__main__":
    split_pdf()
