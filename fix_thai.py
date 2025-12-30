import sys
import re

def fix_thai_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # PUA mapping (general)
    pua_map = {
        '\uf700': 'ฐ', '\uf701': 'ฑ', '\uf702': 'ฒ', '\uf703': 'ณ', '\uf704': 'ด', 
        '\uf705': 'ต', '\uf706': 'ถ', '\uf707': 'ท', '\uf708': 'ธ', '\uf709': 'น', 
        '\uf70a': 'บ', '\uf70b': 'ป', '\uf70c': 'ผ', '\uf70d': 'ฝ', '\uf70e': 'พ', 
        '\uf70f': 'ฟ', '\uf710': 'ภ', '\uf711': 'ม', '\uf712': 'ย', '\uf713': 'ร', 
        '\uf714': 'ฤ', '\uf715': 'ล', '\uf716': 'ภ', '\uf717': 'ว', '\uf718': 'ศ', 
        '\uf719': 'ษ', '\uf71a': 'ส', '\uf71b': 'ห', '\uf71c': 'ฬ', '\uf71d': 'อ', 
        '\uf71e': 'ฮ', '\uf70f': 'ฯ'
    }
    
    # Replace PUA
    for pua, real in pua_map.items():
        content = content.replace(pua, real)

    # Normalize vowels/tones
    # Swap tone mark and vowel if wrong order (Consonant + Tone + VowelUpper -> Consonant + VowelUpper + Tone)
    # Actually, standard is Consonant + Vowel(if any) + Tone.
    # But commonly Sara Am ( ำ ) is decomposed as Nikhahit ( ํ ) + Sara Aa ( า ).
    # And sometimes sequences like Mai Ek ( ่ ) comes before Nikhahit.
    
    # 1. Normalize Sara Am
    content = content.replace('\u0e4d\u0e32', '\u0e33') # Nikhahit + Sara Aa -> Sara Am
    
    # 2. Fix floating vowels (simplified) - removed for now as regex is complex and context specific.
    
    # 3. Replace 'เ' + 'เ' with 'แ'
    content = content.replace('เเ', 'แ')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed encoding in {filepath}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_thai_file(sys.argv[1])
    else:
        print("Usage: python fix_thai.py <file>")
