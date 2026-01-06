import argparse
import os
import re
import sys
from pypdf import PdfReader

def normalize_text(text):
    """
    Normalizes text for comparison:
    - Removes whitespace
    - Removes punctuation
    - Converts Thai numerals to Arabic for content ratio check (to align with potential PDF extraction behavior which might vary)
      or keeps them if PDF extraction preserves them.
    Actually, let's keep it simple: Remove all whitespace and non-alphanumeric chars (keep Thai/English).
    """
    # Remove all whitespace
    text = re.sub(r'\s+', '', text)
    # Keep only Thai (U+0E00-U+0E7F) and English chars and numerals
    # Actually, pypdf extraction might be messy. strict alphanumeric might be too harsh.
    # Let's just strip whitespace.
    return text

def get_thai_tokens(text):
    """
    Splits text into rough tokens (words) is hard for Thai.
    Using n-grams (shingles) on characters is more robust for OCR comparison.
    """
    text = normalize_text(text)
    # create 4-grams
    n = 4
    return set(text[i:i+n] for i in range(len(text)-n+1))

def check_numerals(md_content):
    issues = []
    lines = md_content.splitlines()
    for i, line in enumerate(lines):
         # Skip likely English lines (e.g. headers, footer, or tables with English)
         # Heuristic: if line has Thai chars, it should use Thai numerals.
         if re.search(r'[ก-ฮ]', line):
             # Look for Arabic numerals 0-9
             # Exclude patterns like URLs, English references (e.g. v.1, 2024, etc)
             # This is a strict check as requested.
             
             # Find all matches
             matches = re.finditer(r'[0-9]+', line)
             for m in matches:
                 # Check context? For now, just flag it.
                 # Maybe ignore if it looks like a year "256x" and user allows it? 
                 # But user specifically asked for Thai numerals.
                 # Volume 7 usually uses Thai numerals for everything in the body.
                 
                 # Exception: "Page X" or similar if explicit.
                 # Exception: English words nearby?
                 
                 issues.append(f"⚠️  Line {i+1}: Arabic numeral '{m.group()}' found in Thai context.")
                 if len(issues) >= 10:
                     issues.append("... (too many numeral errors, stopping check)")
                     return issues
    return issues

def verify_content(md_path, pdf_path=None):
    print(f"🔍 Verifying: {os.path.basename(md_path)}")
    
    if not os.path.exists(md_path):
        print(f"❌ Error: Markdown file not found: {md_path}")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 1. Numeral Check
    num_issues = check_numerals(md_content)
    if num_issues:
        print("\n🔢 Numeral Validation Issues:")
        for issue in num_issues:
            print(issue)
    else:
        print("✅ Numeral Validation Passed (No misplaced Arabic numerals found).")

    # 2. PDF Comparison (if provided)
    if pdf_path and os.path.exists(pdf_path):
        print(f"\n📄 Comparing with PDF: {os.path.basename(pdf_path)}")
        try:
            reader = PdfReader(pdf_path)
            pdf_text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pdf_text += extracted
            
            # Simple Length Ratio
            norm_md = normalize_text(md_content)
            norm_pdf = normalize_text(pdf_text)
            
            len_md = len(norm_md)
            len_pdf = len(norm_pdf)
            
            if len_pdf == 0:
                print("⚠️  Warning: Could not extract text from PDF (it might be image-only without OCR layer). Comparison skipped.")
            else:
                ratio = len_md / len_pdf
                print(f"   - PDF Char Length: {len_pdf}")
                print(f"   - MD Char Length:  {len_md}")
                print(f"   - Ratio (MD/PDF):  {ratio:.2f}")
                
                if ratio < 0.8:
                    print("❌ Warning: Markdown significantly shorter than PDF text (< 80%). Content might be missing.")
                elif ratio > 1.2:
                    print("⚠️  Warning: Markdown significantly longer than PDF text (> 120%). Possible duplication or hallucination.")
                else:
                    print("✅ Length Ratio looks healthy (0.8 - 1.2).")
                
                # Jaccard Sim (Set Overlap)
                # Using 4-char shingles
                pdf_shingles = set(norm_pdf[i:i+4] for i in range(len(norm_pdf)-3))
                md_shingles = set(norm_md[i:i+4] for i in range(len(norm_md)-3))
                
                if not pdf_shingles:
                     print("⚠️  Warning: No text features extracted from PDF.")
                else:
                    intersection = pdf_shingles.intersection(md_shingles)
                    union = pdf_shingles.union(md_shingles)
                    jaccard = len(intersection) / len(union) if union else 0
                    
                    print(f"   - Content Overlap (Jaccard): {jaccard:.2f}")
                    if jaccard < 0.5:
                        print("❌ Low content overlap. Please check for hallucination or wrong file.")
                    elif jaccard > 0.8:
                        print("✅ High content overlap. Extraction looks accurate.")
                    else:
                        print("⚠️  Moderate content overlap. Worth a quick spot check.")

        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
    else:
        if pdf_path:
            print(f"⚠️  PDF path provided but not found: {pdf_path}")
        else:
            print("ℹ️  No PDF provided. Skipping detailed comparison.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Markdown content against PDF.")
    parser.add_argument("md_file", help="Path to the markdown file")
    parser.add_argument("pdf_file", nargs="?", help="Path to the source PDF file (optional)")
    
    args = parser.parse_args()
    
    pdf_path = args.pdf_file
    
    # Auto-infer PDF path if not provided
    if not pdf_path:
        # Check if there is a .pdf with same name in same dir
        base = os.path.splitext(args.md_file)[0]
        potential_pdf = base + ".pdf"
        if os.path.exists(potential_pdf):
            pdf_path = potential_pdf
            
    verify_content(args.md_file, pdf_path)
