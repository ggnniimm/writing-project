import re
import sys

def to_thai_num(n):
    thai_digits = '๐๑๒๓๔๕๖๗๘๙'
    return ''.join(thai_digits[int(d)] for d in str(n))

def main(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex for [^123]:
    # We want to replace it with <sup>๑๒๓</sup> (note the space after colon usually)
    
    def replace_func(match):
        num = match.group(1)
        rest = match.group(2)
        thai_num = to_thai_num(num)
        return f"<sup>{thai_num}</sup>{rest}"

    new_content = re.sub(r'^\[\^(\d+)\]:(.*)', replace_func, content, flags=re.MULTILINE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Processed {filepath}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python fix_footnote_defs.py <file>")
