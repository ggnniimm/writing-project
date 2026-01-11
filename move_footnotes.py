
def move_footnotes():
    path = 'etc/Academic_230317_084750-2_parts/part_42.md'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 0-indexed: Line 601 is index 600.
    # Line 658 is index 657.
    # Check content
    start_idx = 600
    end_idx = 658 # Inclusive of line 658? 
                  # Line 658 in view was "ความเห็นชอบจากกรมธนารักษ์"
                  # This is inside Footnote 80-81.
                  # Step 292 deleted 660-661.
                  # So lines 659 is empty?
    
    # Let's start from correct index.
    # grep said 601: <sup>๗๙</sup>
    if "<sup>๗๙</sup>" not in lines[start_idx]:
        print(f"Error: Line {start_idx+1} does not start with footnote 79.")
        print(f"Found: {lines[start_idx]}")
        return

    # Find end index: Just before "บำรุงรักษา ใช้..."
    # Warning: Line numbers might have shifted if I didn't reload or if view was misleading.
    # I'll search for the split point.
    split_point = -1
    for i in range(start_idx, len(lines)):
        if "บำรุงรักษา ใช้ และจัดหาประโยชน์" in lines[i]:
            split_point = i
            break
    
    if split_point == -1:
        print("Error: Could not find split point 'บำรุงรักษา ใช้...'")
        return

    # Footnotes are from start_idx to split_point - 1
    footnotes = lines[start_idx:split_point]
    
    # Remaining main text (before footnotes) -> up to start_idx
    # Continuation (after footnotes) -> split_point to end
    
    # But wait, "ดูแล" is at the end of line start_idx - 1?
    # View Step 301 says: 597: "...ดูแล" (Line 597!)
    # And 601: Footnote 79.
    # Gap 598-600?
    # 598: Blank?
    # 599: "---"? (I added ---)
    # 600: Blank?
    # So I should include --- in the move or delete it.
    # I'll keep --- with the footnotes.
    
    # Let's grab everything from "---" (around 598) to split_point.
    # Search for ---
    separator_idx = -1
    for i in range(start_idx - 5, start_idx + 1):
        if "---" in lines[i]:
            separator_idx = i
            break
            
    if separator_idx != -1:
        start_cut = separator_idx
    else:
        start_cut = start_idx

    footnotes_block = lines[start_cut:split_point]
    
    # Construct new file
    new_lines = lines[:start_cut] + lines[split_point:] + ["\n"] + footnotes_block
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Moved {len(footnotes_block)} lines to the end.")

if __name__ == "__main__":
    move_footnotes()
