import pdfplumber
import re
import sys
import difflib
from collections import Counter

def normalize_text(text):
    """Normalize text for comparison."""
    # Remove markdown specific chars that strictly don't appear in PDF text usually in this form
    # But keep it simple: remove bold, italic markers
    text = text.replace('**', '').replace('__', '')
    text = text.replace('##', '') # Remove headers
    
    # Remove strict newlines and multi-spaces for content stream comparison
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_thai_numerals(text):
    """Extract Thai numerals."""
    return re.findall(r'[๐-๙]+(?:[.,][๐-๙]+)*', text)

def verify_content(md_path, pdf_path):
    print(f"Verifying {md_path} against {pdf_path}...")
    
    # 1. Read Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 2. Extract PDF Text
    pdf_text_all = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pdf_text_all += text + "\n"
    
    # Save PDF text for debug
    with open("debug_pdf_extract.txt", "w", encoding="utf-8") as f:
        f.write(pdf_text_all)
        
    # 3. NUMERAL VERIFICATION
    print("\n--- Numeral Verification ---")
    md_nums = extract_thai_numerals(md_content)
    pdf_nums = extract_thai_numerals(pdf_text_all)
    
    print(f"MD Numerals: {len(md_nums)}")
    print(f"PDF Numerals: {len(pdf_nums)}")
    
    # Save numerals for inspection
    with open("debug_md_nums.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(md_nums))
    with open("debug_pdf_nums.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(pdf_nums))
    
    md_counts = Counter(md_nums)
    pdf_counts = Counter(pdf_nums)
    
    all_num_keys = set(md_nums) | set(pdf_nums)
    num_discrepancies = []
    
    for num in sorted(all_num_keys):
        if md_counts[num] != pdf_counts[num]:
            num_discrepancies.append((num, md_counts[num], pdf_counts[num]))
            
    if num_discrepancies:
        print("❌ Numeral Discrepancies found (Num: MD count vs PDF count). Top 50 by difference:")
        # Sort by absolute difference
        num_discrepancies.sort(key=lambda x: abs(x[1]-x[2]), reverse=True)
        for d in num_discrepancies[:50]:
            print(f"  '{d[0]}': MD={d[1]}, PDF={d[2]}")
    else:
        print("✅ Numerals match perfectly!")

    # 4. TEXT STREAM VERIFICATION
    print("\n--- Text Content Verification ---")
    
    # Clean PDF text by removing lines that are likely garbage
    # Heuristic: If line has < 2 valid Thai/English chars or has > 50% unknown symbols
    def is_garbage(line):
        line = line.strip()
        if not line: return True
        # Count Thai chars
        thai_chars = len(re.findall(r'[ก-๙]', line))
        if thai_chars < 3 and len(line) > 10: return True 
        return False

    pdf_lines = pdf_text_all.split('\n')
    clean_pdf_lines = [l for l in pdf_lines if not is_garbage(l)]
    clean_pdf_text = "\n".join(clean_pdf_lines)
    
    # Save clean PDF text
    with open("debug_clean_pdf.txt", "w", encoding="utf-8") as f:
        f.write(clean_pdf_text)

    # Normalize both
    norm_md = normalize_text(md_content)
    norm_pdf = normalize_text(clean_pdf_text)
    
    # Check for missing chunks again with cleaned text
    pdf_chunks = [c.strip() for c in clean_pdf_text.split('\n') if c.strip()]
    
    missing_chunks = []
    for chunk in pdf_chunks:
        clean_chunk = re.sub(r'\s+', ' ', chunk).strip()
        if len(clean_chunk) < 5: continue
        
        # Exact substring search in normalized MD
        if clean_chunk not in norm_md:
            missing_chunks.append(clean_chunk)

    if missing_chunks:
        print(f"❌ Found {len(missing_chunks)} clean text blocks from PDF missing in MD:")
        for mc in missing_chunks[:20]:
            print(f"  Missing: '{mc}'")
    else:
        print("✅ All clean PDF text blocks found in MD!")

    # 5. Reverse check: MD text not in PDF? (Generated content / hallucinations)
    # This is harder because MD has valid formatting text.
    # We'll rely on numeral check and the PDF->MD extraction check primarily.

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 verify_full_content.py <md_path> <pdf_path>")
        sys.exit(1)
        
    verify_content(sys.argv[1], sys.argv[2])
