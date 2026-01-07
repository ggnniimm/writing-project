import re

def clean_thai_text(text):
    # Remove lines 1-4 and 36-38 roughly (headers/mid-page noise)
    # But better to just clean the string.
    
    # Remove header if present
    text = re.sub(r'^\s*?๒๐๔ แนวคาวินิจฉัยของศาลปกครอง', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*ศาลปกครองแห่งความเชื่อมั่น', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*.*แนวคาวินิจฉัยของศาลปกครอง ๒๐๕', '', text, flags=re.MULTILINE)
    
    # Normalize spaces: Remove spaces between Thai characters
    # Matches Thai followed by space followed by Thai
    text = re.sub(r'([ก-๙])\s+([ก-๙])', r'\1\2', text)
    # Again to handle wide spacing
    text = re.sub(r'([ก-๙])\s+([ก-๙])', r'\1\2', text)
    
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()

def main():
    # Read missing content
    with open('page_204_content.txt', 'r', encoding='utf-8') as f:
        missing_raw = f.read()
    
    missing_clean = clean_thai_text(missing_raw)
    
    # Read original MD
    with open('part_12_backup.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Construct new content
    # Lines are 0-indexed.
    # We want lines 0 to 613 (inclusive). MD line 613 is index 612.
    # MD content ends at line 613 with "วินิจฉัยชี้ขาด"
    
    # Check index 612 (Line 613)
    # It seems originally:
    # 613: มายังศาลปกครองตามมาตรา ๑๐ วรรคหนึ่ง (๒) แห่งพระราชบัญญัติว่าด้วยการวินิจฉัยชี้ขาด
    
    # We want up to index 612 (inclusive)
    
    upper_part = lines[:613] 
    
    # Middle part (Page 204)
    # Need to verify if missing_clean needs a newline prefix
    
    # Lower part
    # Start from Line 618 (user visible), so index 617.
    # 618: ผู้ฟ้องคดีจึงต้องนำคดีมาฟ้องต่อศาลภายในวันที่ ๒๗...
    # We skip 614, 615, 616, 617 (indices 613, 614, 615, 616).
    
    # Check index 617:
    # Should be "ผู้ฟ้องคดีจึงต้องนำคดีมาฟ้องต่อศาลภายในวันที่ ๒๗..."
    
    # And we STOP before the appended junk.
    # The appended junk started at line 650 (index 649).
    # But indices shifted? No, we are reading from backup which has the duplicate.
    # Wait, backup was made from current state (with duplication).
    # Current state has junk starting at line 650.
    # Line 649 is "ศาลปกครองแห่งความเชื่อมั่น TRUST\n"
    # Line 650 is "\n" or start of junk.
    
    # So we want lines[617:649] approximately.
    # Let's verify line 649 content.
    
    lower_part = lines[617:649]
    
    final_content = "".join(upper_part) + "\n" + missing_clean + "\n" + "".join(lower_part)
    
    with open('part_12.md', 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"Reconstructed part_12.md")
    print(f"Original lines: {len(lines)}")
    print(f"Inserted content length: {len(missing_clean)}")
    print(f"Upper part lines: {len(upper_part)}")
    print(f"Lower part lines: {len(lower_part)}")

if __name__ == "__main__":
    main()
