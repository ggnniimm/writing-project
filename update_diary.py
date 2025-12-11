import sys
import datetime
import os

DIARY_FILE = "git_diary.md"

def get_thai_date():
    months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    now = datetime.datetime.now()
    year = now.year + 543 if now.year < 2400 else now.year # Adjust only if it's Christ era
    # Actually user seems to use 2025 in the file, let's match the file format
    # File uses: ## 📅 11 ธันวาคม 2025
    # So year is 2025 (CE). Let's stick to CE if the file uses CE.
    # checking file... "11 ธันวาคม 2025" -> This is CE.
    return f"{now.day} {months[now.month-1]} {now.year}"

def get_time_str():
    return datetime.datetime.now().strftime("%H:%M")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 update_diary.py <category> <message> [details]")
        sys.exit(1)

    category_code = sys.argv[1] # 'content' or 'system'
    message = sys.argv[2]
    details = sys.argv[3] if len(sys.argv) > 3 else ""

    today_date = get_thai_date()
    header_date = f"## 📅 {today_date}"
    
    cat_header = ""
    icon = ""
    if category_code == "content":
        cat_header = "### ✍️ Content & Research (งานเนื้อหาและค้นคว้า)"
        icon = "📝" # Default icon, can be customized
    elif category_code == "system":
        cat_header = "### 🔧 System & Workflow (งานระบบและคำสั่ง)"
        icon = "🛠"
    else:
        print(f"Unknown category: {category_code}")
        sys.exit(1)

    entry_line = f"*   **[{get_time_str()}] {icon} {message}**"
    if details:
        # Indent details
        entry_line += "\n" + "\n".join([f"    *   {line}" for line in details.split('\n') if line.strip()])

    # Read file
    if not os.path.exists(DIARY_FILE):
        lines = []
    else:
        with open(DIARY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Logic to insert
    # 1. Find Date Header
    date_found_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == header_date:
            date_found_idx = i
            break
    
    if date_found_idx == -1:
        # Create new date block at the end
        if lines and lines[-1].strip() != "":
            lines.append("\n")
        lines.append(f"{header_date}\n\n{cat_header}\n{entry_line}\n")
    else:
        # Date found, look for Category Header under this date
        # Search from date_found_idx onwards until next ## Header or End of file
        cat_found_idx = -1
        next_date_idx = len(lines)
        
        for i in range(date_found_idx + 1, len(lines)):
            if lines[i].strip().startswith("## "): # Next date block
                next_date_idx = i
                break
            if lines[i].strip() == cat_header.strip():
                cat_found_idx = i
        
        if cat_found_idx != -1:
            # Append inside existing category
            # Find the end of this category (start of next cat or next date)
            insert_pos = next_date_idx
            for i in range(cat_found_idx + 1, next_date_idx):
                if lines[i].strip().startswith("### "): # Next category
                    insert_pos = i
                    break
            
            # Use insert_pos
            lines.insert(insert_pos, f"{entry_line}\n")
            
        else:
            # Category not found under this date, Insert it.
            # Determine where to insert: After the last category of this date?
            # Or just after the Date header if no cats exist?
            
            # Simple logic: Insert before next date or at end of existing content for this date
            insert_pos = next_date_idx
            # If there is another category, we might want to order them? 
            # Content First, System Second.
            if category_code == "content":
                 # Insert right after date header + 1 (blank line)
                 insert_pos = date_found_idx + 2
                 if insert_pos >= len(lines):
                     lines.append("\n")
                     insert_pos = len(lines)
            else:
                 # System goes to the end of the day block
                 pass # insert_pos is already next_date_idx
            
            lines.insert(insert_pos, f"\n{cat_header}\n{entry_line}\n")

    # Write back
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"✅ บันทึก '{message}' ลงในหมวด '{category_code}' เรียบร้อย")

if __name__ == "__main__":
    main()
