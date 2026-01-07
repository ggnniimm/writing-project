
import os
import re
import subprocess
import json

def get_counts(text):
    # Raw count
    raw_count = len(text)
    # Non-whitespace count
    clean_content = re.sub(r'\s+', '', text)
    nws_count = len(clean_content)
    return raw_count, nws_count

def run_pdftotext(pdf_path, output_txt_path):
    # -layout is good for reading but sometimes adds too much space.
    # For char count, -raw or default might be fine, but we used -layout before.
    # We'll use -layout to match previous successful manual check methodology.
    subprocess.run(['pdftotext', '-layout', pdf_path, output_txt_path], check=True)

def verify_file(part_num):
    part_str = f"part_{part_num:02d}"
    pdf_path = f"etc/split_vol07/{part_str}.pdf"
    md_path = f"etc/split_vol07/{part_str}.md"
    temp_txt_path = f"etc/split_vol07/temp_ver_{part_str}.txt"
    
    if not os.path.exists(pdf_path):
        return {"part": part_str, "error": "PDF not found"}
    if not os.path.exists(md_path):
        return {"part": part_str, "error": "MD not found"}

    try:
        # 1. Extract PDF Text
        run_pdftotext(pdf_path, temp_txt_path)
        
        # 2. Read PDF Text
        with open(temp_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            pdf_text = f.read()
            
        # 3. Read MD Text
        with open(md_path, 'r', encoding='utf-8', errors='ignore') as f:
            md_text = f.read()
            
        # 4. Get Counts
        pdf_raw, pdf_nws = get_counts(pdf_text)
        md_raw, md_nws = get_counts(md_text)
        
        diff = md_nws - pdf_nws
        diff_pct = (diff / pdf_nws) * 100 if pdf_nws > 0 else 0
        
        # Cleanup
        if os.path.exists(temp_txt_path):
            os.remove(temp_txt_path)
            
        status = "OK"
        if abs(diff) > 500:
             status = "⚠️ CHECK"
        if abs(diff_pct) > 2.0:
             status = "⚠️ CHECK"
             
        return {
            "part": part_str,
            "status": status,
            "md_chars": md_nws,
            "pdf_chars": pdf_nws,
            "diff": diff,
            "diff_pct": diff_pct
        }
    except Exception as e:
        return {"part": part_str, "error": str(e)}

def main():
    results = []
    print(f"{'Part':<10} | {'Status':<10} | {'MD Chars':<10} | {'PDF Chars':<10} | {'Diff':<8} | {'Diff %':<8}")
    print("-" * 70)
    
    for i in range(1, 12): # 1 to 11
        res = verify_file(i)
        
        if "error" in res:
            print(f"{res['part']:<10} | ERROR: {res['error']}")
        else:
            diff_str = f"{res['diff']:+d}"
            print(f"{res['part']:<10} | {res['status']:<10} | {res['md_chars']:<10} | {res['pdf_chars']:<10} | {diff_str:<8} | {res['diff_pct']:>6.2f}%")
        
        results.append(res)
        
    # Analysis
    print("\n--- Summary ---")
    issues = [r for r in results if r.get('status') != "OK" and "error" not in r]
    if not issues:
        print("✅ All files (01-11) passed character count verification.")
    else:
        print(f"⚠️ Found {len(issues)} potential issues:")
        for issue in issues:
            print(f"  - {issue['part']}: Diff {issue['diff']} chars ({issue['diff_pct']:.2f}%)")

if __name__ == "__main__":
    main()
