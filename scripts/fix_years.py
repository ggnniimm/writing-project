
import os
import json

base_dir = "etc/split_v14_2569_40"

corrections = {
  "part_25": ["อผ. ๓๙/๒๕๖๔"],
  "part_26": ["อ. ๙/๒๕๖๔"],
  "part_27": ["อร. ๓/๒๕๖๔", "อ. ๖๕/๒๕๖๔", "อ. ๓๖๘/๒๕๖๔", "อ. ๔๖/๒๕๖๔", "อ. ๙๘/๒๕๖๔"],
  "part_28": ["อ. ๘/๒๕๖๔", "อ. ๘๒/๒๕๖๔"],
  "part_29": ["อร. ๑๔/๒๕๖๔", "อร. ๑๘/๒๕๖๔", "อ. ๓๕๓/๒๕๖๔", "อร. ๓๕/๒๕๖๔", "อร. ๑๑/๒๕๖๔"],
  "part_30": ["อ. ๓๕๘/๒๕๖๔", "อร. ๗/๒๕๖๔", "อร. ๔๐/๒๕๖๔", "อร. ๖๐/๒๕๖๔", "อ. ๑๐/๒๕๖๔", "อ. ๓๖๕/๒๕๖๔", "อ. ๑๘๙/๒๕๖๔"],
  "part_31": ["อ. ๒๙๗/๒๕๖๔"],
  "part_32": ["อ. ๒๔๔/๒๕๖๔", "อร. ๓๘/๒๕๖๔", "อร. ๒๐/๒๕๖๔"],
  "part_33": ["อ. ๑๕๓/๒๕๖๔", "อ. ๑๙๖/๒๕๖๔"],
  "part_34": ["อ. ๓๓๑/๒๕๖๔"],
  "part_37": ["อร. ๓๓/๒๕๖๔"],
  "part_38": ["อร. ๑๕/๒๕๖๔", "อ. ๒๐๙/๒๕๖๔"]
}

def fix_files():
    for part, items in corrections.items():
        md_path = os.path.join(base_dir, f"{part}.md")
        if not os.path.exists(md_path):
            print(f"Skipping {part} (not found)")
            continue
            
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        modified = False
        for item in items:
            # item is like "อผ. ๓๙/๒๕๖๔"
            # We want to replace it with "อผ. ๓๙/๒๕๖๘"
            target = item
            replacement = item.replace("๒๕๖๔", "๒๕๖๘")
            
            if target in content:
                content = content.replace(target, replacement)
                print(f"Fixed {target} -> {replacement} in {part}")
                modified = True
            else:
                print(f"Warning: Could not find {target} in {part}")
                
        if modified:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved {part}")

if __name__ == "__main__":
    fix_files()
