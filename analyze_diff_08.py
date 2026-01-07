
import re
import difflib

def normalize_text(text):
    # Remove all whitespace for char counting/comparison to ignore formatting diffs
    return re.sub(r'\s+', '', text)

def main():
    pdf_text_path = 'etc/split_vol07/temp_part_08_analysis.txt'
    md_path = 'etc/split_vol07/part_08.md'

    print(f"Reading {pdf_text_path}...")
    with open(pdf_text_path, 'r', encoding='utf-8') as f:
        pdf_text = f.read()

    print(f"Reading {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    norm_pdf = normalize_text(pdf_text)
    norm_md = normalize_text(md_text)

    print(f"PDF content length (normalized): {len(norm_pdf)}")
    print(f"MD content length (normalized): {len(norm_md)}")
    print(f"Diff: {len(norm_md) - len(norm_pdf)}")

    # Use difflib to find large missing blocks
    s = difflib.SequenceMatcher(None, norm_pdf, norm_md)
    
    print("\n--- Significant Discrepancies (Length > 100) ---")
    conflict_found = False
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'equal':
            continue
            
        chunk_pdf = norm_pdf[i1:i2]
        chunk_md = norm_md[j1:j2]
        
        if len(chunk_pdf) > 100 or len(chunk_md) > 100:
            conflict_found = True
            print(f"\n[{tag.upper()}] PDF len: {len(chunk_pdf)}, MD len: {len(chunk_md)}")
            if len(chunk_pdf) > 0:
                print(f"PDF Preview: {chunk_pdf[:100]}...")
            if len(chunk_md) > 0:
                print(f"MD Preview: {chunk_md[:100]}...")
    
    if not conflict_found:
        print("\nNo significant discrepancies found.")

if __name__ == "__main__":
    main()
