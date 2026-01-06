import difflib
import sys
import re
import unicodedata
from pypdf import PdfReader

def normalize(text):
    # Normalize unicode characters (e.g. combine Thai vowels)
    text = unicodedata.normalize('NFC', text)
    # Remove all whitespace to compare actual chars
    return re.sub(r'\s+', '', text)

def get_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text

def check_diff(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    pdf_text = get_text_from_pdf(pdf_path)
    
    norm_md = normalize(md_text)
    norm_pdf = normalize(pdf_text)
    
    # Use difflib to find differences
    s = difflib.SequenceMatcher(None, norm_pdf, norm_md)
    
    print(f"PDF Normalized Length: {len(norm_pdf)}")
    print(f"MD Normalized Length: {len(norm_md)}")
    print(f"Difference: {len(norm_pdf) - len(norm_md)}")
    
    print("\n--- Differences (PDF -> MD) ---")
    print("Format: [Operation] 'Text in PDF' -> 'Text in MD'")
    
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'replace':
            print(f"[REPLACE] PDF '{norm_pdf[i1:i2]}' -> MD '{norm_md[j1:j2]}'")
        elif tag == 'delete':
            print(f"[MISSING IN MD] '{norm_pdf[i1:i2]}'")
        elif tag == 'insert':
            print(f"[EXTRA IN MD] '{norm_md[j1:j2]}'")

if __name__ == "__main__":
    check_diff("etc/split_vol07/part_01.md", "etc/split_vol07/part_01.pdf")
