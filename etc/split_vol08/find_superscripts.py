import re

def scan_digits(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # regex for Thai digits
    digit_pattern = re.compile(r'[\u0e50-\u0e59]+')
    
    print(f"Scanning {filepath} for Thai digits...")
    for i, line in enumerate(lines):
        # We are looking for digits that might be superscripts.
        # Common pattern: digit at end of word, maybe surrounded by spaces.
        # But we want to filter out clear years "๒๕๔๒", "๒๕๔๓", "๑๓๕๕" (phone), "๑." (header)
        
        matches = list(digit_pattern.finditer(line))
        for m in matches:
            val = m.group()
            start, end = m.span()
            
            # Context
            context = line.strip()
            
            # Filters
            # 1. Year (4 digits starting with 25xx)
            if re.match(r'๒๕\d\d', val): continue
            # 2. Section headers "๑.", "๑.๑" etc.
            # a bit hard to regex perfectly but if it is at start of line
            if start < 10 and (line[end:end+1] == '.' or line[end:end+1] == ' '):
                # Likely header "๑. "
                continue
                
            # 3. Phone number 1355
            if val == '๑๓๕๕': continue
            
            # 4. Enclosed in parens (๑), (๑๒)
            # Check char before and after
            prev_char = line[start-1] if start > 0 else ''
            next_char = line[end] if end < len(line) else ''
            
            if prev_char == '(' and next_char == ')': continue
            
            # 5. Page numbers? (often standalone)
            if len(context) < 3: continue 
            
            print(f"Line {i+1}: Found '{val}' in: {context}")

if __name__ == "__main__":
    scan_digits('/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_03_raw.txt')
