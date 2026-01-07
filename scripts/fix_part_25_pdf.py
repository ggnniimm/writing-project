
from pypdf import PdfReader, PdfWriter
import os

def extract_part_25():
    source = "raw_pdfs/Academic_230317_084750-2.pdf"
    output = "etc/split_vol07/part_25.pdf"
    
    # Physical indices (0-based) for pages 486 to 506
    # Page 486 is index 485.
    # Page 506 is index 505.
    start_index = 485
    end_index = 506 # inclusive 506 physically? End range is exclusive in range(), so 506 covers up to index 505.
    
    # Wait, check logic:
    # 486 (phys) -> index 485.
    # 506 (phys) -> index 505.
    # range(485, 506) -> 485, ..., 505. Correct.
    
    reader = PdfReader(source)
    writer = PdfWriter()
    
    print(f"Extracting pages {start_index+1} to {end_index} (Physical)...")
    
    for i in range(start_index, end_index):
        writer.add_page(reader.pages[i])

    with open(output, "wb") as f:
        writer.write(f)
    print(f"Created {output}")

extract_part_25()
