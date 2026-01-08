
import os
import re

def check_files():
    base_path = '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07'
    
    # Range 45 to 58
    files_to_check = [f'part_{i:02d}.md' for i in range(45, 59)]
    
    results = {}
    
    for filename in files_to_check:
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath):
            results[filename] = "File not found"
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        has_header_pattern = re.search(r'(?:^\s*[๐-๙]+\s+แนวคำวินิจฉัยของศาลปกครอง|^\s*แนวคำวินิจฉัยของศาลปกครอง\s+[๐-๙]+)', content, re.MULTILINE)
        has_footer_pattern = "TRUST ศาลปกครองแห่งความเชื่อมั่น" in content or "ศาลปกครองแห่งความเชื่อมั่น TRUST" in content
        
        status = []
        if not has_header_pattern:
            status.append("Missing Header/Page Num")
        if not has_footer_pattern:
            status.append("Missing Footer")
            
        if not status:
            results[filename] = "OK"
        else:
            results[filename] = ", ".join(status)
            
    for filename, status in results.items():
        print(f"{filename}: {status}")

if __name__ == "__main__":
    check_files()
