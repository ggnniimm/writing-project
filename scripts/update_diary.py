import sys
import datetime
import os
import subprocess
import re
import google.generativeai as genai

# Load API Keys from .env manually to avoid extra dependencies
def load_env():
    api_keys = []
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        # Robust quoting handling: strip " and '
                        value = value.strip().strip("'").strip('"')
                        if key.startswith("GEMINI_API_KEY") and value:
                             api_keys.append(value)
    # Deduplicate while preserving order
    return list(dict.fromkeys(api_keys))

API_KEYS = load_env()
# Default to first key if available, logic will switch if needed
if API_KEYS:
    genai.configure(api_key=API_KEYS[0])

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


def generate_ai_log(diff_text):
    if not API_KEYS:
        return None, None, None
    

    current_key_index = 0
    max_retries = len(API_KEYS) * 2 # Try each key twice if needed
    
    for attempt in range(max_retries):
        try:
            # Configure current key
            genai.configure(api_key=API_KEYS[current_key_index])
            model = genai.GenerativeModel('models/gemini-flash-latest')
            
            prompt = f"""
            Analyze this 'git diff' summary and generate a development log in THAI (ภาษาไทย).
            
            Input Diff Summary:
            {diff_text[:5000]}  # Limit context size
            
            Requirements:
            1. **Role:** You are the AI Developer writing your own "Captain's Log". Use "ผม" (I).
            2. **Main Message:** A concise title of the event/action. (Start with emoji).
            3. **Details:** A chronological narrative paragraph covering:
               - **Event (Situation):** What happened? What did you encounter? (e.g. "ได้รับแจ้งว่า...", "เจอ error ว่า...")
               - **Action:** How did you handle it? (e.g. "ผมจึงตรวจสอบ...", "ผมได้แก้ไขโดย...")
               - **Result:** What was the outcome? (e.g. "ผลลัพธ์คือ...", "ทำให้ระบบสามารถ...")
            4. **Language:** STRICTLY THAI (English allowed only for technical terms/vars).
            5. **Format:** Output ONLY specific string format: "CATEGORY|MAIN_MESSAGE|DETAILS_TEXT"
               - CATEGORY must be 'content' (for markdown/docs) or 'system' (for code/scripts).
               
            Example Output:
            content|📝 ปรับปรุงบทความตาม User Feedback|เมื่อได้รับแจ้งจาก User ว่าตารางเปรียบเทียบดูยาก ผมจึงได้แก้ไข CSS ให้มีความกว้างมากขึ้นและเพิ่มสีพื้นหลังสลับบรรทัด ผลลัพธ์คือตารางอ่านง่ายขึ้นมากและ User พอใจครับ
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse text
            parts = text.split('|')
            if len(parts) >= 3:
                return parts[0], parts[1], parts[2]
            return "system", text, "" # Fallback
            
        except Exception as e:
            # Check for Rate Limit (429) or Resource Exhausted
            if "429" in str(e) or "ResourceExhausted" in str(type(e).__name__):
                if len(API_KEYS) > 1:
                    current_key_index = (current_key_index + 1) % len(API_KEYS)
                    continue # Retry with next key
            return None, None, None
            
            return None, None, None
            
    return None, None, None

def rewrite_log_entry(message, details):
    """
    Uses AI to rewrite the log entry into the standard Strict SAR format.
    Returns: title, situation, action, result
    """
    if not API_KEYS:
        return message, "User cmd", "Executed command", details # Fallback

    current_key_index = 0
    max_retries = len(API_KEYS) * 2
    
    for attempt in range(max_retries):
        try:
            genai.configure(api_key=API_KEYS[current_key_index])
            model = genai.GenerativeModel('models/gemini-flash-latest')
            
            prompt = f"""
            You are the "Chief Officer" of this coding project. 
            Rewrite the following git log entry into the Strict SAR Format (Situation-Action-Result) in Thai.

            Input Message: "{message}"
            Input Details/Context: "{details}"
            
            Rules:
            1. **Language:** STRICTLY THAI (ภาษาไทย). Use English only for specific technical terms.
            2. **Style:** Professional, Narrative, First-person ("ผม").
            3. **Structure (Output Format):**
               You must return exactly 4 parts separated by " ||| ".
               Format: TITLE ||| SITUATION ||| ACTION ||| RESULT
               
               - **TITLE:** Concise summary (e.g. "แก้ไขบั๊กการคำนวณภาษี").
               - **SITUATION:** Context/Why? (e.g. "User แจ้งว่ายอดเงินไม่ตรง...").
               - **ACTION:** What did you do? (e.g. "ผมได้ตรวจสอบสูตรและแก้ไขไฟล์...").
               - **RESULT:** Outcome? (e.g. "ผลลัพธ์คือคำนวณถูกต้องแม่นยำ").

            Example Output:
            ปรับปรุงระบบ Login ||| User แจ้งว่าเข้าสู่ระบบไม่ได้เมื่อเน็ตช้า ||| ผมได้เพิ่ม Timeout และ Retry logic ในหน้า Login ||| ทำให้ User สามารถเข้าใช้งานได้เสถียรขึ้นแม้เน็ตไม่ดี
            """
            
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            if "|||" in text:
                parts = text.split("|||")
                if len(parts) >= 4:
                    return parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
                else:
                    # Best effort mapping
                    return parts[0].strip(), "See details", "Executed changes", text
            else:
                return text, "Context unavailable", "Executed changes", details 
                
        except Exception as e:
            if len(API_KEYS) > 1:
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                continue
            return message, "Unknown Context", "Executed Command", details 

    return message, "Unknown Context", "Executed Command", details

def suggest_mode():
    changes = run_git_diff()
    if not changes:
        print("system|Log: บันทึกเพิ่มเติมก่อน Push|No changes detected")
        return

    # Use 'git diff --cached' to get actual content for AI
    try:
        full_diff = subprocess.check_output(["git", "diff", "--cached"], encoding="utf-8")
    except:
        full_diff = ""

    # Try AI Generation first
    ai_cat, ai_msg, ai_details = generate_ai_log(full_diff)
    
    if ai_cat and ai_msg:
        # Success AI
        # Clean newlines in details for passing to bash
        ai_details_clean = ai_details.replace('\n', ' ').strip()
        print(f"{ai_cat}|{ai_msg}|{ai_details_clean}")
        return

    # Fallback to Heuristic Analysis (Old Logic)
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



def auto_summarize_log(lines, header_date):
    # Heuristic: Scan lines after header_date for log entries
    # Log entry pattern: *   **[HH:MM] 🔧 Task Name**
    
    accomplished_items = []
    
    date_found = False
    for line in lines:
        if line.strip() == header_date:
            date_found = True
            continue
        
        if date_found:
            if line.strip().startswith("## "): # Next date
                break
            
            # Regex for log header
            match = re.search(r'\*\s+\*\*\[\d{2}:\d{2}\]\s+(?:.*?)\s+(.*?)\*\*', line)
            if match:
                task_name = match.group(1).strip()
                # Clean up "Task Name"
                accomplished_items.append(task_name)
    
    # Unique items, preserve order (Python 3.7+ dict is insertion ordered)
    unique_items = list(dict.fromkeys(accomplished_items))
    return unique_items

def summary_mode(target_date=None):
    print("\n🤖 **Daily Retrospective (Auto-Generated)**")
    
    if target_date:
        today_date = target_date
    else:
        today_date = get_thai_date()

    header_date = f"## 📅 {today_date}"
    
    if not os.path.exists(DIARY_FILE):
        print(f"❌ ไม่พบไฟล์ {DIARY_FILE}")
        return

    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Auto-Extract Accomplished
    accomplished_list = auto_summarize_log(lines, header_date)
    
    summary_md = ""
    summary_md += f"**🤖 สรุปภาพรวมประจำวัน (Daily Retrospective):**\n\n"
    
    if accomplished_list:
        summary_md += f"### 1. สิ่งที่ทำไปแล้ว (Accomplished) ✅\n"
        for item in accomplished_list:
            summary_md += f"*   {item}\n"
        summary_md += "\n"
    else:
        summary_md += f"### 1. สิ่งที่ทำไปแล้ว (Accomplished) ✅\n*   (No logs recorded)\n\n"
        
    # Keep Pending and others Empty or Standard
    summary_md += f"### 🎯 เป้าหมายและแผนงาน (Goals & Plans)\n*   (See task.md)\n\n"
    
    # 3. Went Well (Auto-Generated)
    summary_md += f"### 3. สิ่งที่ทำได้ดี (What Went Well) 🌟\n*   System Stability & Automated Git Sync\n\n"
    
    # 4. Not Well (Auto-Generated)
    summary_md += f"### 4. สิ่งที่ยังทำได้ไม่ดี (What Didn't Go Well) 🚧\n*   -\n\n"

    # Update Diary File
    # Logic to replace summary
    # Find Date Header
    date_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == header_date:
            date_idx = i
            break
    
    if date_idx == -1:
         # No date entry? Then we can't summarize logs effectively if they don't exist under this date
         # But maybe logs were just added? 
         # For safety, if no date header, we can't replace summary.
         print("❌ ไม่พบหัวข้อวันที่ (No date section found). Please run 'ppp' first.")
         return
    else:
        # Date exists. Look for the "Summary" section to replace.
        start_replace = date_idx + 1
        end_replace = start_replace
        
        log_header_marker = "### 📝 บันทึกการปฏิบัติงาน"
        
        for i in range(start_replace, len(lines)):
            if lines[i].strip().startswith(log_header_marker):
                end_replace = i
                break
            if lines[i].strip().startswith("## 📅"):
                 end_replace = i
                 break
        
        # Replace
        lines[start_replace:end_replace] = [s + "\n" for s in summary_md.split('\n')]

    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
        
    print("✅ สรุปงานประจำวันอัตโนมัติเรียบร้อย")

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

def get_previous_next_steps(lines, current_header_date):
    """
    Scans the diary for the most recent 'Next Steps' block BEFORE the current date.
    Returns a list of extracted items.
    """
    next_steps = []
    
    # We want to look at the day immediately preceeding the current one.
    # Since the file is reverse chronological (mostly), the previous day should be *after* the current day's entry (if it existed)
    # But start_day_mode is usually run when the current day *doesn't* exist yet, so we just want the top-most date.
    
    # Strategy: Find the first "## 📅" that is NOT the current_header_date (if it exists).
    # Actually, in start_day_mode, we haven't inserted the new date yet. 
    # So we just look for the first occurrence of "⏭️ ก้าวต่อไป (Next Steps)"
    
    start_search = False
    items_found = []
    
    for line in lines:
        if "⏭️ ก้าวต่อไป (Next Steps)" in line:
            start_search = True
            continue
        
        if start_search:
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("---"): 
                break # End of section
            
            if stripped.startswith("- [ ]") or stripped.startswith("- [x]") or stripped.startswith("* "):
                # Extract text
                # clean "- [ ] " or "* "
                clean_item = re.sub(r'^[-*]\s+(\[.*?\]\s+)?', '', stripped)
                if clean_item and "..." not in clean_item:
                     items_found.append(clean_item)
            
            if items_found: # Just take the first block found (latest day)
                 pass 
                 
    # We only want the *first* block we find (which corresponds to the latest previous entry)
    # The loop above continues, but we should probably stop after the first block ends.
    # Let's refine the logic.
    
    
    final_items = []
    in_section = False
    
    # Headers to look for (Legacy & New)
    target_headers = [
        "⏭️ ก้าวต่อไป (Next Steps)",
        "สิ่งที่ยังไม่ได้ทำและมีแผนจะทำ (Pending / Planned)",
        "🎯 เป้าหมายและแผนงาน (Goals & Plans)"
    ]

    for line in lines:
        if any(h in line for h in target_headers):
            in_section = True
            # Check if this header is NOT the current day's (if passing current_header_date is used for exclusion, 
            # but lines are scanned linearly. We assume we scan from top.
            # If start_day_mode is run, the current day doesn't exist yet, so the first match IS the previous day.)
            continue
        
        if in_section:
            stripped = line.strip()
            if not stripped: continue
            
            if stripped.startswith("#") or stripped.startswith("---"):
                break # End of most recent Next Steps section
            
            # Capture items
            if stripped.startswith("-") or stripped.startswith("*"):
                 final_items.append(stripped) # Keep format
                 
    return final_items

def load_content_ideas():
    """
    Loads key future goals from content_ideas.md.
    Returns a list of goal strings to display in diary.
    """
    ideas_file = "content_ideas.md"
    if not os.path.exists(ideas_file):
        return []
    
    goals = []
    with open(ideas_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract key topics from content_ideas.md
    # Looking for main headings (###) that represent planned work
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('### '):
            title = line.replace('### ', '').strip()
            # Extract a brief description...
            desc = ""
            for j in range(i+1, min(i+10, len(lines))): # Scan a bit deeper
                strip_l = lines[j].strip()
                if strip_l.startswith('*') and "ที่มา" not in strip_l and "ประเด็น" not in strip_l:
                     desc = strip_l.replace('*', '').strip()
                     break
            
            if desc:
                goals.append(f"- [ ] **{title}**: {desc[:60]}...")
            else:
                goals.append(f"- [ ] **{title}**")
            
            if len(goals) >= 3: # Get top 3
                break
    
    return goals


def start_day_mode():
    if not os.path.exists(DIARY_FILE):
        print(f"❌ ไม่พบไฟล์ {DIARY_FILE}")
        return

    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    today_date = get_thai_date()
    header_date = f"## 📅 {today_date}"
    
    # Check if date already exists
    date_exists = any(line.strip() == header_date for line in lines)
    if date_exists:
        print("⚠️ วันนี้มีการเริ่มงานไปแล้ว (Date entry already exists)")
        return

    # Auto-Fetch Previous Next Steps
    previous_plans = get_previous_next_steps(lines, header_date)
    
    # Load future goals from content_ideas.md
    content_goals = load_content_ideas()

    # Create new section
    new_section = []
    new_section.append(f"\n{header_date}\n")
    
    new_section.append(f"### 🎯 เป้าหมายและแผนงาน (Goals & Plans)\n")
    new_section.append(f"**สถานะปัจจุบัน (Current Status):**\n")
    new_section.append(f"-   (รอสรุปสถานะ...)\n\n")

    new_section.append(f"**แผนงานวันนี้ (Today's Plan):**\n")
    
    # Display ongoing tasks
    if previous_plans:
        new_section.append(f"**จากงานค้างเมื่อวาน (From Previous Day):**\n")
        for item in previous_plans:
             clean_item = item.replace("- [x]", "- [ ]").replace("- [/]", "- [ ]")
             new_section.append(f"{clean_item}\n")
        new_section.append("\n")
    
    # Display future goals
    if content_goals:
        new_section.append(f"**ไอเดียที่น่าสนใจ (From content_ideas.md):**\n")
        for goal in content_goals:
            new_section.append(f"{goal}\n")
    else:
         new_section.append(f"- [ ] (No automatic suggestions found)\n")
    
    new_section.append("\n") # Spacer

    new_section.append(f"### 📝 บันทึกการปฏิบัติงาน (Operations Log)\n")
    
    # Initial Log Entry
    time_str = get_time_str().split(" ")[1]
    new_section.append(f"**[{time_str}] เริ่มต้นภารกิจประจำวัน (Start of Day)**\n")
    new_section.append(f"    > เริ่มต้นวันใหม่ ตรวจสอบสถานะและวางแผนงานเรียบร้อย\n\n")
    
    # Insert at top (after main header)
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("# "): 
             insert_idx = i + 1
             if insert_idx < len(lines) and lines[insert_idx].strip() == "":
                 insert_idx += 1
             break
    
    lines[insert_idx:insert_idx] = new_section
    
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"✅ เริ่มต้นวันใหม่เรียบร้อย ({today_date})")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--suggest":
            suggest_mode()
            sys.exit(0)
        elif sys.argv[1] == "--summary":
            target_date = None
            if len(sys.argv) > 2:
                # Allow passing date as "16 ธันวาคม 2025"
                target_date = sys.argv[2]
            summary_mode(target_date)
            sys.exit(0)

        elif sys.argv[1] == "--read-latest":
            read_latest_mode()
            sys.exit(0)
        elif sys.argv[1] == "--start-day":
            start_day_mode()
            sys.exit(0)

    if len(sys.argv) < 3:
        print("Usage: python3 update_diary.py <category> <message> [details]")
        sys.exit(1)

    category_code = sys.argv[1] # 'content' or 'system'
    raw_message = sys.argv[2]
    raw_details = sys.argv[3] if len(sys.argv) > 3 else ""

    # --- NEW: Standardize Input via AI ---
    # Always rewrite to ensure Thai language and narrative style
    print("🤖 AI กำลังเรียบเรียงภาษาตาม Strict SAR Format...")
    title, situation, action, result = rewrite_log_entry(raw_message, raw_details)

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
    
    # Strict SAR Entry Format
    # **[HH:MM] 🔧 Title**
    #     > **Situation (ที่มา):** ...
    #     > **Action (การดำเนินการ):** ...
    #     > **Result (ผลลัพธ์):** ...
    #     *   *Files:* ...
    
    time_str = get_time_str().split(" ")[1] # Get HH:MM
    entry_header = f"**[{time_str}] {icon} {title}**"
    
    entry_body = []
    entry_body.append(f"    > **Situation (ที่มา):** {situation}")
    entry_body.append(f"    > **Action (การดำเนินการ):** {action}")
    entry_body.append(f"    > **Result (ผลลัพธ์):** {result}")

    # Auto-detect files
    file_list_str = ""
    try:
        files = [line.split('\t')[1] for line in run_git_diff() if len(line.split('\t')) > 1]
        if files:
            file_objs = [f"`{os.path.basename(f)}`" for f in files]
            file_list_str = ", ".join(file_objs)
    except:
        pass
    
    if file_list_str:
        entry_body.append(f"    *   *Files:* {file_list_str}")
        
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
        new_section = []
        new_section.append(f"\n{header_date}\n")
        new_section.append(f"**🤖 สรุปภาพรวมประจำวัน:**\n(รอสรุป...)\n\n")
        new_section.append(f"{log_header}\n")
        new_section.append(full_entry)
        new_section.append("\n### ⏭️ ก้าวต่อไป (Next Steps)\n- [ ] ...\n")
        new_section.append("---")
        
        # Insert after the main header (usually line 0 or 1)
        # Find the first line starting with '# ' and sub-header if any
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                 insert_idx = i + 1
                 # Maybe allow for some spacing
                 if insert_idx < len(lines) and lines[insert_idx].strip() == "":
                     insert_idx += 1
                 break
        
        lines[insert_idx:insert_idx] = new_section
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
    
    print(f"✅ บันทึก '{title}' เรียบร้อย")

if __name__ == "__main__":
    main()
