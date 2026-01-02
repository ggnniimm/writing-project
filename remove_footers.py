import re
import sys

def remove_footers(file_path):
    print(f"Removing footers from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the 4-line footer block with flexible leading whitespace
    pattern = r'[ \t]*ระบบงานคดีปกครองอิเล็กทรอนิกส์\n' \
              r'[ \t]*ยื่นฟ้องออนไลน์ สะดวก รวดเร็ว เป็นธรรม\n' \
              r'[ \t]*https://bit\.ly/3sBQbvO\n' \
              r'[ \t]*สายด่วนศาลปกครอง ๑๓๕๕'
    
    # Remove all occurrences
    new_content = re.sub(pattern, '', content)
    
    # Count how many were removed
    count = len(re.findall(pattern, content))
    
    if new_content != content:
        print(f"  Removed {count} footer(s)")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print(f"  No footers found")

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        remove_footers(arg)
