#!/usr/bin/env python3
"""
Split a PDF file into parts of maximum 20 pages each.
Usage: python3 split_pdf.py <input_pdf> [output_dir]
"""

import sys
import os
from pypdf import PdfReader, PdfWriter

def split_pdf(input_pdf, output_dir=None, max_pages=20):
    """
    Split a PDF into parts with maximum pages per part.
    
    Args:
        input_pdf: Path to input PDF file
        output_dir: Directory to save split PDFs (default: same as input)
        max_pages: Maximum pages per part (default: 20)
    
    Returns:
        List of output file paths
    """
    if not os.path.exists(input_pdf):
        print(f"❌ Error: File not found: {input_pdf}")
        return []
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(input_pdf))
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename
    base_name = os.path.splitext(os.path.basename(input_pdf))[0]
    
    # Read input PDF
    print(f"📖 Reading: {input_pdf}")
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    print(f"📄 Total pages: {total_pages}")
    
    # Calculate number of parts
    num_parts = (total_pages + max_pages - 1) // max_pages
    print(f"✂️  Splitting into {num_parts} parts (max {max_pages} pages each)")
    
    output_files = []
    
    # Split into parts
    for part_num in range(num_parts):
        start_page = part_num * max_pages
        end_page = min(start_page + max_pages, total_pages)
        
        # Create writer for this part
        writer = PdfWriter()
        
        # Add pages to this part
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        # Save this part
        output_filename = f"{base_name}_part_{part_num + 1:02d}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        output_files.append(output_path)
        print(f"  ✅ Part {part_num + 1:02d}: pages {start_page + 1}-{end_page} → {output_filename}")
    
    print(f"\n✨ Split complete! Created {len(output_files)} parts in: {output_dir}")
    return output_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 split_pdf.py <input_pdf> [output_dir]")
        print("Example: python3 split_pdf.py raw_pdfs/Academic_280125_142653.pdf etc/academic_parts")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    split_pdf(input_pdf, output_dir)
