import os
import subprocess
import glob
import time
import shutil

PARTS_TO_FIX = [54, 41, 42, 43, 45, 49, 52, 53]
BASE_DIR = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project"
SCRIPT_PATH = os.path.join(BASE_DIR, "scripts/gemini_pdf_to_md.py")
PDF_DIR = os.path.join(BASE_DIR, "etc/split_vol08")
MD_OUTPUT_DIR = os.path.join(BASE_DIR, "scripts/references/rulings_court")

def get_newest_file(dir_path):
    files = glob.glob(os.path.join(dir_path, "*.md"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def fix_part(part_num):
    print(f"\n♻️  Re-extracting Part {part_num}...")
    pdf_file = os.path.join(PDF_DIR, f"part_{part_num:02d}.pdf")
    target_md = os.path.join(PDF_DIR, f"part_{part_num:02d}.md")
    
    # Record time before run to identify new files
    start_time = time.time()
    
    # Run extraction
    cmd = ["python3", SCRIPT_PATH, pdf_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Error extracting Part {part_num}: {result.stderr}")
        return
        
    # Find the output file
    # The script dumps into scripts/references/rulings_court usually
    # We look for files modified *after* start_time
    time.sleep(1) # Ensure stats update
    
    new_file = get_newest_file(MD_OUTPUT_DIR)
    
    if new_file and os.path.getmtime(new_file) > start_time:
        print(f"✅ Extracted to: {os.path.basename(new_file)}")
        # Move to target
        shutil.move(new_file, target_md)
        print(f"📦 Restored to: part_{part_num:02d}.md (Size: {os.path.getsize(target_md) // 1024} KB)")
    else:
        print(f"❌ Check Failed: No new file found for Part {part_num}")

def main():
    print(f"🛠  Starting Batch Fix for {len(PARTS_TO_FIX)} parts...")
    for part in PARTS_TO_FIX:
        fix_part(part)
        time.sleep(2) # Cooldown
        
    print("\n✨ Batch Fix Complete!")

if __name__ == "__main__":
    main()
