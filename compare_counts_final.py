import re

def get_counts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Raw count
    raw_count = len(content)
    
    # Non-whitespace count
    clean_content = re.sub(r'\s+', '', content)
    nws_count = len(clean_content)
    
    return raw_count, nws_count

def main():
    md_path = 'etc/split_vol07/part_12.md'
    pdf_txt_path = 'etc/split_vol07/final_pdf_dump.txt'
    
    md_raw, md_nws = get_counts(md_path)
    pdf_raw, pdf_nws = get_counts(pdf_txt_path)
    
    print(f"--- Final Comparison ---")
    print(f"File: {md_path}")
    print(f"  Raw Chars: {md_raw}")
    print(f"  Non-Space: {md_nws}")
    print(f"File: {pdf_txt_path} (Source PDF)")
    print(f"  Raw Chars: {pdf_raw}")
    print(f"  Non-Space: {pdf_nws}")
    
    diff = md_nws - pdf_nws
    print(f"---")
    print(f"Difference (Non-Space): {diff:+d} chars")
    
    if abs(diff) < 500:
        print("✅ Result: Counts are extremely close. Content is likely complete.")
    else:
        print("⚠️ Result: Significant difference detected.")

if __name__ == "__main__":
    main()
