import re

input_file = "references/court_rulings_books/administrative_court_rulings_vol_10.md"

def clean_file():
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define patterns to remove
    patterns = [
        r"ข้อมูลฉับไว ไขข้อข้องใจ ใส่ใจประชาชน",
        r"สายด่วนศาลปกครอง ๑๓๕๕",
        r"สายด่วนศาลปกครอง 1355",
        r"TRUST and CONFIDENCE",
        r"www\.admincourt\.go\.th",
        r"^\s*-\s*Page\s*\d+\s*-\s*$", # - Page 1 - style headers
        r"สำนักวิจัยและวิชาการ สำนักงานศาลปกครอง"
    ]
    
    # 1. Line-based filtering
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        should_remove = False
        for p in patterns:
            if re.search(p, line, re.IGNORECASE):
                should_remove = True
                break
        if not should_remove:
            cleaned_lines.append(line)
            
    new_content = "\n".join(cleaned_lines)
    
    # 2. Fix multiple newlines (optional, but good for readability)
    new_content = re.sub(r'\n{3,}', '\n\n', new_content)
    
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"✅ Cleaned {input_file}")

if __name__ == "__main__":
    clean_file()
