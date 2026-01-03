import os
import glob
import re

base_dir = "etc/Academic_281020_102051_parts"
output_file = "references/court_rulings_books/administrative_court_rulings_vol_10.md"

def combine_files():
    parts = sorted(glob.glob(os.path.join(base_dir, "Academic_281020_102051_part_*.md")))
    
    if not parts:
        print("No parts found!")
        return

    print(f"Combining {len(parts)} files...")
    
    # Ensure output dir exists
    out_dir = os.path.dirname(output_file)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for idx, part_file in enumerate(parts):
            print(f"Reading {os.path.basename(part_file)}...")
            with open(part_file, 'r', encoding='utf-8') as infile:
                content = infile.read()
                
                # OPTIONAL: Clean footers here or in separate pass?
                # Let's simple combine first, then we can run a cleaner.
                # Or just basic newline ensures.
                
                outfile.write(content)
                if idx < len(parts) - 1:
                    outfile.write("\n\n")
                    
    print(f"✅ Created {output_file}")

if __name__ == "__main__":
    combine_files()
