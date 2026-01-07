import re

def clean_extract(text):
    # Standard cleanup for Gemini extraction noise if any
    text = text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("\n", 1)[0]
    return text

def main():
    md_path = 'etc/split_vol07/part_09.md'
    extract_path = 'etc/split_vol07/extract_09_missing.md'
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    with open(extract_path, 'r', encoding='utf-8') as f:
        new_content = f.read()
        
    new_content = clean_extract(new_content)
    
    # We found the split point at "แต่ต่อมาผู้ถูกฟ้องคดีได้มีหนังสือ"
    # But wait, looking at the previous analysis...
    # The file ends:
    # "...ศาลปกครองแห่งความเชื่อมั่น TRUST"
    # This junk footer is actually masking the fact that content stopped BEFORE it.
    
    # Let's look for the last valid sentence fragment we saw in the tail.
    # "...เพื่อใช้ในการจัดทำบริการสาธารณะ แต่ต่อมาผู้ถูกฟ้องคดีได้มีหนังสือ"
    # This phrase is where the PDF slice STARTED.
    
    # So we need to:
    # 1. Find this phrase in the ORIGINAL markdown.
    # 2. Cut the original markdown right BEFORE this phrase (or just replace from it).
    # 3. Append the new extracted content (which starts with this phrase).
    
    anchor = "แต่ต่อมาผู้ถูกฟ้องคดีได้มีหนังสือ"
    
    idx = md_content.find(anchor)
    if idx == -1:
        # Maybe the MD file ends differently?
        # Let's try a shorter anchor.
        anchor = "เพื่อใช้ในการจัดทำบริการสาธารณะ"
        idx = md_content.find(anchor)
        
    if idx == -1:
        print("❌ Anchor not found!")
        return
        
    print(f"Found anchor at index {idx}")
    print(f"Context: {md_content[idx:idx+50]}...")
    
    # We want to keep everything UP TO the start of the anchor?
    # No, the extracted PDF started with the page containing the anchor.
    # So the extracted MD will likely contain the anchor text at the beginning too.
    
    # Let's see what the new content looks like.
    # (We assume it starts with the text on that page).
    
    # Prune MD to just before the anchor line?
    # Actually, let's verify if the new content replicates the anchor.
    # If yes, we cut MD before anchor.
    
    # But wait, the previous tail showed:
    # "แต่ต่อมาผู้ถูกฟ้องคดีได้มีหนังสือ\nศาลปกครองแห่งความเชื่อมั่น\nTRUST"
    # So the MD file HAS the anchor, but then cuts to footer.
    
    # So we cut MD *at* the anchor index.
    truncated_md = md_content[:idx]
    
    # And we append the new content.
    # But does the new content start with the anchor?
    # We should normalize to avoid duplication.
    
    # Let's just strip the anchor from the START of new_content if it exists?
    # Or rely on visual check.
    
    final_md = truncated_md + new_content
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(final_md)
        
    print(f"✅ Merged content. New size: {len(final_md)}")

if __name__ == "__main__":
    main()
