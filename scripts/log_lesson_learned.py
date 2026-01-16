
import os
import datetime

def log_lesson_learned():
    diary_path = 'git_diary.md'
    
    lesson_entry = (
        "\n### 🧠 บทเรียนและแนวทางป้องกัน (Lesson Learned)\n"
        "**Date:** 2026-01-16\n"
        "**Incident:** Inserted duplicate content (Pages 453-468) into `part_25.md`.\n"
        "**Root Cause:**\n"
        "1.  **PDF Overlap Blind Spot:** `part_25.pdf` contained pages 452-469, but `part_25.md` was intended to start at 469. I assumed the PDF extraction was the 1:1 target for the MD file.\n"
        "2.  **Isolated Verification:** I verified `part_25.md` in isolation without checking the end of `part_24.md`. If I had checked `part_24.md`, I would have seen Page 468 there.\n"
        "**Prevention Plan:**\n"
        "1.  **Neighbor Check:** Before adding \"missing\" pages to the start of a file, ALWAYS check the *end* of the *previous* file (`part_N-1.md`).\n"
        "2.  **Overlap Awareness:** Recognize that split PDFs often contain overlapping pages (context) from previous sections. Do not assume all PDF content belongs in the current MD file.\n"
        "3.  **Strict Continuity Rule:** If `Start_Page(Current_MD) > Start_Page(Source_PDF)`, verification is PASSED if `End_Page(Prev_MD) == Start_Page(Current_MD) - 1`.\n"
    )
    
    with open(diary_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Append to the end of the file or specifically under today's date if possible.
    # For simplicity and visibility, appending at the end of today's section.
    
    # Find end of today's section
    insert_idx = len(lines)
    for i in range(len(lines)-1, -1, -1):
        if lines[i].strip().startswith("## 📅"):
             # Found a date header, so we are inside some date.
             # Ideally we put it before the next date.
             pass
             
    lines.append(lesson_entry)
        
    with open(diary_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print("Lesson learned logged.")

if __name__ == '__main__':
    log_lesson_learned()
