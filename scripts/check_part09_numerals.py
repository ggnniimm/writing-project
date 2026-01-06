from pypdf import PdfReader
import re

pdf_path = "etc/split_vol07/part_09.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

def normalize(t):
    return re.sub(r'\s+', '', t)

norm_text = normalize(full_text)

# Search for "ซอย" and "5" context
# Target: "ซอย 5" or "ซอย ๕"
snippets = [
    "ในชุมชนฟ้าฮ่ามซอย",
    "ซอย5",
    "ซอย๕"
]

print(f"\n--- Searching for snippets in PDF ---")
for snip in snippets:
    print(f"\nSearching for: {snip}")
    start = 0
    while True:
        idx = norm_text.find(snip, start)
        if idx == -1:
            break
        
        context_start = max(0, idx - 40)
        context_end = min(len(norm_text), idx + len(snip) + 40)
        print(f"Found at {idx}: ...{norm_text[context_start:context_end]}...")
        start = idx + 1
