import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    fns = ['๓๖', '๓๗', '๓๘', '๓๙', '๑', '๒', '๓', '๔']
    
    # Map for easy lookup
    fn_set = set(fns)

    def replacement(match):
        fn = match.group(1)
        start = match.start()
        end = match.end()
        
        # Context
        # preceding char
        prev_char = text[start-1] if start > 0 else ''
        prev_two = text[start-2:start] if start > 1 else ''
        next_char = text[end] if end < len(text) else ''
        
        # Check if Definition Line
        # If line contains ONLY the number and whitespace
        # Find line start/end
        line_start = text.rfind('\n', 0, start) + 1
        line_end = text.find('\n', end)
        if line_end == -1: line_end = len(text)
        line_content = text[line_start:line_end].strip()
        
        if line_content == fn:
            return f'<sup>{fn}</sup>'
        
        # Skip Year: 25xx
        if fn in ['๓๖', '๓๗', '๓๘', '๓๙']:
            if prev_two == '๒๕': return fn # Year 2536 etc
            
        # Skip List: (1)
        if prev_char == '(' and next_char == ')': return fn
        
        # Skip Amounts/Decimals
        if prev_char in ['.', ',']: return fn
        
        # Skip if part of larger number (followed by digit)
        if re.match(r'[๐-๙]', next_char): return fn
        
        # Handle 1-4 specific
        if fn in ['๑', '๒', '๓', '๔']:
            # Skip if space before (Moo 1, No 1)
            if prev_char == ' ': return fn
            # Skip if digit before (11, 21, 41 ambiguous)
            # Unless we are sure. For now SKIP to avoid errors like 0.12
            if re.match(r'[๐-๙]', prev_char): return fn
            
        return f'<sup>{fn}</sup>'

    # Regex to match any FN
    # Sort by length desc so 36 matches before 3
    pattern = '|'.join(sorted(fns, key=len, reverse=True))
    
    new_text = re.sub(f'({pattern})', replacement, text)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_text)

process_file('/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_310717_154727-2_parts/part_06.md')
