import re
import sys

def print_context(path, numeral):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # regex for isolated numeral: not preceded or followed by Thai digit
    pattern = r'(?<![๐-๙])' + re.escape(numeral) + r'(?![๐-๙])'
    
    matches = list(re.finditer(pattern, text))
    print(f"Found {len(matches)} occurrences of ISOLATED {numeral} in {path}")
    for i, m in enumerate(matches):
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        snippet = text[start:end].replace('\n', ' ')
        print(f"  {i+1}: ...{snippet}...")

if __name__ == "__main__":
    path = sys.argv[1]
    numeral = sys.argv[2]
    print_context(path, numeral)
