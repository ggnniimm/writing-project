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
        if re.search(r'[ก-ฮ]', line):
            matches = re.finditer(r'[0-9]+', line)
            for m in matches:
                # Filter out likely superscripts (footnotes) if they are 1-2 digits
                # But strictly speaking, the prompt says "Thai Court Rulings use Thai numerals".
                # Superscripts in HTML are text.
                # If the regex matches inside <sup>...</sup>, we might want to allow it IF the user accepts Arabic for footnotes.
                # However, usually footnotes in Thai texts are also Thai numerals.
                # Let's flag everything for now.
                issues.append(f"⚠️  Line {i+1}: Arabic numeral '{m.group()}' found in Thai context.")
                if len(issues) >= 10:
                    issues.append("... (too many numeral errors, stopping check)")
                    return issues
    return issues

def check_footnotes(md_content):
    """
    Verifies footnote completeness and correctness.
    1. Finds all references `<sup>X</sup>`.
    2. Finds all definitions starting with `<sup>X</sup>`.
    3. Checks sequence and pairing.
    """
    issues = []
    
    # 1. Normalize numbers in superscripts to integers
    # Regex for <sup> 1 </sup>, <sup>๑</sup>, etc.
    # We will convert Thai digits to Arabic for logic check
    
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    trans = str.maketrans(thai_digits, arabic_digits)
    
    def to_int(s):
        s = s.translate(trans)
        try:
            return int(s)
        except:
            return None

    # Find References
    # Pattern: <sup>(digits)</sup>
    ref_matches = []
    for m in re.finditer(r'<sup>\s*([0-9๐-๙]+)\s*</sup>', md_content):
        val = to_int(m.group(1))
        if val is not None:
            ref_matches.append(val)
    
    # Find Definitions
    # Pattern: Start of line (ignoring whitespace), <sup>(digits)</sup>
    # Or common fallback: * (digits) or just (digits) if prompt failed slightly
    def_matches = []
    lines = md_content.splitlines()
    for i, line in enumerate(lines):
        # Strict check based on new prompt rules
        m = re.match(r'^\s*<sup>\s*([0-9๐-๙]+)\s*</sup>', line)
        if m:
            val = to_int(m.group(1))
            if val is not None:
                def_matches.append(val)
                
    # Sort
    refs = sorted(list(set(ref_matches)))
    defs = sorted(list(set(def_matches)))
    
    # CHECK 1: Sequence
    if refs:
        full_seq = list(range(refs[0], refs[-1] + 1))
        missing_refs = [x for x in full_seq if x not in refs]
        if missing_refs:
            issues.append(f"❌ GAP in Footnote References: Missing {missing_refs}")
    
    if defs:
        full_seq_defs = list(range(defs[0], defs[-1] + 1))
        missing_defs = [x for x in full_seq_defs if x not in defs]
        if missing_defs:
            issues.append(f"❌ GAP in Footnote Definitions: Missing {missing_defs}")

    # CHECK 2: Pairing
    # Refs without Defs
    orphan_refs = [x for x in refs if x not in defs]
    if orphan_refs:
        issues.append(f"❌ References without Definitions: {orphan_refs}")
        
    # Defs without Refs
    orphan_defs = [x for x in defs if x not in refs]
    if orphan_defs:
        issues.append(f"❌ Definitions without References: {orphan_defs}")

    if not refs and not defs:
        issues.append("ℹ️  No footnotes found.")
        
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
        print("✅ Numeral Validation Passed.")

    # 2. Footnote Check
    fn_issues = check_footnotes(md_content)
    if fn_issues:
        print("\nFn Footnote Validation Issues:")
        for issue in fn_issues:
            print(issue)
    else:
        print("✅ Footnote Validation Passed (Sequence & Pairing correct).")

    ratio = None
    jaccard = None
    len_md = 0
    len_pdf = 0

    # 3. PDF Comparison (if provided)
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
    
    print("\n✅ Verification Complete.")
    
    # Summary for Agent Reporting
    print("\n" + "="*40)
    print("📋 REPORT SUMMARY (COPY THIS TO USER)")
    print("="*40)
    if pdf_path and ratio is not None: 
        print(f"File: {os.path.basename(md_path)}")
        print(f"Stats: Ratio={ratio:.2f} (MD: {len_md} / PDF: {len_pdf} chars)")
        if jaccard is not None:
            print(f"Jaccard: {jaccard:.2f}")
    if fn_issues:
        print(f"Footnotes: ⚠️ Found {len(fn_issues)} issues")
    else:
        print("Footnotes: ✅ Clean")
    print("="*40 + "\n")

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
