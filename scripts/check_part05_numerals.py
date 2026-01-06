from pypdf import PdfReader
import re

pdf_path = "etc/split_vol07/part_05.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

# Normalize for searching
def normalize(t):
    return re.sub(r'\s+', '', t)

# We will search for specific snippets and print surrounding text
snippets = [
    # Line 364 context: "เป็นไปตามข้อ 5 ของประกาศมหาวิทยาลัยสงขลานครินทร์"
    "เป็นไปตามข้อ",
    "ของประกาศมหาวิทยาลัยสงขลานครินทร์เรื่องหลักเกณฑ์การพัฒนา"
]

print(f"Total PDF Length: {len(full_text)}")
norm_text = normalize(full_text)

for snip in snippets:
    print(f"\n--- Searching for: {snip} ---")
    # Find all occurrences
    start = 0
    found = False
    while True:
        idx = norm_text.find(snip, start)
        if idx == -1:
            if not found and start == 0:
                print("Not found!")
            break
        found = True
        # Print context
        context_start = max(0, idx - 20)
        context_end = min(len(norm_text), idx + len(snip) + 30)
        print(f"Context: ...{norm_text[context_start:context_end]}...")
        start = idx + 1
