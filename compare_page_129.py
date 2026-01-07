
import re

def clean(text):
    return re.sub(r'\s+', '', text)

def get_page_129_pdf():
    # Load full dump
    with open('etc/split_vol07/temp_part_09_analysis.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Locate page 129
    # Look for header "๑๒๙ แนวคาวินิจฉัยของศาลปกครอง" (PDF dump uses 'คา' vs 'คำ' sometimes?)
    # or "แนวคาวินิจฉัยของศาลปกครอง ๑๒๙"
    # From grep above: "แนวคาวินิจฉัยของศาลปกครอง ๑๒๙"
    
    start_marker = "แนวคาวินิจฉัยของศาลปกครอง ๑๒๙"
    end_marker = "๑๓๐ แนวคาวินิจฉัยของศาลปกครอง" # Next page header? or footer?
    
    # Actually, let's just grab a chunk around the marker
    start_idx = content.find(start_marker)
    if start_idx == -1:
        # Try 'คำ' instead of 'คา'
        start_marker = "แนวคำวินิจฉัยของศาลปกครอง ๑๒๙"
        start_idx = content.find(start_marker)
        
    if start_idx == -1:
        return "PAGE_NOT_FOUND_IN_PDF"
        
    # Get 1000 chars
    chunk = content[start_idx:start_idx+1000]
    return chunk

def get_page_129_md():
    with open('etc/split_vol07/part_09.md', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Marker in MD: "แนวคำวินิจฉัยของศาลปกครอง ๑๒๙"
    start_marker = "แนวคำวินิจฉัยของศาลปกครอง ๑๒๙"
    start_idx = content.find(start_marker)
    
    if start_idx == -1:
        return "PAGE_NOT_FOUND_IN_MD"
        
    chunk = content[start_idx:start_idx+1000]
    return chunk

def main():
    pdf_text = get_page_129_pdf()
    md_text = get_page_129_md()
    
    c_pdf = clean(pdf_text)
    c_md = clean(md_text)
    
    print("--- PDF (Cleaned, first 200 chars) ---")
    print(c_pdf[:200])
    print("\n--- MD (Cleaned, first 200 chars) ---")
    print(c_md[:200])
    
    # Diff?
    # Let's just find the first difference
    limit = min(len(c_pdf), len(c_md))
    for i in range(limit):
        if c_pdf[i] != c_md[i]:
            print(f"\n❌ Difference at index {i}:")
            print(f"PDF context: ...{c_pdf[i-10:i]} [{c_pdf[i]}] {c_pdf[i+1:i+10]}...")
            print(f"MD  context: ...{c_md[i-10:i]} [{c_md[i]}] {c_md[i+1:i+10]}...")
            break

if __name__ == "__main__":
    main()
