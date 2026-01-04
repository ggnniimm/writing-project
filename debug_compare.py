import re
import sys
import pdfplumber
import unicodedata

def normalize_text(text):
    if not text: return ""
    pua_map = {
        '\uf70a': '่', '\uf70b': '้', '\uf70c': '๊', '\uf70d': '๋', '\uf70e': '์',
        '\uf701': '่', '\uf702': '้', '\uf703': '๊', '\uf704': '๋',
        '\uf710': '่', '\uf711': '้', '\uf712': '๊', '\uf713': '๋', '\uf714': '์',
        '\uf705': '่', '\uf706': '้', '\uf707': '๊', '\uf708': '๋', '\uf709': '์'
    }
    for pua, std in pua_map.items():
        text = text.replace(pua, std)
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\s+', '', text)
    return text

def is_footer(line):
    norm_line = normalize_text(line)
    keywords = [
        normalize_text("สายด่วนศาลปกครอง ๑๓๕๕"),
        normalize_text("ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน"),
        "TRUST"
    ]
    for k in keywords:
        if k in norm_line: return True
    return False

pdf_file = sys.argv[1]
md_file = sys.argv[2]

with pdfplumber.open(pdf_file) as pdf:
    text = pdf.pages[-1].extract_text() or ""
    pdf_lines = [l.strip() for l in text.split('\n') if l.strip()]
    pdf_valid = [l for l in pdf_lines if not is_footer(l)]
    print(f"PDF Valid lines (last 3): {pdf_valid[-3:]}")

with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()
    md_lines = [l.strip() for l in md_content.split('\n') if l.strip()]
    md_valid = [l for l in md_lines if not is_footer(l)]
    print(f"MD Valid lines (last 3): {md_valid[-3:]}")

p_norm = normalize_text(pdf_valid[-1]) if pdf_valid else ""
m_norm = normalize_text(md_valid[-1]) if md_valid else ""

print(f"PDF Norm: '{p_norm[-50:]}'")
print(f"MD Norm : '{m_norm[-50:]}'")
print(f"Equal? {p_norm == m_norm}")
