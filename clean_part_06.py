import re

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    
    # Pattern for Header: Any combo of Thai num and Title
    # Note: PDF extraction might have \f at start
    # Title: แนวคําวินิจฉัยของศาลปกครอง (Check encoding variations)
    
    # Pattern for Footer: ศาลปกครองแห่งความเชื่อมั่น
    
    # Footnote Def Pattern: Indented Number alone on line? 
    # In the view I saw:
    # 59:             ๓๖
    # 60:               พระราชบัญญัติ...
    # So the number is on its own line?
    
    # Let's verify patterns by printing matching lines first
    
    for i, line in enumerate(lines):
        # Remove Form Feed
        line = line.replace('\x0c', '')
        
        # Remove Footer
        if 'ศาลปกครองแหงความเชื่อมั่น' in line or 'ศาลปกครองแห่งความเชื่อมั่น' in line:
            continue
            
        # Normalize Header
        if 'แนวคําวินิจฉัยของศาลปกครอง' in line or 'แนวคำวินิจฉัยของศาลปกครอง' in line:
            # Extract number
            nums = re.findall(r'[๐-๙]+', line)
            if nums:
                page_num = nums[-1] if 'แนว' in line else nums[0] 
                # If "84 Title", num is first. If "Title 85", num is last.
                # Actually just find the number and the text.
                # Standardize to: แนวคำวินิจฉัยของศาลปกครอง [Num]
                new_lines.append(f'แนวคำวินิจฉัยของศาลปกครอง {page_num}\n')
                continue
        
        new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

clean_file('/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_310717_154727-2_parts/part_06.md')
