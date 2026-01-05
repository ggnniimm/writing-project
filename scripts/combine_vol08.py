
import os
import glob
import re

def combine_vol08():
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "etc", "split_vol08")
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "references", "court_rulings_books", "administrative_court_rulings_vol_08.md")
    
    print(f"Combining Markdown files from {base_dir}...")
    
    # Get all part_*.md files
    md_files = sorted(glob.glob(os.path.join(base_dir, "part_*.md")))
    
    if not md_files:
        print("❌ No markdown files found.")
        return

    combined_content = ""
    
    for md_file in md_files:
        print(f"Reading {os.path.basename(md_file)}...")
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            combined_content += f"\n\n<!-- DEBUG: Start of {os.path.basename(md_file)} -->\n\n"
            combined_content += content
            combined_content += f"\n\n<!-- DEBUG: End of {os.path.basename(md_file)} -->\n\n"

    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined_content)
    
    print(f"✅ Combined {len(md_files)} files into {output_path}")
    print(f"Total size: {os.path.getsize(output_path) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    combine_vol08()
