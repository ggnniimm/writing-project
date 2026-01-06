import os
import subprocess
import glob
import time
import shutil
import sys

# Volume 7 has 58 parts
PARTS_TO_FIX = list(range(1, 59)) 

BASE_DIR = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project"
SCRIPT_PATH = os.path.join(BASE_DIR, "scripts/gemini_pdf_to_md.py")
PDF_DIR = os.path.join(BASE_DIR, "etc/split_vol07")
# gemini_pdf_to_md.py outputs to 'references' in CWD usually, 
# but let's check recursively in the project root's references just in case.
REF_DIR = os.path.join(BASE_DIR, "references")

def get_newest_recursive(root_dir):
    # Find all .md files recursively
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".md"):
                all_files.append(os.path.join(root, f))
                
    if not all_files:
        return None
    return max(all_files, key=os.path.getctime)

def fix_part(part_num):
    print(f"\n♻️  Extracting Part {part_num}...")
    pdf_file = os.path.join(PDF_DIR, f"part_{part_num:02d}.pdf")
    target_md = os.path.join(PDF_DIR, f"part_{part_num:02d}.md")
    
    if not os.path.exists(pdf_file):
        print(f"❌ PDF not found: {pdf_file}")
        return

    # Check if MD already exists
    if os.path.exists(target_md):
        print(f"⏭️  Part {part_num} already exists. Skipping.")
        return

    start_time = time.time()
    
    # Run, inheriting stdout/stderr
    try:
        # Pass both input PDF and output MD path
        cmd = ["python3", SCRIPT_PATH, pdf_file, target_md]
        subprocess.run(cmd, timeout=300) 
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout extracting Part {part_num}. Skipping...")
        return 
    
    # Verify file existed
    if os.path.exists(target_md):
        print(f"✅ Verified: part_{part_num:02d}.md created successfully.")
    else:
        print(f"❌ Failed to create output for Part {part_num}")

def main():
    print(f"🛠  Starting Batch Extraction for Volume 7 ({len(PARTS_TO_FIX)} parts)...")
    
    # Verify REF_DIR exists
    if not os.path.exists(REF_DIR):
        os.makedirs(REF_DIR)

    for part in PARTS_TO_FIX:
        fix_part(part)
        time.sleep(5) # Cooldown
        
    print("\n✨ Volume 7 Batch Extraction Complete!")

if __name__ == "__main__":
    main()
