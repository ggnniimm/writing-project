
import os
import subprocess
import time
import sys

def reextract_parts():
    parts_to_extract = list(range(47, 58)) # 47 to 57 inclusive
    base_dir = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07"
    script_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/scripts/gemini_pdf_to_md.py"
    
    for part_num in parts_to_extract:
        pdf_name = f"part_{part_num:02d}.pdf"
        md_name = f"part_{part_num:02d}.md"
        pdf_path = os.path.join(base_dir, pdf_name)
        md_path = os.path.join(base_dir, md_name)
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF not found: {pdf_path}")
            continue
            
        print(f"🔄 Re-extracting Part {part_num}...")
        
        try:
            # Call the extraction script
            # python3 scripts/gemini_pdf_to_md.py <pdf_path> <output_path>
            cmd = [sys.executable, script_path, pdf_path, md_path]
            subprocess.run(cmd, check=True)
            print(f"✅ Finished Part {part_num}")
            
            # Use 'cat' to modify update time or just touch, but subprocess.run should have overwritten it
            
        except subprocess.CalledProcessError as e:
             print(f"❌ Failed to extract Part {part_num}: {e}")
        except Exception as e:
             print(f"❌ Unexpected error on Part {part_num}: {e}")
             
        # Small delay to be nice to API rate limits (though script handles it too)
        time.sleep(2)

if __name__ == "__main__":
    reextract_parts()
