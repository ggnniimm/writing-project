from pypdf import PdfReader
import re

pdf_path = "etc/split_vol07/part_03.pdf"
reader = PdfReader(pdf_path)
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

# Normalize for searching
def normalize(t):
    return re.sub(r'\s+', '', t)

contexts = [
    # Line 29: 5 แนวคำวินิจฉัยของศาลปกครอง
    "แนวคำวินิจฉัยของศาลปกครอง",
    # Line 66: จัดตั้งขึ้นตามมาตรา 5 
    "จัดตั้งขึ้นตามมาตรา",
    # Line 294: ...และมาตรา 5
    "และมาตรา",
    # Line 301: ...และมาตรา 5
    "และมาตรา",
    # Line 460: ลงวันที่ 5 กันยายน
    "ลงวันที่"
]

print(f"Total PDF Length: {len(full_text)}")

# We will search for specific snippets and print surrounding text
snippets = [
    # Line 29 context: Search for text immediately following the header
    "สำนักงานคณะกรรมการกำกับและส่งเสริมการประกอบ",
    # Line 294 context: Search for text following "มาตรา 5"
    "แห่งพระราชบัญญัติป่าสงวนแห่งชาติ"
]

norm_text = normalize(full_text)

for snip in snippets:
    print(f"\n--- Searching for: {snip} ---")
    # Find all occurrences
    start = 0
    while True:
        idx = norm_text.find(snip, start)
        if idx == -1:
            break
        # Print context
        context_start = max(0, idx - 10)
        context_end = min(len(norm_text), idx + len(snip) + 10)
        print(f"Context: ...{norm_text[context_start:context_end]}...")
        start = idx + 1
