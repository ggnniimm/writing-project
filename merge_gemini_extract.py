import re

def clean_extracted_text(text):
    # Remove Headers 
    # "๒๐๔ แนวคำวินิจฉัยของศาลปกครอง"
    text = re.sub(r'^\s*[๐-๙0-9]+\s+แนว.*วินิจฉัยของศาลปกครอง.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*แนว.*วินิจฉัยของศาลปกครอง\s+[๐-๙0-9]+.*$', '', text, flags=re.MULTILINE)
    
    # Remove Footers
    # "ศาลปกครองแห่งความเชื่อมั่น TRUST"
    text = re.sub(r'^.*ศาลปกครองแห่งความเชื่อมั่น.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^.*TRUST.*$', '', text, flags=re.MULTILINE)
    
    # Remove leading/trailing formatting structure
    text = text.strip()
    return text

def main():
    # Load current MD
    with open('etc/split_vol07/part_12.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    # Find the split point
    # "มายังศาลปกครองตามมาตรา ๑๐ วรรคหนึ่ง (๒) แห่งพระราชบัญญัติว่าด้วยการวินิจฉัยชี้ขาด"
    split_phrase = "แห่งพระราชบัญญัติว่าด้วยการวินิจฉัยชี้ขาด"
    
    idx = md_content.find(split_phrase)
    if idx == -1:
        print("❌ Could not find split phrase in part_12.md")
        return
        
    end_idx = idx + len(split_phrase)
    
    # Validation: Print valid content before split
    print(f"Split point found at char {end_idx}")
    print(f"Pre-split context: ...{md_content[end_idx-50:end_idx]}")
    
    # Truncate
    valid_upper_part = md_content[:end_idx]
    
    # Load Gemini extraction
    with open('etc/split_vol07/extract_204_205.md', 'r', encoding='utf-8') as f:
        new_extract = f.read()
        
    # Clean it
    cleaned_extract = clean_extracted_text(new_extract)
    
    # Check start of extract
    # Should start with "อำนาจหน้าที่ระหว่างศาล..."
    print(f"Cleaned extract start: {cleaned_extract[:50]}...")
    
    # Merge
    # Add a newline just in case
    final_content = valid_upper_part + "\n" + cleaned_extract
    
    with open('etc/split_vol07/part_12.md', 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print("✅ Successfully merged Gemini extraction into part_12.md")

if __name__ == "__main__":
    main()
