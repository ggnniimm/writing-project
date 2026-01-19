from pypdf import PdfReader

pdf_path = "etc/Academic_310717_154727-2_parts/part_37.pdf"
output_path = "part_37_vol8.txt"

reader = PdfReader(pdf_path)
with open(output_path, "w", encoding="utf-8") as f:
    for page in reader.pages:
        text = page.extract_text()
        f.write(text + "\n")

print(f"Extracted {len(reader.pages)} pages to {output_path}")
