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
    extract_path = 'etc/split_vol07/extract_09_gap.md'
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    with open(extract_path, 'r', encoding='utf-8') as f:
        new_content = f.read()
        
    new_content = clean_extract(new_content)
    
    # We need to insert this content AFTER Page 131.
    # Page 131 ends with... let's check Page 134 header.
    # In file, we saw:
    # 170:แนวคำวินิจฉัยของศาลปกครอง ๑๓๑
    # ... content of 131 ...
    # 204:๑๓๔ แนวคำวินิจฉัยของศาลปกครอง
    
    # We want to insert validly between 131 and 134.
    # The extraction presumably includes "๑๓๒..." and "๑๓๓..." headers.
    
    # Find the start of Page 134
    anchor_134 = "๑๓๔ แนวคำวินิจฉัยของศาลปกครอง"
    idx_134 = md_content.find(anchor_134)
    
    if idx_134 == -1:
        print("❌ Anchor 134 not found!")
        return
        
    # We insert BEFORE Page 134.
    # Ensure newline separation
    upper_part = md_content[:idx_134]
    lower_part = md_content[idx_134:]
    
    final_md = upper_part + "\n" + new_content + "\n\n" + lower_part
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(final_md)
        
    print(f"✅ Inserted missing pages. New size: {len(final_md)}")

if __name__ == "__main__":
    main()
