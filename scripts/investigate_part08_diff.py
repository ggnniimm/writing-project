from pypdf import PdfReader
import difflib
import re

# 1. Load Texts
md_path = "etc/split_vol07/part_08.md"
pdf_path = "etc/split_vol07/part_08.pdf"

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

reader = PdfReader(pdf_path)
pdf_text = ""
for page in reader.pages:
    pdf_text += page.extract_text() + "\n"

# 2. Normalize slightly for comparison (keep newlines to spot headers)
def specific_normalize(t):
    # Remove all whitespace for content checking
    return re.sub(r'\s+', '', t)

# Split original by lines for reference, but use normalized string for diffing? 
# Better: normalize each line and compare?
# If we normalize the whole text, we lose line context.
# Let's try to find chunks of text in PDF that are NOT in MD at all.

md_norm = specific_normalize(md_text)
pdf_norm = specific_normalize(pdf_text)

print(f"MD Normalized Char Length: {len(md_norm)}")
print(f"PDF Normalized Char Length: {len(pdf_norm)}")
print(f"Difference: {len(pdf_norm) - len(md_norm)} chars")

# Check for specific suspicious missing phrases (detected in previous run)
# "หากเห็นว่าไม่ถูกต้องเหมาะสม"
phrases_to_check = [
    "หากเห็นว่าไม่ถูกต้องเหมาะสมย่อมมีอำนาจสั่งแก้ไข",
    "กับพฤติการณ์การกระทำความผิดได้",
    "ซึ่งผู้ถูกฟ้องคดีที่๑ย่อมต้องผูกพันในการสั่งลงโทษ",
    "เป็นไล่ผู้ฟ้องคดีออกจากราชการ",
]

print("\n--- Checking specific phrases from previous diff ---")
for p in phrases_to_check:
    # searching in MD
    if p in md_norm:
        print(f"FOUND: {p[:30]}...")
    else:
        print(f"MISSING: {p[:30]}...")

# Heuristic: headers often contribute to size diff
common_headers = [
    "บันทึกวิเคราะห์สรุป",
    "ศาลปกครองสูงสุด",
    "สำนักประธานศาลปกครองสูงสุด",
    "กลุ่มงานวิชาการ",
]

print("\n--- Counting Headers in PDF vs MD ---")
for h in common_headers:
    h_norm = specific_normalize(h)
    pdf_count = pdf_norm.count(h_norm)
    md_count = md_norm.count(h_norm)
    print(f"'{h}': PDF={pdf_count}, MD={md_count} -> Diff={pdf_count - md_count}")


