
import os

def main():
    part_08_path = 'etc/split_vol07/part_08.md'
    extracted_page_path = 'scripts/references/rulings_court/ref_sac_unknown.md'
    
    # Read Part 08
    with open(part_08_path, 'r', encoding='utf-8') as f:
        part_08_lines = f.readlines()
        
    print(f"Original lines in part_08.md: {len(part_08_lines)}")
    
    # Read Extracted Page
    with open(extracted_page_path, 'r', encoding='utf-8') as f:
        extracted_lines = f.readlines()
        
    print(f"Extracted lines: {len(extracted_lines)}")
    
    # Insertion Point:
    # Based on view:
    # 230: ศาลปกครองสูงสุดที่ ๑๗๘/๒๕๖๐)
    # 231: TRUST
    # 232: ศาลปกครองแห่งความเชื่อมั่น
    # 233: 
    # 234: ๑๑๔ แนวคำวินิจฉัยของศาลปกครอง
    
    # We want to replace lines 231-233 with Page 113.
    # Lines 231-233 are indices 230, 231, 232.
    
    if "TRUST" not in part_08_lines[230] or "ศาลปกครองแห่งความเชื่อมั่น" not in part_08_lines[231]:
        print("Warning: Lines 231-232 do not match expected artifacts. Aborting.")
        print(f"Line 231: {part_08_lines[230].strip()}")
        print(f"Line 232: {part_08_lines[231].strip()}")
        return

    # New lines: Part 1 (0 to 229 inclusive), Page 113, Part 2 (233 onwards)
    new_part_08_lines = part_08_lines[:230] # Indices 0..229
    
    # Append Page 113
    new_part_08_lines.extend(extracted_lines)
    
    # Add a newline for separation if needed (Page 113 ends with TRUST, Page 114 starts with header)
    if not new_part_08_lines[-1].endswith('\n'):
        new_part_08_lines[-1] += '\n'
    new_part_08_lines.append('\n')
    
    # Append Part 2 (from index 233 which is line 234)
    new_part_08_lines.extend(part_08_lines[233:])
    
    # Write back
    with open(part_08_path, 'w', encoding='utf-8') as f:
        f.writelines(new_part_08_lines)
        
    print(f"Merged successfully. New line count: {len(new_part_08_lines)}")

if __name__ == "__main__":
    main()
