import re
from pypdf import PdfReader

def normalize(text):
    return re.sub(r'\s+', '', text)

# PDF Contexts
pdf_contexts = []
reader = PdfReader("etc/split_vol07/part_01.pdf")
pdf_text = ""
for page in reader.pages:
    pdf_text += page.extract_text()
pdf_text = normalize(pdf_text)

matches = re.finditer(r'๒๖๒', pdf_text)
for m in matches:
    start = max(0, m.start() - 30)
    end = m.end()
    pdf_contexts.append(pdf_text[start:end])

# MD Contexts
with open("etc/split_vol07/part_01.md", 'r') as f:
    md_text = f.read()
md_text = normalize(md_text)

md_contexts = []
matches = re.finditer(r'๒๖๒', md_text)
for m in matches:
    start = max(0, m.start() - 30)
    end = m.end()
    md_contexts.append(md_text[start:end])

print("--- PDF Contexts (Total: {}) ---".format(len(pdf_contexts)))
for c in pdf_contexts:
    print(c)

print("\n--- MD Contexts (Total: {}) ---".format(len(md_contexts)))
for c in md_contexts:
    print(c)
