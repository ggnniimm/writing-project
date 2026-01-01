import pdfplumber
import re
import sys

def extract_thai_numerals(text):
    # Match Thai numerals with optional commas or periods for decimals/thousands
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def compare(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    md_nums = extract_thai_numerals(md_text)
    
    pdf_nums = []
    pdf_text_all = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pdf_text_all += f"\n--- Page {i+1} ---\n" + text
                pdf_nums.extend(extract_thai_numerals(text))
    
    # Save the extracted text for manual inspection if needed
    with open("pdf_extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(pdf_text_all)

    print(f"MD Thai Numerals count: {len(md_nums)}")
    print(f"PDF Thai Numerals count: {len(pdf_nums)}")
    
    # Simple frequency count
    from collections import Counter
    md_counts = Counter(md_nums)
    pdf_counts = Counter(pdf_nums)
    
    all_nums = set(md_nums) | set(pdf_nums)
    discrepancies = []
    for num in sorted(all_nums):
        if md_counts[num] != pdf_counts[num]:
            discrepancies.append((num, md_counts[num], pdf_counts[num]))
    
    if discrepancies:
        print("\nDiscrepancies found (Num, MD count, PDF count):")
        for d in discrepancies[:50]: # Show first 50
            print(f"{d[0]}: MD={d[1]}, PDF={d[2]}")
    else:
        print("\nNo frequency discrepancies found for detected patterns.")

if __name__ == "__main__":
    md_path = sys.argv[1]
    pdf_path = sys.argv[2]
    compare(md_path, pdf_path)
