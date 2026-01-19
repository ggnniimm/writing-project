
import sys
import re

def fix_thai_pua(text):
    # Mapping PUA characters to standard Thai characters
    # Based on common PDF extraction artifacts
    
    mapping = {
        '\uf700': '\u0e10', # Thantanakhat? No, usually not mapped this way.
        # Tone marks at different levels
        '\uf70a': '\u0e49', # Mai Tho (High)
        '\uf70b': '\u0e49', # Mai Tho
        '\uf709': '\u0e49', # Mai Tho (Low)
        
        '\uf70e': '\u0e4c', # Thanthakhat
        
        '\uf707': '\u0e48', # Mai Ek (High)
        '\uf708': '\u0e48', # Mai Ek (Low)
        
        '\uf70c': '\u0e4a', # Mai Tri
        '\uf70d': '\u0e4b', # Mai Chattawa
        
        '\uf705': '\u0e48', # Mai Ek
        '\uf706': '\u0e49', # Mai Tho
        
        # Vowels
        '\uf701': '\u0e31', # Mai Han-Akat
        '\uf702': '\u0e31',
        '\uf703': '\u0e33', # Sara Am
        '\uf704': '\u0e33', 
        
        # Nikhahit
        '\uf711': '\u0e4d',
        
        # Sara I/Ii/Ue/Uee etc often shift too
        # But usually it's just the tone marks that are weirdest.
    }
    
    # Specific observations from the file:
    # ผู ->  (U+F709) -> ้ (U+0E49)
    # ฟอง ->  (U+F70A) -> ้ (U+0E49)
    # แหง ->  (U+F708) -> ่ (U+0E48)
    # สัปดาห ->  (U+F70E) -> ์ (U+0E4C)
    
    # Let's perform the replacement
    new_text = ""
    for char in text:
        if char in mapping:
            new_text += mapping[char]
        elif 0xF700 <= ord(char) <= 0xF71F:
            # Fallback or log? 
            # Let's map typicals:
            if char == '\uf708': new_text += '\u0e48'
            elif char == '\uf709': new_text += '\u0e49'
            elif char == '\uf70a': new_text += '\u0e49'
            elif char == '\uf70e': new_text += '\u0e4c'
            elif char == '\uf707': new_text += '\u0e48'
            elif char == '\uf70c': new_text += '\u0e4a'
            elif char == '\uf70d': new_text += '\u0e4b'
            else:
                new_text += char # Keep if unknown, but maybe warn?
        else:
            new_text += char
            
    return new_text

def main(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fixed_content = fix_thai_pua(content)
    
    if content != fixed_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"Fixed encoding in {filepath}")
    else:
        print(f"No changes needed for {filepath}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python fix_thai_encoding.py <file>")
