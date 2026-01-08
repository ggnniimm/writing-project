import sys
import re
from pypdf import PdfReader

def find_page_by_regex(pdf_path, regex_pattern):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"Total Pages: {total_pages}")
    
    found = False
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if re.search(regex_pattern, text):
            print(f"Found Pattern '{regex_pattern}' on Page Index: {i} (Page Label ~ {i+1})")
            # Print a snippet
            match = re.search(regex_pattern, text)
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 20)
            print(f"Snippet: {text[start:end]}")
            found = True
            
    if not found:
        print(f"Pattern '{regex_pattern}' NOT FOUND")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python find_text_page.py <pdf> <regex>")
        sys.exit(1)
        
    find_page_by_regex(sys.argv[1], sys.argv[2])
