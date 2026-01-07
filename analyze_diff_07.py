import difflib
import re

def normalize_text(text):
    # Remove all whitespace to ignore formatting differences
    return re.sub(r'\s+', '', text)

def main():
    pdf_txt_path = 'etc/split_vol07/temp_part_07_analysis.txt'
    md_path = 'etc/split_vol07/part_07.md'
    
    print(f"Reading {pdf_txt_path}...")
    with open(pdf_txt_path, 'r', encoding='utf-8') as f:
        pdf_text = f.read()
        
    print(f"Reading {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Pre-clean PDF text: remove typical footer noise that we know we don't want
    pdf_text = re.sub(r'ศาลปกครองแห่งความเชื่อมั่น\s*TRUST', '', pdf_text)
    
    # Also remove page headers for cleaner comparison? 
    # Actually, let's keep headers as content anchors, but they might format differently.
    
    # Normalize for comparison
    pdf_norm = normalize_text(pdf_text)
    md_norm = normalize_text(md_text)
    
    print(f"PDF content length (normalized): {len(pdf_norm)}")
    print(f"MD content length (normalized): {len(md_norm)}")
    print(f"Diff: {len(md_norm) - len(pdf_norm)}")
    
    # Use SequenceMatcher to find missing blocks
    s = difflib.SequenceMatcher(None, pdf_norm, md_norm)
    
    print("\n--- Missing Blocks (Present in PDF but NOT in MD) ---")
    threshold = 50 # Only show blocks larger than this
    
    count = 0
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'delete': # content in pdf (i1:i2) not in md (j1:j2)
            missing = pdf_norm[i1:i2]
            if len(missing) > threshold:
                count += 1
                # Try to map back to original text for context (approximate)
                print(f"\n[MISSING BLOCK #{count}] Size: {len(missing)} chars")
                print(f"Preview: {missing[:100]}...")
                
                # Find context in original PDF text (approx)
                # This is hard because we stripped whitespace.
                # Let's just output the normalized missing text.
                
    if count == 0:
        print("\nNo significant missing blocks found.")

if __name__ == "__main__":
    main()
