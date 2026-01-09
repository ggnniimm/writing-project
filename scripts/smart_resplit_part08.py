
import os
from pypdf import PdfReader, PdfWriter
import difflib

def get_page_text(pdf_path, page_num):
    reader = PdfReader(pdf_path)
    if page_num < len(reader.pages):
        return reader.pages[page_num].extract_text()
    return ""

def smart_resplit():
    base_dir = "etc/Academic_230317_084750-2_parts"
    source_pdf = "raw_pdfs/Academic_230317_084750-2.pdf"
    
    # Target parts relative to 08
    prev_pdf = os.path.join(base_dir, "part_07.pdf")
    next_pdf = os.path.join(base_dir, "part_09.pdf")
    new_part08_path = os.path.join(base_dir, "part_08.pdf")
    
    # 1. Identify "signatures" of End of 07 and Start of 09
    print("🔍 Analyzing boundaries...")
    
    # Last page of Part 07
    reader_prev = PdfReader(prev_pdf)
    prev_pages_count = len(reader_prev.pages)
    last_text_07 = reader_prev.pages[-1].extract_text().replace("\n", "").strip()[-100:]
    print(f"Part 07 ends with: ...{last_text_07}")

    # First page of Part 09
    reader_next = PdfReader(next_pdf)
    # next_pages_count = len(reader_next.pages)
    first_text_09 = reader_next.pages[0].extract_text().replace("\n", "").strip()[:100]
    print(f"Part 09 starts with: {first_text_09}...")

    # 2. Find these pages in the Source PDF
    print("📖 Scanning source PDF for match...")
    reader_source = PdfReader(source_pdf)
    total_pages = len(reader_source.pages)
    
    start_index = -1
    end_index = -1
    
    # Search for Part 07 End
    # We expect it around page 140 (7 * 20)
    search_window_start = 120
    search_window_end = 160
    
    for i in range(search_window_start, min(search_window_end, total_pages)):
        text = reader_source.pages[i].extract_text().replace("\n", "").strip()
        if last_text_07 in text:
            start_index = i + 1 # Next page is start of 08
            print(f"✅ Found Part 07 End at Source Page {i} (Index). So Part 08 starts at {start_index}.")
            break
            
    # Search for Part 09 Start
    # We expect it around page 160 (8 * 20)
    for i in range(search_window_start + 10, min(search_window_end + 30, total_pages)):
        text = reader_source.pages[i].extract_text().replace("\n", "").strip()
        if first_text_09 in text:
            end_index = i # This page IS start of 09, so 08 ends at i-1
            print(f"✅ Found Part 09 Start at Source Page {i} (Index). So Part 08 ends at {end_index}.")
            break
            
    if start_index != -1 and end_index != -1:
        print(f"✂️ Cutting Part 08 from Index {start_index} to {end_index} (Exclusive of end)...")
        
        writer = PdfWriter()
        for i in range(start_index, end_index):
            writer.add_page(reader_source.pages[i])
            
        with open(new_part08_path, "wb") as f:
            writer.write(f)
        print(f"🎉 Successfully created smart {new_part08_path}")
        print(f"   Pages included: {end_index - start_index}")
        
    else:
        print("❌ Could not verify boundaries exactly. Aborting smart split.")
        if start_index == -1: print("   Missed Part 07 End match.")
        if end_index == -1: print("   Missed Part 09 Start match.")

if __name__ == "__main__":
    smart_resplit()
