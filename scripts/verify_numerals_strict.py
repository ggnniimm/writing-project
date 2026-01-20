import argparse
import os
import re
import sys
from pypdf import PdfReader
from difflib import SequenceMatcher

def normalize_text(text):
    """Normalize text by removing whitespace and zero-width chars."""
    return re.sub(r'\s+', '', text)

def get_pdf_text(pdf_path):
    """Extract text from PDF using pypdf."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def find_context_match(target_context, pdf_text_normalized, window_size=50):
    """
    Find best match for target_context in pdf_text_normalized.
    Returns the matching text snippet from PDF or None if no good match.
    """
    # Simple strict search first
    if target_context in pdf_text_normalized:
        return target_context
    
    # If not found, try fuzzy match (expensive for large text, so searching in chunks might be better)
    # But for now, let's rely on strict match of *smaller* anchors around the number.
    return None

def verify_numerals(md_path, pdf_path):
    print(f"🔍 Strict Numeral Verification: {os.path.basename(md_path)}")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_lines = f.readlines()
        
    pdf_text = get_pdf_text(pdf_path)
    if not pdf_text:
        print("❌ Failed to extract PDF text. Cannot verify.")
        return

    # Create a normalized version of PDF text for easier search (remove spaces/newlines)
    # But checking index alignment is hard.
    # Instead, let's keep it simple: normalize spaces to single space.
    pdf_text_clean = re.sub(r'\s+', ' ', pdf_text)
    
    issues_found = 0
    
    print("\n--------------------------------------------------")
    print("Checking for Arabic Numerals (0-9) in Thai Context")
    print("--------------------------------------------------")

    for line_idx, line in enumerate(md_lines):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Find all Arabic numerals
        matches = list(re.finditer(r'[0-9]+', line))
        
        for m in matches:
            num = m.group()
            start = m.start()
            end = m.end()
            
            # Context Extraction (approx 20 chars before and after)
            context_start = max(0, start - 30)
            context_end = min(len(line), end + 30)
            
            prefix = line[context_start:start].strip()
            suffix = line[end:context_end].strip()
            
            # Normalize context (remove all spaces for search)
            clean_prefix = re.sub(r'\s+', '', prefix)
            clean_suffix = re.sub(r'\s+', '', suffix)
            
            # Construct a regex pattern to find this context in PDF
            # Pattern: prefix + (any characters approx length of num) + suffix
            # Actually, we want to see what is *between* prefix and suffix in PDF.
            
            # Search in PDF
            # We look for the prefix, followed by some short text, followed by suffix
            # This is tricky because PDF might have line breaks.
            
            # Strategy: Find the prefix in PDF (normalized)
            # Then look ahead check.
            
            pdf_norm = re.sub(r'\s+', '', pdf_text)
            
            # Locate anchor (prefix + suffix) is risky if prefix/suffix are common.
            # Combine them: prefix + ??? + suffix
            
            search_pattern = re.escape(clean_prefix) + r'(.{1,10})' + re.escape(clean_suffix)
            
            match = re.search(search_pattern, pdf_norm)
            
            status = "❓ UNCHECKED"
            action = ""
            
            if match:
                found_val = match.group(1)
                
                # Check if found value is Thai numeral corresponding to the Arabic num
                thai_digits = "๐๑๒๓๔๕๖๗๘๙"
                arabic_digits = "0123456789"
                trans_to_arabic = str.maketrans(thai_digits, arabic_digits)
                
                found_val_as_arabic = found_val.translate(trans_to_arabic)
                
                if found_val == num:
                    # PDF has Arabic '5' and MD has '5' -> Match (But is it correct?)
                    # If user rule is "Thai Numerals Only", this is suspicious BUT correct to source.
                    status = "⚠️  MATCH (Arabic in PDF)"
                    action = "Check if PDF is OCR error or intent"
                elif found_val_as_arabic == num:
                    # PDF has Thai '๕' (or ๖ read as 5?) and MD has '5'
                    # Wait, if PDF has Thai '๕', we want MD to be '๕'.
                    # So MD '5' is WRONG format.
                    status = "❌ FORMAT MISMATCH"
                    action = f"AUTO-FIX: Change {num} -> {found_val}"
                    issues_found += 1
                elif num == '5' and found_val == '๖':
                    # Classic OCR Error case
                    status = "❌ VALUE MISMATCH (OCR Error)"
                    action = f"AUTO-FIX: Change 5 -> ๖ (PDF says ๖)"
                    issues_found += 1
                else:
                    status = f"❌ MISMATCH (PDF: {found_val})"
                    action = "Manual Check"
                    issues_found += 1
                    
                print(f"Line {line_idx+1}: Found '{num}' | Context: ...{prefix[-10:]} [?] {suffix[:10]}...")
                print(f"   -> PDF Match: '{found_val}'")
                print(f"   -> Status: {status}")
                if action:
                    print(f"   -> Action: {action}")
                print("-" * 30)
                
            else:
                # Context not found - might be due to line break in PDF splitting the context
                # or formatting differences.
                # Fallback: Just report it needs manual check
                print(f"Line {line_idx+1}: Found '{num}' | Context: ...{prefix} [?] {suffix}...")
                print("   -> Status: ❓ Context Not Found in PDF (Manual verify needed)")
                print("-" * 30)

    if issues_found == 0:
        print("\n✅ Strict Numeral Check Passed (No obvious mismatches in found contexts).")
    else:
        print(f"\n⚠️  Found {issues_found} strict numeral issues.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Strictly verify numerals against PDF text context.")
    parser.add_argument("md_file", help="Path to markdown file")
    parser.add_argument("pdf_file", help="Path to PDF file")
    
    args = parser.parse_args()
    
    verify_numerals(args.md_file, args.pdf_file)
