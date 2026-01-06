from pypdf import PdfReader

pdf_path = "etc/split_vol07/part_01.pdf"
reader = PdfReader(pdf_path)
text = ""
for page in reader.pages:
    text += page.extract_text()

# Check for "262" (thai)
import re
matches = re.findall(r'๒๖๒', text)
print(f"Found '๒๖๒' count: {len(matches)}")
if matches:
    print("Example context:")
    idx = text.find('๒๖๒')
    print(text[idx-20:idx+20])
