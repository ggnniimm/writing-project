import os
import glob
import re

def combine_parts():
    parts_dir = "etc/Academic_291121_112321_parts"
    
    # Custom sort to handle part numbers correctly (part_2 vs part_10)
    # The default alphanumeric sort might do 1, 10, 11... 2. 
    # But usually 'part_01', 'part_10' works with standard sort if zero-padded.
    # The files are named part_01, part_02, so simple sort works.
    
    md_files = sorted(glob.glob(os.path.join(parts_dir, "Academic_291121_112321_part_*.md")))
    
    print(f"Found {len(md_files)} parts to combine")
    
    combined_content = ""
    
    for md_file in md_files:
        part_name = os.path.basename(md_file)
        # print(f"  Adding {part_name}...", end='\r')
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            combined_content += content + "\n\n"
            
    # Save combined file
    output_dir = "references/court_rulings_books"
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    output_file = os.path.join(output_dir, "administrative_court_rulings_vol_11.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_content)
    
    # Stats
    lines = len(combined_content.splitlines())
    size_mb = len(combined_content) / (1024 * 1024)
    
    print(f"\n✅ Combined file created: {output_file}")
    print(f"   Lines: {lines:,}")
    print(f"   Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    combine_parts()
