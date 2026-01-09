
import os
import sys
import re

def verify_extraction_completeness(base_dir, total_parts):
    print(f"🔍 Verifying {total_parts} parts in {base_dir}...")
    
    missing_files = []
    empty_files = []
    valid_files = 0
    
    for i in range(1, total_parts + 1):
        filename = f"part_{i:02d}.md"
        filepath = os.path.join(base_dir, filename)
        
        if not os.path.exists(filepath):
            missing_files.append(filename)
            continue
            
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            empty_files.append(filename)
            continue
            
        # Optional: check for basic Thai content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(100)
            if not content.strip():
                empty_files.append(filename)
                continue
                
        valid_files += 1
        
    print(f"✅ Valid Files: {valid_files}/{total_parts}")
    
    if missing_files:
        print(f"❌ Missing Files ({len(missing_files)}): {missing_files}")
    else:
        print("✨ No missing files.")
        
    if empty_files:
        print(f"⚠️ Empty/Invalid Files ({len(empty_files)}): {empty_files}")
    else:
        print("✨ No empty files.")
        
    return len(missing_files) == 0 and len(empty_files) == 0

if __name__ == "__main__":
    base_dir = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_230317_084750-2_parts"
    total_parts = 87
    
    success = verify_extraction_completeness(base_dir, total_parts)
    
    if not success:
        sys.exit(1)
    else:
        print("🎉 Verification Successful!")
