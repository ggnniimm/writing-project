import re
import subprocess
import os

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

def verify_part01():
    md_path = "etc/split_vol08/part_01.md"
    pdf_path = "etc/split_vol08/part_01.pdf"
    
    if not os.path.exists(md_path) or not os.path.exists(pdf_path):
        print("❌ Missing files for verification.")
        return

    pdf_text, txt_path = extract_text_from_pdf(pdf_path)
    if pdf_text is None: return

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    pdf_counts, pdf_total = count_thai_numerals(pdf_text)
    md_counts, md_total = count_thai_numerals(md_text)

    print("\n--- Thai Numerals Verification Result ---")
    print(f"{'Digit':<6} | {'PDF':<6} | {'MD':<6} | {'Status'}")
    print("-" * 35)
    
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    for digit in thai_digits:
        status = "✅" if pdf_counts[digit] == md_counts[digit] else "❌"
        print(f"{digit:<6} | {pdf_counts[digit]:<6} | {md_counts[digit]:<6} | {status}")
    
    print("-" * 35)
    total_status = "✅" if pdf_total == md_total else "❌"
    print(f"{'Total':<6} | {pdf_total:<6} | {md_total:<6} | {total_status}")
    
    # Check for common keywords likely to be at start/end
    print("\n--- Header/Footer Check ---")
    headers = ["แนวดำวินิจฉัยของศาลปกครอง", "เล่มที่ ๘", "ISBN"]
    for h in headers:
        if h in md_text:
            print(f"✅ Found header/meta: {h}")
        else:
            print(f"❌ Missing header/meta: {h}")

    years = ["๒๕๖๐", "๒๕๖๑", "๒๕๖๒"]
    for y in years:
        if y in md_text:
            print(f"✅ Found year: {y}")

    print(f"\n📝 Raw extraction saved to: {txt_path}")

if __name__ == "__main__":
    verify_part01()
