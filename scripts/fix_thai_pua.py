
import re

# Mapping based on common Thai PUA usage (and derived from context)
pua_map = {
    '\uf700': '\u0e10', # ฐ
    '\uf701': '\u0e0d', # ญ (upper part)
    '\uf702': '\u0e10', # ฐ (no base)
    '\uf703': '\u0e19', # น (unlikely but safe fallback) - Actually usually ญ bottom
    '\uf704': '\u0e19', 
    '\uf705': '\u0e31', # ั (Mai Han-Akat)
    '\uf706': '\u0e49', # ้ (Mai Tho - special)
    '\uf707': '\u0e4e', # ์ (Thanthakhat) - check context
    '\uf708': '\u0e4d', # ํ (Nikhahit)
    '\uf709': '\u0e47', # ็ (Mai Taikhu)
    
    # Tone marks (Lower position variants often used in PUA)
    '\uf70a': '\u0e48', # ่ (Mai Ek)
    '\uf70b': '\u0e49', # ้ (Mai Tho)
    '\uf70c': '\u0e4a', # ๊ (Mai Tri)
    '\uf70d': '\u0e4b', # ๋ (Mai Chattawa)
    '\uf70e': '\u0e4c', # ์ (Thanthakhat/Garan)
    
    # Vowels
    '\uf70f': '\u0e2d', # อ
    '\uf710': '\u0e30', # ะ
    '\uf711': '\u0e34', # ิ
    '\uf712': '\u0e35', # ี
    '\uf713': '\u0e36', # ึ
    '\uf714': '\u0e37', # ื
    '\uf715': '\u0e38', # ุ
    '\uf716': '\u0e39', # ู
    '\uf717': '\u0e3a', # ฺ (Phinthu)
    
    # More tones/vowels variants
    '\uf718': '\u0e48', 
    '\uf719': '\u0e49',
    '\uf71a': '\u0e4a',
    '\uf71b': '\u0e4b',
    '\uf71c': '\u0e4c',
    '\uf71d': '\u0e4d',
    
    # Walailak encoding shifts (sometimes found)
    '\uf712': '\u0e4c', # ์ (Possible conflict, trust context)
}

# Specific context-based fixes found in file
# \uf712 -> used as sra-ee or garan? 
# "ทรัพย\uf70eสิน" -> ทรัพย์สิน -> \uf70e is Garan (\u0e4c)
# "ความเป\uf712นธรรม" -> เป็น -> \uf712 is Mai Taikhu (\u0e47) OR Sra E (\u0e4b)? 
# Wait, "เป\uf712น" = "เป็น". standard is เ-ป-็-น. 
# If \uf712 is replacing ็ (Mai Taikhu).
pua_map['\uf712'] = '\u0e47' 

def fix_pua(text):
    for wrong, right in pua_map.items():
        text = text.replace(wrong, right)
    return text

target_file = '/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_310717_154727-2_parts/part_40.md'

with open(target_file, 'r') as f:
    content = f.read()

fixed_content = fix_pua(content)

with open(target_file, 'w') as f:
    f.write(fixed_content)

print("Thai PUA characters fixed.")
