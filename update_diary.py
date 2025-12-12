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
        return f"General Update{content_summary}"
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
                messages.append(f"Update {filename}: {header}")
                details.append(f"📝 แก้ไข: {filename} (Section: {header})")
            else:
                messages.append(f"Update {filename}")
                details.append(f"📝 แก้ไข: {filename}")
    
    # Check for other files
    other_files = [f[1] for f in changes if f[1] not in content_files]
    if other_files:
        if not messages: # Pure system update
            messages.append("System Update: Config & Scripts")
        
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

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--suggest":
        suggest_mode()
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
    log_header = "### 📝 Operations Log"
    
    # Icon mapping
    icon = "📌"
    if category_code == "content":
        icon = "📝"
    elif category_code == "system":
        icon = "🔧"
    
    # Narrative Entry Format
    # *   **[HH:MM] 🔧 Task Name**
    #     [Narrative...]
    #     *   *Files:* ...
    
    time_str = get_time_str().split(" ")[1] # Get HH:MM
    entry_header = f"*   **[{time_str}] {icon} {message}**"
    
    entry_body = []
    if details:
        details_clean = details.replace("\\n", "\n")
        # Add narrative text directly
        entry_body.append(f"    {details_clean}")
    
    # Auto-detect files if not explicitly mentioned (Simple heuristic)
    try:
        files = [line.split('\t')[1] for line in run_git_diff() if len(line.split('\t')) > 1]
        if files:
            file_list = ", ".join([f"`{os.path.basename(f)}`" for f in files])
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
        # Create new date section with Summary placeholder
        if lines and lines[-1].strip() != "":
            lines.append("\n")
        lines.append(f"{header_date}\n")
        lines.append(f"**🤖 Daily Summary:**\n(Pending Summary...)\n\n")
        lines.append(f"{log_header}\n")
        lines.append(full_entry)
        lines.append("\n### ⏭️ Next Steps\n- [ ] ...\n")
    else:
        # Date exists, find Log Header
        log_found_idx = -1
        next_section_idx = len(lines)
        
        for i in range(date_found_idx + 1, len(lines)):
            if lines[i].strip().startswith("## "): # Next date
                next_section_idx = i
                break
            if lines[i].strip() == log_header:
                log_found_idx = i
            # If we find "Next Steps" or other h3
            if lines[i].strip().startswith("### ⏭️"):
                next_section_idx = i
                break
                
        if log_found_idx != -1:
            # Append to existing log section (before the next section)
            # Find the end of this log section
            insert_pos = next_section_idx
            # Backtrack empty lines
            while insert_pos > log_found_idx and lines[insert_pos-1].strip() == "":
                insert_pos -= 1
            
            lines.insert(insert_pos, f"{full_entry}")
            # Ensure spacing
            if lines[insert_pos-1].strip() != "":
               lines.insert(insert_pos, "\n")
               
        else:
            # Date exists but no Log header (weird, but create it)
            # Insert after Summary (assuming summary is right after date)
            insert_pos = date_found_idx + 1
            # Skip summary lines
            while insert_pos < len(lines) and not lines[insert_pos].strip().startswith("###"):
                 insert_pos += 1
            
            lines.insert(insert_pos, f"\n{log_header}\n{full_entry}\n")

    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"✅ บันทึก '{message}' เรียบร้อย")

if __name__ == "__main__":
    main()
