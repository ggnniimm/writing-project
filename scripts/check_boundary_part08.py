
import os
from pypdf import PdfReader

def get_text_from_pdf(pdf_path, page_index):
    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) <= page_index:
            return f"[Error: Page {page_index} out of bounds, max {len(reader.pages)-1}]"
        page = reader.pages[page_index]
        return page.extract_text()
    except Exception as e:
        return f"[Error reading {pdf_path}: {e}]"

def analyze_boundary():
    base_dir = "etc/Academic_230317_084750-2_parts"
    
    parts = [7, 8, 9]
    
    for i in range(len(parts) - 1):
        curr_num = parts[i]
        next_num = parts[i+1]
        
        curr_pdf = os.path.join(base_dir, f"part_{curr_num:02d}.pdf")
        next_pdf = os.path.join(base_dir, f"part_{next_num:02d}.pdf")
        
        print(f"--- Boundary: Part {curr_num} (End) -> Part {next_num} (Start) ---")
        
        # Get last page of current
        reader = PdfReader(curr_pdf)
        last_page_idx = len(reader.pages) - 1
        text_end = reader.pages[last_page_idx].extract_text()
        lines_end = text_end.splitlines()
        last_few = "\n".join(lines_end[-5:]) if lines_end else "[Empty]"
        
        # Get first page of next
        reader_next = PdfReader(next_pdf)
        text_start = reader_next.pages[0].extract_text()
        lines_start = text_start.splitlines()
        first_few = "\n".join(lines_start[:5]) if lines_start else "[Empty]"
        
        print(f"[{curr_num} END]:\n{last_few}")
        print("-" * 20)
        print(f"[{next_num} START]:\n{first_few}")
        print("=" * 40)

if __name__ == "__main__":
    analyze_boundary()
