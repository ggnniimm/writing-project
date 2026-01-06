from pypdf import PdfReader
import re

pdf_path = "etc/split_vol07/part_07.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

def normalize(t):
    return re.sub(r'\s+', '', t)

norm_text = normalize(full_text)
print(f"Total Normalized Length: {len(norm_text)}")

# Pattern found in previous output: "แนวคาวินิจฉัยของศาลปกครอง"
# Note: "คำ" became "คา" in extraction
snippet = "แนวคาวินิจฉัยของศาลปกครอง"

print(f"\n--- Searching for: {snippet} ---")
start = 0
while True:
    idx = norm_text.find(snippet, start)
    if idx == -1:
        break
    
    # Print context, especially AFTER the snippet to see the number
    context_start = max(0, idx - 10)
    context_end = min(len(norm_text), idx + len(snippet) + 10)
    print(f"Found at {idx}: ...{norm_text[context_start:context_end]}...")
    start = idx + 1
