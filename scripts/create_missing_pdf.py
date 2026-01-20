
from pypdf import PdfReader, PdfWriter
import sys

input_pdf = "etc/Academic_310717_154727-2_parts/part_40.pdf"
output_pdf = "part_40_missing.pdf"

reader = PdfReader(input_pdf)
writer = PdfWriter()

# Pages 18, 19, 20 correspond to indices 17, 18, 19
# Verify we don't go out of bounds
total_pages = len(reader.pages)
print(f"Total pages: {total_pages}")

for i in range(17, min(20, total_pages)):
    print(f"Adding page index {i}")
    writer.add_page(reader.pages[i])

writer.write(output_pdf)
print(f"Created {output_pdf}")
