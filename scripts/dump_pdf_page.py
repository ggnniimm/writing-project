from pypdf import PdfReader

pdf_path = "etc/split_vol07/part_01.pdf"
reader = PdfReader(pdf_path)

# Page 4 in PDF (index 3 if 0-indexed) seems to be the one based on previous output
print("--- Page 4 Content ---")
print(reader.pages[3].extract_text())
print("--- Page 3 Content ---")
print(reader.pages[2].extract_text())
