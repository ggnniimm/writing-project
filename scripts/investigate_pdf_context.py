
from pypdf import PdfReader
import sys
import re

def investigate_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    print(f"Investigating {pdf_path} ({len(reader.pages)} pages)")
    
    # Contexts to look for
    contexts = [
        "พวกรวม", "กำหนด", "พัสดุระดับ",
        "ข้อ ๑ ของ", "แห่งประมวลกฎหมายแพ่ง",
        "มาตรา ๕๘" 
    ]
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"\n--- Page {i+1} ---")
        
        # Check for Arabic or Thai 5
        # We look for lines containing contexts
        lines = text.split('\n')
        for line in lines:
            # Check for our '5' contexts
            if "พวกรวม" in line or "หมู่" in line:
                 print(f"FOUND CONTEXT line: {line.strip()}")
            if "กำหนด" in line and "เดือน" in line:
                 print(f"FOUND CONTEXT line: {line.strip()}")
            if "พัสดุระดับ" in line:
                 print(f"FOUND CONTEXT line: {line.strip()}")

            # Check for footnote contexts
            if "ข้อ ๑ ของ" in line or "กฎกระทรวง" in line:
                 print(f"FOUND FOOTNOTE context: {line.strip()}")
            
            # General numeral check on line
            # Print lines with mixed Thai/Arabic if suspicious
            if re.search(r'\d', line) and re.search(r'[ก-๙]', line):
                 print(f"Line with Arabic numeral: {line.strip()}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        investigate_pdf(sys.argv[1])
    else:
        print("Usage: python investigate_pdf_context.py <pdf_path>")
