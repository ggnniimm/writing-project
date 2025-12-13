import sys
import datetime
import os
import subprocess
import re

DIARY_FILE = "git_diary.md"

def get_thai_date():
    months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
        "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    now = datetime.datetime.now()
    return f"{now.day} {months[now.month-1]} {now.year}"

def get_time_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def run_git_diff():
    try:
        # Get status of staged files
        result = subprocess.check_output(["git", "diff", "--cached", "--name-status"], encoding="utf-8")
        return [line.split('\t') for line in result.strip().split('\n') if line.strip()]
    except:
        return []

def analyze_markdown_changes(filepath):
    try:
        # Get diff content to see which lines changed
        diff = subprocess.check_output(["git", "diff", "--cached", "-U0", filepath], encoding="utf-8")
        
        # Determine changed line number (first match)
        match = re.search(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', diff)
        if not match:
            return None
        
        changed_line_num = int(match.group(1))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 1. Find Header (Context)
        current_header = None
        for i in range(min(changed_line_num - 1, len(lines) - 1), -1, -1):
            line = lines[i].strip()
            if line.startswith("#"):
                current_header = line.lstrip("#").strip()
                break

        # 2. Extract Added Content (Summary)
        # Look for lines starting with '+' in diff, exclude '+++' header and empty lines
        added_lines = []
        for line in diff.split('\n'):
            if line.startswith('+') and not line.startswith('+++') and len(line) > 2:
                clean_line = line[1:].strip().replace('*', '').replace('-', '').strip()
                if clean_line:
                    added_lines.append(clean_line)
        
        # Summarize content (take first 2 meaningful lines)
        content_summary = ""
        if added_lines:
            content_summary = " (Items: " + ", ".join(added_lines[:2]) + ")"
        
        if current_header:
            return f"{current_header}{content_summary}"
        return f"อัปเดตทั่วไป{content_summary}"
    except:
        return None

def suggest_mode():
    changes = run_git_diff()
    if not changes:
        print("system|Log: บันทึกเพิ่มเติมก่อน Push|No changes detected")
        return

    # Heuristic Analysis
    category = "system"
    messages = []
    details = []

    content_files = [f[1] for f in changes if f[1].endswith(".md") and "articles/" in f[1]]
    
    if content_files:
        category = "content"
        for f in content_files:
            filename = os.path.basename(f)
            header = analyze_markdown_changes(f)
            if header:
                messages.append(f"แก้ไข {filename}: {header}")
                details.append(f"📝 แก้ไข: {filename} (ส่วน: {header})")
            else:
                messages.append(f"แก้ไข {filename}")
                details.append(f"📝 แก้ไข: {filename}")
    
    # Check for other files
    other_files = [f[1] for f in changes if f[1] not in content_files]
    if other_files:
        if not messages: # Pure system update
            messages.append("ปรับปรุงระบบ: Config & Scripts")
        
        for f in other_files:
            if f.endswith(".py") or f.endswith(".sh") or "push-work" in f:
                details.append(f"🛠 แก้ไขระบบ: {os.path.basename(f)}")
            else:
                details.append(f"📄 แก้ไข: {os.path.basename(f)}")

    # Construct Output
    final_message = " | ".join(messages[:2]) # Take max 2 primary messages
    if len(messages) > 2:
        final_message += " and more..."
        
    final_details = "\\n".join(details)
    
    print(f"{category}|{final_message}|{final_details}")

def summary_mode():
    print("\n📝 **Daily Retrospective (สรุปภาพรวมประจำวัน)**")
    print("กรุณาตอบคำถามสั้นๆ (กด Enter เพื่อข้ามหัวข้อที่ไม่ต้องการระบุ)\n")

    accomplished = input("1. ✅ สิ่งที่ทำสำเร็จ (Accomplished): ").strip()
    pending = input("2. 🗓️ สิ่งที่ยังค้างอยู่/แผนต่อไป (Pending): ").strip()
    went_well = input("3. 🌟 สิ่งที่ทำได้ดี (What Went Well): ").strip()
    not_well = input("4. 🚧 สิ่งที่ยังทำได้ไม่ดี (What Didn't Go Well): ").strip()
    improvements = input("5. 🔧 สิ่งที่ควรปรับปรุง (Improvements): ").strip()

    # Generate Summary Markdown
    summary_md = ""
    
    summary_md += f"**🤖 สรุปภาพรวมประจำวัน (Daily Retrospective):**\n\n"
    
    if accomplished:
        summary_md += f"### 1. สิ่งที่ทำไปแล้ว (Accomplished) ✅\n*   {accomplished}\n\n"
    
    if pending:
        summary_md += f"### 2. สิ่งที่ยังไม่ได้ทำและมีแผนจะทำ (Pending / Planned) 🗓️\n*   {pending}\n\n"
    
    if went_well:
        summary_md += f"### 3. สิ่งที่ทำได้ดี (What Went Well) 🌟\n*   {went_well}\n\n"
        
    if not_well:
        summary_md += f"### 4. สิ่งที่ยังทำได้ไม่ดี (What Didn't Go Well) 🚧\n*   {not_well}\n\n"
        
    if improvements:
        summary_md += f"### 5. สิ่งที่ควรต้องแก้ไข (Improvements) 🔧\n*   {improvements}\n\n"
        
    if not summary_md.strip().replace("**🤖 สรุปภาพรวมประจำวัน (Daily Retrospective):**", "").strip():
         print("❌ ไม่มีการกรอกข้อมูลสรุป ยกเลิกการอัปเดตสรุปประจำวัน")
         return

    # Update Diary File
    if not os.path.exists(DIARY_FILE):
        print(f"❌ ไม่พบไฟล์ {DIARY_FILE}")
        return

    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    today_date = get_thai_date()
    header_date = f"## 📅 {today_date}"
    
    # Logic to replace summary
    # Find Date Header
    date_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == header_date:
            date_idx = i
            break
    
    if date_idx == -1:
        # Create new date section (should be unusual for end of day, but handle it)
         if lines and lines[-1].strip() != "":
            lines.append("\n")
         lines.append(f"{header_date}\n")
         lines.append(f"{summary_md}")
         lines.append(f"### 📝 บันทึกการปฏิบัติงาน (Operations Log)\n") # Add log header if new
         print("⚠️ สร้างหัวข้อวันที่ใหม่ (ปกติควรมีอยู่แล้วจากการทำงานระหว่างวัน)")
    else:
        # Date exists. Look for the "Summary" section to replace.
        # It usually starts after date header and ends before "### 📝 บันทึกการปฏิบัติงาน"
        
        start_replace = date_idx + 1
        end_replace = start_replace
        
        # Heuristic: Find where the operations log starts
        log_header_marker = "### 📝 บันทึกการปฏิบัติงาน"
        
        for i in range(start_replace, len(lines)):
            if lines[i].strip().startswith(log_header_marker):
                end_replace = i
                break
            # Safety break if we hit next date
            if lines[i].strip().startswith("## 📅"):
                 end_replace = i
                 break
        
        # Replace the range [start_replace:end_replace] with new summary
        # But allow keeping lines that are NOT the old summary boilerplate if impactful?
        # For simplicity and robustness, we overwrite the "Summary Block".
        
        # Construct the new specific block
        lines[start_replace:end_replace] = [s + "\n" for s in summary_md.split('\n')]

    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    print("✅ อัปเดตสรุปภาพรวมประจำวันเรียบร้อย")

def read_latest_mode():
    if not os.path.exists(DIARY_FILE):
        print(f"❌ ไม่พบไฟล์ {DIARY_FILE}")
        return

    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    found_first_date = False
    printed_lines = []
    
    for line in lines:
        if line.strip().startswith("## 📅"):
            if found_first_date:
                # Found the *second* date, stop
                break
            found_first_date = True
        
        if found_first_date:
            printed_lines.append(line)
            
    if not printed_lines:
        print("ยังไม่มีบันทึกประจำวัน")
    else:
        print("".join(printed_lines).strip())


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--suggest":
            suggest_mode()
            sys.exit(0)
        elif sys.argv[1] == "--summary":
            summary_mode()
            sys.exit(0)
        elif sys.argv[1] == "--read-latest":
            read_latest_mode()
            sys.exit(0)

    if len(sys.argv) < 3:
        print("Usage: python3 update_diary.py <category> <message> [details]")
        sys.exit(1)

    category_code = sys.argv[1] # 'content' or 'system'
    message = sys.argv[2]
    details = sys.argv[3] if len(sys.argv) > 3 else ""

    today_date = get_thai_date()
    # Format: ## 📅 12 ธันวาคม 2025
    header_date = f"## 📅 {today_date}"
    
    # New Standard Header for Logs
    log_header = "### 📝 บันทึกการปฏิบัติงาน (Operations Log)"
    
    # Icon mapping
    icon = "📌"
    if category_code == "content":
        icon = "📝"
    elif category_code == "system":
        icon = "🔧"
    
    # Narrative Entry Format
    # *   **[HH:MM] 🔧 Task Name**
    #     > "Narrative..."
    #     *   *Files:* ...
    
    time_str = get_time_str().split(" ")[1] # Get HH:MM
    entry_header = f"*   **[{time_str}] {icon} {message}**"
    
    entry_body = []
    if details:
        details_clean = details.replace("\\n", "\n")
        # Add narrative text with quote style for emphasis (Context)
        # Check if it looks like a file list or narrative
        lines_detail = details_clean.splitlines()
        narrative = []
        file_info = []
        
        for line in lines_detail:
            if line.strip().startswith("📝 แก้ไข:") or line.strip().startswith("🛠") or line.strip().startswith("✨") or line.strip().startswith("📄"):
                 file_info.append(line)
            else:
                 narrative.append(line)
        
        if narrative:
            entry_body.append("    > " + "\n    > ".join(narrative))
            entry_body.append("") # Spacer
            
        if file_info:
             entry_body.extend([f"    {l}" for l in file_info])
    
    # Auto-detect files if not explicitly mentioned (Simple heuristic)
    try:
        files = [line.split('\t')[1] for line in run_git_diff() if len(line.split('\t')) > 1]
        if files:
            file_list = ", ".join([f"`{os.path.basename(f)}`" for f in files])
            # Avoid duplicate file listing if possible, but keep specific changes
            if not any("Files:" in d for d in details.split("\\n")):
                 entry_body.append(f"    *   *Files:* {file_list}")
    except:
        pass

    full_entry = f"{entry_header}\n" + "\n".join(entry_body) + "\n"

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
        # Create new date section
        if lines and lines[-1].strip() != "":
            lines.append("\n")
        lines.append(f"{header_date}\n")
        lines.append(f"**🤖 สรุปภาพรวมประจำวัน:**\n(รอสรุป...)\n\n")
        lines.append(f"{log_header}\n")
        lines.append(full_entry)
        lines.append("\n### ⏭️ ก้าวต่อไป (Next Steps)\n- [ ] ...\n")
    else:
        # Date exists, find Log Header
        log_found_idx = -1
        
        for i in range(date_found_idx + 1, len(lines)):
            if lines[i].strip() == log_header:
                log_found_idx = i
                break
            if lines[i].strip().startswith("## "): # Next date safety check
                break
                
        if log_found_idx != -1:
            # Insert AT THE TOP of the log section (LIFO)
            insert_pos = log_found_idx + 1
            lines.insert(insert_pos, f"{full_entry}")
               
        else:
            # Date exists but no Log header (weird), Insert after Summary
            insert_pos = date_found_idx + 1
            while insert_pos < len(lines) and not lines[insert_pos].strip().startswith("###"):
                 insert_pos += 1
            
            lines.insert(insert_pos, f"\n{log_header}\n{full_entry}\n")

    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"✅ บันทึก '{message}' เรียบร้อย")

if __name__ == "__main__":
    main()
