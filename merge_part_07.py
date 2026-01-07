
import os

def main():
    part_07_path = 'etc/split_vol07/part_07.md'
    extracted_page_path = 'scripts/references/rulings_court/ref_sac_unknown.md'
    
    # Read Part 07
    with open(part_07_path, 'r', encoding='utf-8') as f:
        part_07_lines = f.readlines()
        
    print(f"Original lines in part_07.md: {len(part_07_lines)}")
    
    # Read Extracted Page
    with open(extracted_page_path, 'r', encoding='utf-8') as f:
        extracted_lines = f.readlines()
        
    print(f"Extracted lines: {len(extracted_lines)}")
    
    # Truncate Part 07
    # We want to remove lines 650 and 651 (based on 1-index), so keep 0-649 (index).
    # Line 649 in 1-based index is line 648 in 0-based index.
    # The file had 651 lines.
    # Line 649 content: "...อันเนื่องจากการกระทำของผู้ถูกฟ้องคดี"
    # Line 650: empty
    # Line 651: "TRUST..."
    
    # Verify line 649 content
    if "อันเนื่องจากการกระทำของผู้ถูกฟ้องคดี" not in part_07_lines[648]:
        print("Warning: Line 649 does not match expected content. Aborting to be safe.")
        print(f"Actual line 649: {part_07_lines[648]}")
        return

    # Keep lines up to line 649 (index 648), inclusive.
    # Slice is [0:649] which gives indices 0..648.
    new_part_07_lines = part_07_lines[:649]
    
    print(f"Truncated part_07_lines to: {len(new_part_07_lines)}")
    
    # Append newline if needed
    if not new_part_07_lines[-1].endswith('\n'):
        new_part_07_lines[-1] += '\n'
        
    # Append Extracted Content
    # We might want to strip the first line if it's just '```markdown' or similar metadata, 
    # but gemini extraction usually gives raw text.
    # Let's verify the header is 'แนวคำวินิจฉัย...'
    
    new_part_07_lines.extend(extracted_lines)
    
    # Write back
    with open(part_07_path, 'w', encoding='utf-8') as f:
        f.writelines(new_part_07_lines)
        
    print(f"Merged successfully. New line count: {len(new_part_07_lines)}")

if __name__ == "__main__":
    main()
