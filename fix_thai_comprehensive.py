#!/usr/bin/env python3
"""
Comprehensive Thai character fix - detect and fix missing tone marks and vowels
"""

import re
import sys
from collections import Counter

def analyze_broken_thai(text):
    """Analyze patterns of broken Thai characters."""
    pattern = r'([\u0E00-\u0E7F]) +([\u0E31-\u0E3A\u0E47-\u0E4E])'
    matches = re.findall(pattern, text)
    
    if matches:
        counter = Counter([''.join(m) for m in matches])
        print("Most common broken patterns:")
        for pattern, count in counter.most_common(20):
            print(f"  '{pattern}' → appears {count} times")
    
    return matches

def fix_comprehensive_thai(text):
    """Fix all Thai character spacing issues comprehensively."""
    
    # Remove ALL spaces between Thai base characters and their vowels/tone marks
    # This regex matches: [Thai consonant/vowel] + [space(s)] + [Thai above/below vowel or tone mark]
    pattern = r'([\u0E00-\u0E7F]) +([\u0E31-\u0E3A\u0E47-\u0E4E])'
    
    # Keep replacing until no more matches (handles multiple spaces)
    prev_text = None
    while prev_text != text:
        prev_text = text
        text = re.sub(pattern, r'\1\2', text)
    
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fix_thai_comprehensive.py <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    print(f"Analyzing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analyze first
    print("\nBefore fixing:")
    analyze_broken_thai(content)
    
    # Fix
    fixed_content = fix_comprehensive_thai(content)
    
    # Count changes
    pattern = r'([\u0E00-\u0E7F]) +([\u0E31-\u0E3A\u0E47-\u0E4E])'
    remaining = len(re.findall(pattern, fixed_content))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"\n✅ Fixed all Thai character spacing issues")
    print(f"Remaining issues: {remaining}")
    
    if remaining > 0:
        print("\nAfter fixing, remaining patterns:")
        analyze_broken_thai(fixed_content)

if __name__ == "__main__":
    main()
