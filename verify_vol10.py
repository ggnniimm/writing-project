import os
import glob
import re
import pdfplumber
import unicodedata

# Config
parts_dir = "etc/Academic_281020_102051_parts"
total_parts = 49

def normalize_text(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    return re.sub(r'\s+', '', text)

def is_footer(line):
    # Standard footers to ignore
    footers = [
        "ข้อมูลฉับไว", 
        "ไขข้อข้องใจ", 
        "ใส่ใจประชาชน",
        "สายด่วนศาลปกครอง", 
        "1355", 
        "TRUST"
    ]
    norm = normalize_text(line)
    for f in footers:
        if normalize_text(f) in norm:
            return True
    return False

def verify_parts():
    print(f"{'Part':<5} | {'Status':<50}")
    print("-" * 60)
    
    issues = []
    
    for i in range(1, total_parts + 1):
        md_file = os.path.join(parts_dir, f"Academic_281020_102051_part_{i:02d}.md")
        pdf_file = os.path.join(parts_dir, f"Academic_281020_102051_part_{i:02d}.pdf")
        
        if not os.path.exists(md_file):
            print(f"{i:02d}    | MISSING MD File")
            issues.append(f"Part {i}: Missing MD")
            continue
            
        # Check end of content match
        # 1. Get last meaningful PDF line
        pdf_last_line = ""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                if pdf.pages:
                    text = pdf.pages[-1].extract_text() or ""
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    # Filter footers from bottom up
                    valid_lines = [l for l in lines if not is_footer(l)]
                    if valid_lines:
                        pdf_last_line = valid_lines[-1]
        except Exception as e:
            pdf_last_line = f"ERROR: {e}"

        # 2. Get last meaningful MD line
        md_last_line = ""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                # Filter footers from bottom up
                valid_lines = [l for l in lines if not is_footer(l)]
                if valid_lines:
                    md_last_line = valid_lines[-1]
        except Exception as e:
             md_last_line = f"ERROR: {e}"
             
        # Compare
        p_norm = normalize_text(pdf_last_line)[-50:] # Compare last 50 chars
        m_norm = normalize_text(md_last_line)[-50:]
        
        status = "OK"
        if p_norm != m_norm:
            # Fuzzy check: is PDF subset of MD or vice versa?
            if p_norm in m_norm or m_norm in p_norm:
                status = "OK (Fuzzy)"
            else:
                status = "DIFF"
                issues.append(f"Part {i}: Content Diff")
                
        print(f"{i:02d}    | {status}")
        if status == "DIFF":
            print(f"       PDF: ...{pdf_last_line[-60:]}")
            print(f"       MD : ...{md_last_line[-60:]}")

    print("\nSummary:")
    if issues:
        print(f"Found {len(issues)} issues.")
    else:
        print("All parts verified successfully!")

if __name__ == "__main__":
    verify_parts()
