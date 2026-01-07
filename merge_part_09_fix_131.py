import re

def clean_extract(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("\n", 1)[0]
    return text

def main():
    md_path = 'etc/split_vol07/part_09.md'
    extract_path = 'etc/split_vol07/extract_09_page131_133.md'
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    with open(extract_path, 'r', encoding='utf-8') as f:
        new_content = f.read()
        
    new_content = clean_extract(new_content)
    
    # We want to replace everything from Page 131 Header to Page 134 Header.
    # Current MD has Page 131 Header, then some content, then "No info".
    # And then the incorrectly inserted Pages 132/133 (from my previous attempt).
    # And then Page 134.
    
    # So we should just wipe clean between 131 and 134 and put the new 131-133 block.
    
    # Anchor Start: "แนวคำวินิจฉัยของศาลปกครอง ๑๓๑"
    # Actually, let's find the PREVIOUS page end to be safe?
    # No, finding Page 131 Header is fine.
    
    anchor_start_131 = "แนวคำวินิจฉัยของศาลปกครอง ๑๓๑"
    # Note: Header might be "๑๓๑ แนว..." or "แนว... ๑๓๑".
    # Previous check showed "แนวคำวินิจฉัยของศาลปกครอง ๑๓๑" (Step 765)
    
    # Anchor End: "๑๓๔ แนวคำวินิจฉัยของศาลปกครอง" (Step 641)
    anchor_end_134 = "๑๓๔ แนวคำวินิจฉัยของศาลปกครอง"
    
    idx_start = md_content.find(anchor_start_131)
    idx_end = md_content.find(anchor_end_134)
    
    if idx_start == -1:
        # Try alternate header format
        anchor_start_131 = "๑๓๑ แนวคำวินิจฉัยของศาลปกครอง"
        idx_start = md_content.find(anchor_start_131)
        
    if idx_start == -1:
        print("❌ Could not find Page 131 start.")
        return
        
    if idx_end == -1:
        print("❌ Could not find Page 134 start.")
        return
        
    print(f"Replacing range {idx_start} to {idx_end} ({idx_end - idx_start} chars)")
    
    # The new content likely HAS Page 131 header.
    # Let's check new content start.
    print(f"New content start: {new_content[:50]}...")
    
    # We replace from idx_start (inclusive) up to idx_end (exclusive).
    pre_part = md_content[:idx_start]
    post_part = md_content[idx_end:]
    
    final_md = pre_part + new_content + "\n\n" + post_part
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(final_md)
        
    print(f"✅ Replaced Pages 131-133 blocks. New size: {len(final_md)}")

if __name__ == "__main__":
    main()
