import sys
import os
from pypdf import PdfReader, PdfWriter

def split_pdf(input_path, split_page=800):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")

    # Part 1
    writer1 = PdfWriter()
    for i in range(min(split_page, total_pages)):
        writer1.add_page(reader.pages[i])
    
    part1_path = input_path.replace(".pdf", "_part1.pdf")
    with open(part1_path, "wb") as f:
        writer1.write(f)
    print(f"Created {part1_path} ({len(writer1.pages)} pages)")

    # Part 2
    if total_pages > split_page:
        writer2 = PdfWriter()
        for i in range(split_page, total_pages):
            writer2.add_page(reader.pages[i])
        
        part2_path = input_path.replace(".pdf", "_part2.pdf")
        with open(part2_path, "wb") as f:
            writer2.write(f)
        print(f"Created {part2_path} ({len(writer2.pages)} pages)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 split_large_pdf.py <input_pdf>")
    else:
        split_pdf(sys.argv[1])
