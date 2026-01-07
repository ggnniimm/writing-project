
import re
import difflib

def normalize(text):
    # Remove all whitespace
    text = re.sub(r'\s+', '', text)
    # Normalize common Thai OCR errors for fair comparison
    # 'ดา' -> 'ดำ' (Naive approach, but might help align)
    # Actually, let's NOT normalize spelling, just see the raw diff chunks.
    return text

def main():
    with open('etc/split_vol07/temp_part_09_analysis.txt', 'r', encoding='utf-8') as f:
        pdf_content = f.read()
    
    with open('etc/split_vol07/part_09.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    pdf_clean = normalize(pdf_content)
    md_clean = normalize(md_content)
    
    # Use SequenceMatcher to find missing blocks
    s = difflib.SequenceMatcher(None, pdf_clean, md_clean)
    
    print(f"PDF Size: {len(pdf_clean)}")
    print(f"MD Size:  {len(md_clean)}")
    print(f"Diff:     {len(md_clean) - len(pdf_clean)}")
    
    print("\n--- Significant Missing Chunks (in PDF but not MD) ---")
    
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'delete': # content in PDF (a) but not in MD (b)
             missing_chunk = pdf_clean[i1:i2]
             if len(missing_chunk) > 20: # Ignore tiny noise
                 print(f"[{len(missing_chunk)} chars] MISSING: {missing_chunk[:50]}...{missing_chunk[-20:]}")
        elif tag == 'replace':
             pdf_chunk = pdf_clean[i1:i2]
             md_chunk = md_clean[j1:j2]
             if len(pdf_chunk) > 20 and len(md_chunk) < len(pdf_chunk) / 2:
                 # If replaced by something much smaller, potential loss
                 print(f"[{len(pdf_chunk)} chars] REPLACED by [{len(md_chunk)}]: {pdf_chunk[:50]}...")

if __name__ == "__main__":
    main()
