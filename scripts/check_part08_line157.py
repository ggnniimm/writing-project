from pypdf import PdfReader
import re

pdf_path = "etc/split_vol07/part_08.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

def normalize(t):
    return re.sub(r'\s+', '', t)

norm_text = normalize(full_text)

# Line 157 context contains "SSR Mode S"
snippet = "SSR"

print(f"\n--- Searching for SSR ---")
start = 0
while True:
    idx = norm_text.find(snippet, start)
    if idx == -1:
        break
    
    sub_context = norm_text[idx-50:idx+50]
    print(f"Found match: ...{sub_context}...")
    
    start = idx + 1
