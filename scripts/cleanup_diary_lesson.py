
import os

def remove_lesson_from_diary():
    diary_path = 'git_diary.md'
    with open(diary_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_marker = "### 🧠 บทเรียนและแนวทางป้องกัน (Lesson Learned)"
    new_lines = []
    skip = False
    
    for line in lines:
        if start_marker in line:
            skip = True
        
        # If we hit a new date header or similar major section, stop skipping (though this was at the end)
        if skip and line.strip().startswith("## 📅") and "2026-01-16" not in line:
            # Safety check, but likely it's the last item.
            skip = False
            
        if not skip:
            new_lines.append(line)
            
    with open(diary_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Removed duplicate lesson from diary.")

if __name__ == '__main__':
    remove_lesson_from_diary()
