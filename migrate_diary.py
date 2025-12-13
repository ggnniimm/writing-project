import re
import datetime

DIARY_FILE = "git_diary.md"

def parse_diary(content):
    lines = content.splitlines()
    
    header = []
    days = {}
    current_date = None
    current_section = []
    
    # Process Line by Line
    for line in lines:
        # Check for Date Header ## 📅 ...
        date_match = re.match(r"^## 📅 (.*)", line)
        if date_match:
            if current_date:
                days[current_date] = current_section
            
            # Start new section
            current_date = date_match.group(1).strip()
            current_section = [line]
        else:
            if current_date:
                current_section.append(line)
            else:
                header.append(line)
                
    # Save last section
    if current_date:
        days[current_date] = current_section
        
    return header, days

def process_day_section(day_lines):
    # Separate into parts: Summary, Log Header, Entries, Next Steps
    # This is tricky because the format varies.
    # We look for "### 📝 บันทึกการปฏิบัติงาน (Operations Log)"
    
    pre_log = []
    log_entries = []
    post_log = []
    
    mode = "pre" # pre, log, post
    
    current_entry = []
    
    for line in day_lines:
        if "### 📝 บันทึกการปฏิบัติงาน" in line:
            mode = "log"
            pre_log.append(line)
            continue
            
        if mode == "pre":
            pre_log.append(line)
        elif mode == "log":
            # Check if we hit the next section (Next Steps or just end of logs)
            if "### ⏭️" in line:
                mode = "post"
                # Flush last entry
                if current_entry:
                    log_entries.append(current_entry)
                    current_entry = []
                post_log.append(line)
                continue
            
            # Check for new entry start *   **[HH:MM]
            # or **[YYYY-MM-DD HH:MM]
            is_entry_start = re.match(r"^\*   \*\*\[.*\]", line.strip()) or re.match(r"^\*\*\[.*\]", line.strip())
            
            if is_entry_start:
                if current_entry:
                    log_entries.append(current_entry)
                current_entry = [line]
            else:
                if current_entry:
                    current_entry.append(line)
                else:
                    # Trailing lines after header but before first entry?
                    # or lines between logs? 
                    # Add to pre_log if it seems like spacer, or just ignore format drift
                    if line.strip() == "":
                        pass 
                    else:
                        # Probably part of pre_log spacer?
                        pass
                        
        elif mode == "post":
            post_log.append(line)
            
    if current_entry:
        log_entries.append(current_entry)
        
    return pre_log, log_entries, post_log

def clean_entry(entry_lines):
    # normalize entry to have timestamp and well formatted context
    # Try to extract timestamp to sort
    first_line = entry_lines[0]
    ts_match = re.search(r"\[(.*?)\]", first_line)
    timestamp = ts_match.group(1) if ts_match else "00:00"
    
    # Try to normalize date in timestamp if present?
    # Just return as object for sorting
    return timestamp, entry_lines

def run_migration():
    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    header, days = parse_diary(content)
    
    # Sort Days: Newest Date First
    # Heuristic: Parse "13 ธันวาคม 2025" to date object
    # Thai Months mapping
    thai_months = {
        "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4, "พฤษภาคม": 5, "มิถุนายน": 6,
        "กรกฎาคม": 7, "สิงหาคม": 8, "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12
    }
    
    def parse_thai_date(date_str):
        try:
            parts = date_str.split(" ")
            d = int(parts[0])
            m = thai_months.get(parts[1], 1)
            y = int(parts[2])
            return datetime.date(y, m, d)
        except:
            return datetime.date.min
            
    sorted_dates = sorted(days.keys(), key=parse_thai_date, reverse=True)
    
    new_content = []
    # Write Header
    new_content.extend(header)
    
    for date_str in sorted_dates:
        # Prepend a newline before each date properly
        if new_content and new_content[-1].strip() != "":
            new_content.append("")
            
        day_lines = days[date_str]
        pre_log, log_entries, post_log = process_day_section(day_lines)
        
        # Sort Entries: Newest First
        # Need to parse HH:MM or YYYY-MM-DD HH:MM
        # Some are just HH:MM (assumed today)
        # We need to rely on the fact they are currently chronologically sorted (Old->New) usually
        # But wait, looking at file 13 Dec is [13:27], [13:25], [13:20] -> New->Old (Already good?)
        # 12 Dec is [07:55] ... [22:23] -> Old->New
        
        # Let's try to detect sort order.
        # It's better to just force sort by timestamp text if format is consistent
        # Format varies: [07:55] vs [2025-12-11 15:16]
        
        def parse_ts(ts_str):
            # Normalize to sortable string
            # If HH:MM -> append 0 (but wait, day is constant)
            # If YYYY-MM-DD HH:MM -> use as is
            if len(ts_str) <= 5: # HH:MM
                return ts_str
            else:
                return ts_str.split(" ")[1] if " " in ts_str else ts_str
                
        # Actually, let's just Reverse them if they look chronological (Oldest first)
        # Checking first vs last
        if len(log_entries) > 1:
            first_ts = clean_entry(log_entries[0])[0]
            last_ts = clean_entry(log_entries[-1])[0]
            
            # Simple lexicographical comparison works for 24hr time
            t1 = parse_ts(first_ts)
            t2 = parse_ts(last_ts)
            
            if t1 < t2:
                # Chronological (Old -> New), so we REVERSE
                log_entries.reverse()
                
        # Reconstruct Day
        new_content.extend(pre_log)
        for entry in log_entries:
            # Ensure spacing
            if new_content[-1].strip() != "":
                 new_content.append("")
            new_content.extend(entry)
            
        new_content.extend(post_log)
        
        # Add separator between days?
        # User didn't explicitly ask, but it's good practice. 
        # But let's stick to existing style (H2 handles separation)
        
    # Write Back
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(new_content))
        
    print("Migration Complete")

if __name__ == "__main__":
    run_migration()
