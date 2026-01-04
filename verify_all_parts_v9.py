import os
import glob
import re
import pdfplumber
import unicodedata

# Config
parts_dir = "etc/Academic_281019_141643_parts"
total_parts = 49
base_name = "Academic_281019_141643_part"

def normalize_text(text):
    if not text: return ""
    # Normalizing Thai PUA characters
    pua_map = {
        '\uf70a': '่', '\uf70b': '้', '\uf70c': '๊', '\uf70d': '๋', '\uf70e': '์',
        '\uf701': '่', '\uf702': '้', '\uf703': '๊', '\uf704': '๋',
        '\uf710': '่', '\uf711': '้', '\uf712': '็', # Corrected \uf712 to ็
        '\uf713': '๊', '\uf714': '๋', '\uf715': '์',
        '\uf705': '่', '\uf706': '้', '\uf707': '๊', '\uf708': '๋', '\uf709': '์'
    }
    for pua, std in pua_map.items():
        text = text.replace(pua, std)
        
    # Standardize SARA AM variations
    text = text.replace('าํ', 'ำ')
    text = text.replace('ำ', 'ำ') # Ensuring consistent ำ
    
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\s+', '', text)
    return text

def is_footer(line):
    line = normalize_text(line)
    # Check for keywords in normalized content
    keywords = [
        normalize_text("สายด่วนศาลปกครอง ๑๓๕๕"),
        normalize_text("ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน"),
        "TRUST"
    ]
    for k in keywords:
        if k in line: return True
    return False

def verify_parts():
    print(f"{'Part':<5} | {'ASCII Digits':<12} | {'Status':<50}")
    print("-" * 75)
    
    issues = []
    
    for i in range(1, total_parts + 1):
        md_file = os.path.join(parts_dir, f"{base_name}_{i:02d}.md")
        pdf_file = os.path.join(parts_dir, f"{base_name}_{i:02d}.pdf")
        
        if not os.path.exists(md_file):
            print(f"{i:02d}    | MISSING MD File")
            issues.append(f"Part {i}: Missing MD")
            continue
            
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Check ASCII digits
        ascii_digits = re.findall(r'[0-9]', content)
        ascii_status = f"FOUND {len(set(ascii_digits))}" if ascii_digits else "CLEAN"
        if ascii_digits:
            issues.append(f"Part {i}: Found ASCII digits {set(ascii_digits)}")

        # 2. Check end of content match
        pdf_last_line = ""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                if pdf.pages:
                    text = pdf.pages[-1].extract_text() or ""
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    valid_lines = [l for l in lines if not is_footer(l)]
                    if valid_lines:
                        pdf_last_line = valid_lines[-1]
        except Exception as e:
            pdf_last_line = f"ERROR: {e}"

        md_last_line = ""
        try:
            lines = [l.strip() for l in content.split('\n') if l.strip()]
            valid_lines = [l for l in lines if not is_footer(l)]
            if valid_lines:
                md_last_line = valid_lines[-1]
        except Exception as e:
             md_last_line = f"ERROR: {e}"
             
        p_norm = normalize_text(pdf_last_line)[-50:]
        m_norm = normalize_text(md_last_line)[-50:]
        
        status = "OK"
        if p_norm != m_norm:
            if p_norm in m_norm or m_norm in p_norm:
                status = "OK (Fuzzy)"
            else:
                status = "DIFF"
                issues.append(f"Part {i}: Content Diff at end")
                
        print(f"{i:02d}    | {ascii_status:<12} | {status}")

    print("\nSummary:")
    if issues:
        print(f"Found {len(issues)} potential issues.")
        for iss in issues[:10]: # Print first 10
            print(f" - {iss}")
        if len(issues) > 10: print("   ...")
    else:
        print("All parts verified successfully (basic check)!")

if __name__ == "__main__":
    verify_parts()
