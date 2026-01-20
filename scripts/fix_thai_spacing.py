
import re

def fix_spacing(text):
    # Remove spaces between Thai characters
    # Look for [Thai char] [2 or more spaces] [Thai char] - standard layout preservation
    # Look for [Thai char] [1 space] [Thai char] - this is the "exploded text" issue
    
    # Strategy: If we see Thai-Space-Thai, join them.
    # But be careful not to join actual words separated by space.
    # However, "readable" Thai doesn't use spaces between words, only sentences/clauses.
    # The extracted text has spaces between *every* letter.
    
    pattern = r'([ก-๙])\s+([ก-๙])'
    prev_text = ""
    while text != prev_text:
        prev_text = text
        text = re.sub(pattern, r'\1\2', text)
        
    return text

with open('/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_310717_154727-2_parts/part_40.md', 'r') as f:
    lines = f.readlines()

# Only apply to the recovered section (approx line 580 onwards)
fixed_lines = []
for i, line in enumerate(lines):
    if i < 580:
        fixed_lines.append(line)
    else:
        # Also clean up loose vowels if any
        fixed_line = fix_spacing(line)
        # Fix vowel floating issues common in PDF extraction (e.g.    )
        fixed_line = re.sub(r'\s+([ุ-ู็-์])', r'\1', fixed_line)
        fixed_lines.append(fixed_line)

with open('/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_310717_154727-2_parts/part_40.md', 'w') as f:
    f.writelines(fixed_lines)

print("Spacing fixed.")
