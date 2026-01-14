import re

def formatted_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Define Footnotes to process
    # Based on grep: 36, 37, 38, 39, 1, 2, 3, 4
    # We will be careful with 1, 2, 3, 4
    fns = ['๓๖', '๓๗', '๓๘', '๓๙', '๑', '๒', '๓', '๔']
    
    # Track Def lines to avoid double replace
    def_indices = []
    
    # 1. Format Definition Lines
    for i, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line in fns:
            # Check if it looks like a def line (indented or alone)
            # Indentation check?
            if line.startswith(' '):
                 lines[i] = line.replace(clean_line, f'<sup>{clean_line}</sup>')
                 def_indices.append(i)

    full_text = "".join(lines)
    
    # 2. Format Inline References
    # We do this one by one to handle logic
    
    def replacer(match):
        prefix = match.group(1)
        fn_num = match.group(2)
        full_match = match.group(0)
        
        # Check if Year
        if re.match(r'๒๕[๐-๙]{2}', prefix + fn_num):
            return full_match
        # Check if simple number 
        # (heuristics: if prefix is digit, checks mostly done by Year check?
        #  but what about '100' ending in '0'? '๒๐' -> '๒' + '๐' (FN 0?) No FN 0.
        #  If FN is '1'. '11'. '21'. '31'.
        #  If FN is '1'. Prefix '๑'. Match '๑๑'. 
        #  If text is '๑๑', and we replace '๑' with '<sup>๑</sup>', we get '๑<sup>๑</sup>'.
        #  This is bad if it meant '11'.
        #  PROPOSAL: Only replace if matches specific logic or we manually verify context.
        
        # For 36-39, it's safer.
        if fn_num in ['๓๖', '๓๗', '๓๘', '๓๙']:
             return f'{prefix}<sup>{fn_num}</sup>'
             
        # For 1-4:
        # Require prefix to be Non-Digit?
        # Or verify context.
        if fn_num in ['๑', '๒', '๓', '๔']:
             if re.match(r'[๐-๙]', prefix): 
                 # Attached to digit. 
                 # e.g. '๔๑' -> '4' + '1'? 
                 # Check manually?
                 pass 
             else:
                 # Attached to text.
                 # 'ข้อความ๑'.
                 return f'{prefix}<sup>{fn_num}</sup>'
        
        return full_match

    # Regex: (Non-Space)(FN)
    # We use lookbehind or capturing group
    for fn in fns:
        # Pattern: ([^ \n])(FN)(?!>)
        # We ensure we don't match inside already replaced tags
        pattern = f'([^ \n])({fn})(?!</sup>)'
        full_text = re.sub(pattern, replacer, full_text)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_text)

formatted_file('/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_310717_154727-2_parts/part_06.md')
