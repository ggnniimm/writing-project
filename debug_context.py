
import re
import sys

def find_context(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find 3237
    target = '๓๒๓๗'
    idx = text.find(target)
    if idx != -1:
        start = max(0, idx - 50)
        end = min(len(text), idx + 50)
        print(f"FOUND {target} at char index {idx}")
        print(f"CONTEXT: ...{text[start:end]}...")
    else:
        print(f"NOT FOUND {target} in text.")

    # Count 2567
    c2567 = text.count('๒๕๖๗')
    print(f"Count of ๒๕๖๗: {c2567}")
    
    # 25637
    target2 = '๒๕๖๓๗'
    idx2 = text.find(target2)
    if idx2 != -1:
        print(f"FOUND {target2} at char index {idx2}")
    else:
        print(f"NOT FOUND {target2}")

if __name__ == "__main__":
    find_context(sys.argv[1])
