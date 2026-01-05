import re
import subprocess
import os
import sys

def extract_text_from_pdf(pdf_path):
    print(f"📄 Extracting text from {pdf_path}...")
    txt_path = pdf_path.replace(".pdf", "_raw.txt")
    try:
        subprocess.run(["pdftotext", "-layout", pdf_path, txt_path], check=True)
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read(), txt_path
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def count_thai_numerals(text):
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    counts = {digit: text.count(digit) for digit in thai_digits}
    total = sum(counts.values())
    return counts, total

def verify_part(part_num):
    part_str = str(part_num).zfill(2)
    md_path = f"etc/split_vol08/part_{part_str}.md"
    pdf_path = f"etc/split_vol08/part_{part_str}.pdf"
    
    if not os.path.exists(md_path) or not os.path.exists(pdf_path):
        print(f"❌ Missing files for verification: {md_path} or {pdf_path}")
        return

    pdf_text, txt_path = extract_text_from_pdf(pdf_path)
    if pdf_text is None: return

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    pdf_counts, pdf_total = count_thai_numerals(pdf_text)
    md_counts, md_total = count_thai_numerals(md_text)

    print(f"\n--- Thai Numerals Verification Result (Part {part_str}) ---")
    print(f"{'Digit':<6} | {'PDF':<6} | {'MD':<6} | {'Status'}")
    print("-" * 35)
    
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    for digit in thai_digits:
        status = "✅" if pdf_counts[digit] == md_counts[digit] else "❌"
        print(f"{digit:<6} | {pdf_counts[digit]:<6} | {md_counts[digit]:<6} | {status}")
    
    print("-" * 35)
    total_status = "✅" if pdf_total == md_total else "❌"
    print(f"{'Total':<6} | {pdf_total:<6} | {md_total:<6} | {total_status}")
    
    # Check for common keywords
    print("\n--- Content Check ---")
    years = ["๒๕๖๐", "๒๕๖๑", "๒๕๖๒"]
    for y in years:
        if y in md_text:
            print(f"✅ Found year in MD: {y}")
        if y in pdf_text:
            print(f"✅ Found year in PDF: {y}")

    print(f"\n📝 Raw extraction saved to: {txt_path}")

if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else 2
    verify_part(part)
