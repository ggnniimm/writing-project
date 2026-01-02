#!/usr/bin/env python3
"""
Combine all extracted parts in order and create final file
"""

import os
import glob

def combine_parts():
    parts_dir = "etc/Academic_280125_142653_parts"
    
    # Get all MD files in order
    md_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_280125_142653_part_*.md")))
    
    print(f"Found {len(md_files)} parts to combine")
    
    combined_content = ""
    
    for md_file in md_files:
        part_name = os.path.basename(md_file)
        print(f"  Adding {part_name}...")
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_content += content + "\n\n"
    
    # Save combined file
    output_file = os.path.join(parts_dir, "Academic_280125_142653_hybrid.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    # Stats
    lines = len(combined_content.splitlines())
    size_mb = len(combined_content) / (1024 * 1024)
    
    print(f"\n✅ Combined file created: {output_file}")
    print(f"   Lines: {lines:,}")
    print(f"   Size: {size_mb:.2f} MB")
    
    return output_file

if __name__ == "__main__":
    combine_parts()
