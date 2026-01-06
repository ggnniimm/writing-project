from pypdf import PdfReader
import re

pdf_path = "etc/split_vol07/part_04.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

# Normalize for searching
def normalize(t):
    return re.sub(r'\s+', '', t)

# We will search for specific snippets and print surrounding text
snippets = [
    # Line 548 context: "ผู้ฟ้องคดีที่ ๕ และผู้ฟ้องคดีที่ 5 ซึ่งมีบ้านพักอาศัย"
    "ผู้ฟ้องคดีที่๕และผู้ฟ้องคดีที่",
    # Line 650 context: "ที่ 5 หรือผู้ได้รับอนุญาตตามประทานบัตร"
    "ค่าใช้จ่ายของผู้ถูกฟ้องคดีที่"
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
            if start == 0:
                print("Not found!")
            break
        # Print context
        context_start = max(0, idx - 10)
        context_end = min(len(norm_text), idx + len(snip) + 10)
        print(f"Context: ...{norm_text[context_start:context_end]}...")
        start = idx + 1
