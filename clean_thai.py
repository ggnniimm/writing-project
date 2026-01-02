
import re
import sys
import os

def clean_thai_content(text):
    # Regex to find a space between two Thai characters and remove it.
    # Thai range \u0E00-\u0E7F
    # We use lookbehind and lookahead to match the position, capturing the whitespace itself.
    # We strip all whitespace (space, tab, etc) but NOT newlines?
    # \s matches [ \t\n\r\f\v].
    # We typically do NOT want to merge across newlines.
    # So use [ \t]+ or similar.
    
    pattern = r'(?<=[\u0E00-\u0E7F])[ \t]+(?=[\u0E00-\u0E7F])'
    
    # Apply substitution
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def process_file(file_path):
    print(f"Processing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = clean_thai_content(content)
    
    if content != new_content:
        print(f"cleaned {len(content) - len(new_content)} characters (spaces).")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    else:
        print("No changes needed.")

if __name__ == "__main__":
    for arg in sys.argv[1:]:
        process_file(arg)
