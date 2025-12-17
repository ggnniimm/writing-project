
import os
import re
import sys

# Import the logic function from our main script
# Assuming gemini_pdf_to_md is in the same directory
import gemini_pdf_to_md

REFERNECES_DIR = "references/rulings_court"

def rename_sac_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(base_dir, REFERNECES_DIR)
    
    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        return

    print(f"Scanning {target_dir}...")
    
    for filename in os.listdir(target_dir):
        if not filename.endswith(".md"):
            continue
            
        file_path = os.path.join(target_dir, filename)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # We need to prepend "ศาลปกครอง" if it's not detected, or rely on the function?
        # The function `determine_filename_and_path` checks `if "ศาลปกครอง" in content_sample`.
        # Existing SAC files should have it.
        
        new_name, _ = gemini_pdf_to_md.determine_filename_and_path(content)
        
        # determine_filename_and_path returns "ref_sac_unknown.md" if it fails.
        # We don't want to rename to unknown if we can't parse it better than before.
        if "unknown" in new_name:
            # Fallback: Check if filename matches ref_sac_(\d+)_(\d+)_full.md
            # If so, assume it is an appeal case and use "o_" prefix
            match_full = re.match(r"ref_sac_(\d+)_(\d+)_full\.md", filename)
            if match_full:
                n = match_full.group(1)
                y = match_full.group(2)
                new_name = f"ref_sac_o_{n}_{y}.md"
                print(f"⚠️  Content extraction failed for {filename}, but using filename fallback -> {new_name}")
            else:
                print(f"⚠️  Could not determine better name for {filename}. Skipping.")
                continue
            
        if new_name != filename:
            print(f"🔄 Renaming: {filename} -> {new_name}")
            
            # Rename MD
            new_path = os.path.join(target_dir, new_name)
            if os.path.exists(new_path) and new_name != filename: # Prevent overwriting if target exists (unless same file)
                 # Handle collision?
                 # If we are renaming "ref_sac_16_2547_full.md" -> "ref_sac_o_16_2547.md" and that already exists?
                 # Unlikely unless we ran it partially.
                 print(f"   ❌ Target {new_name} already exists! Skipping.")
                 continue
                 
            os.rename(file_path, new_path)
            
            # Rename PDF if exists
            pdf_old = filename.replace(".md", ".pdf")
            pdf_new = new_name.replace(".md", ".pdf")
            
            pdf_old_path = os.path.join(target_dir, pdf_old)
            pdf_new_path = os.path.join(target_dir, pdf_new)
            
            # Check parallel folder 'raw_pdfs' or same folder?
            # Usually PDFs might be in references/raw_pdfs or same folder. 
            # Looking at previous logs, determine_filename returns path.
            # But let's check local dir first.
            if os.path.exists(pdf_old_path):
                os.rename(pdf_old_path, pdf_new_path)
                print(f"   Also renamed PDF: {pdf_old} -> {pdf_new}")
                
        else:
            print(f"✅ {filename} is already correct.")

if __name__ == "__main__":
    rename_sac_files()
