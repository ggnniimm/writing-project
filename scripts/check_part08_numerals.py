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
print(f"Total Normalized Length: {len(norm_text)}")

snippets = [
    # Lines 124, 126, 129, 137: Land deed numbers around crocodile (Jorakhe) rock/stone
    "ตำบลจระเข้หิน", 
    "โฉนดที่ดินเลขที่",
    
    # Line 157: 5 sets
    "จำนวน5ชุด", "จำนวน๕ชุด", "จำนวน๖ชุด", 
    
    # Line 194: 5 people
    "พวกรวม5คน", "พวกรวม๕คน", "พวกรวม๖คน",

    # Line 289, 291: Defendant No. 5
    "ไปยังผู้ถูกฟ้องคดีที่",
]

print(f"\n--- Searching for snippets ---")
for snip in snippets:
    print(f"\nSearching for: {snip}")
    start = 0
    while True:
        idx = norm_text.find(snip, start)
        if idx == -1:
            break
        
        # Context generally
        context_start = max(0, idx - 50)
        context_end = min(len(norm_text), idx + len(snip) + 50)
        print(f"Found at {idx}: ...{norm_text[context_start:context_end]}...")
        start = idx + 1
