from pypdf import PdfReader
import re

pdf_path = "etc/split_vol07/part_06.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

# Normalize for searching
def normalize(t):
    return re.sub(r'\s+', '', t)

# Broad search for Kanchanaburi to locate the section
snippets = [
    "กาญจนบุรี"
]

print(f"Total PDF Length: {len(full_text)}")
norm_text = normalize(full_text)

for snip in snippets:
    print(f"\n--- Searching for: {snip} ---")
    # Find all occurrences
    start = 0
    while True:
        idx = norm_text.find(snip, start)
        if idx == -1:
            break
        # Print generous context
        context_start = max(0, idx - 100)
        context_end = min(len(norm_text), idx + 100)
        print(f"Context: ...{norm_text[context_start:context_end]}...")
        start = idx + 1
