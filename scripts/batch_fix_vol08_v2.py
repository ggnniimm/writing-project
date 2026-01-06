import os
import subprocess
import glob
import time
import shutil

# Remaining parts to fix (Removed 41 and 55 which are handled)
PARTS_TO_FIX = [42, 43, 45, 49, 52, 53, 54, 55]
BASE_DIR = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project"
SCRIPT_PATH = os.path.join(BASE_DIR, "scripts/gemini_pdf_to_md.py")
PDF_DIR = os.path.join(BASE_DIR, "etc/split_vol08")
# Look everywhere in references
REF_DIR = os.path.join(BASE_DIR, "scripts/references")

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
    print(f"\n♻️  Re-extracting Part {part_num}...")
    pdf_file = os.path.join(PDF_DIR, f"part_{part_num:02d}.pdf")
    target_md = os.path.join(PDF_DIR, f"part_{part_num:02d}.md")
    
    start_time = time.time()
    
    # Run, inheriting stdout/stderr
    try:
        # Run with timeout to prevent hanging on stream API issues
        cmd = ["python3", SCRIPT_PATH, pdf_file]
        subprocess.run(cmd, timeout=180) 
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout extracting Part {part_num}. Skipping...")
        return 
    
    time.sleep(2)

    # Check if PDF was renamed (Side-effect of gemini_pdf_to_md.py)
    if not os.path.exists(pdf_file):
        # Look for ref_sac_*.pdf or similar in the same dir
        renamed_pdfs = glob.glob(os.path.join(PDF_DIR, "ref_sac_*.pdf"))
        if renamed_pdfs:
            # Assume the newest one is ours (or just the only one if consistent)
            renamed_pdf = max(renamed_pdfs, key=os.path.getctime)
            print(f"⚠️  PDF was renamed to {os.path.basename(renamed_pdf)}. Restoring...")
            shutil.move(renamed_pdf, pdf_file)
    
    new_file = get_newest_recursive(REF_DIR)
    
    if new_file and os.path.getmtime(new_file) > start_time:
        print(f"✅ Found output: {new_file}")
        shutil.move(new_file, target_md)
        print(f"📦 Restored to: part_{part_num:02d}.md")
    else:
        print(f"❌ Failed to locate new output for Part {part_num}")

def main():
    print(f"🛠  Starting Batch Fix V2 for {len(PARTS_TO_FIX)} parts...")
    for part in PARTS_TO_FIX:
        fix_part(part)
        time.sleep(5) # Cooldown
        
    print("\n✨ Batch Fix V2 Complete!")

if __name__ == "__main__":
    main()
