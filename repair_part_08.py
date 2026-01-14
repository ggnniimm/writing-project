
import re

md_path = "etc/Academic_310717_154727-2_parts/part_08.md"
pdf_txt_path = "part_08_pdf.txt"
out_path = "etc/Academic_310717_154727-2_parts/part_08.md" # Overwrite!

with open(md_path, 'r', encoding='utf-8') as f:
    md_lines = f.readlines()

with open(pdf_txt_path, 'r', encoding='utf-8') as f:
    pdf_text = f.read()

new_lines = []
skip = False

# 1. Fix Headers & Arabic Numeral
for i, line in enumerate(md_lines):
    # Fix Header 131
    if "แนวคำวินิจฉัยของศาลปกครอง ๑๒" in line and "๑๓๑" not in line and "๑๓๒" not in line and len(line.strip()) < 40:
        line = line.replace("๑๒", "๑๓๑")
        print("Fixed Header 131")
    
    # Fix Page 135 Missing Header
    # Logic: Look for the text that starts Page 135.
    # From grep earlier, Page 134 header is at line 349.
    # Page 136 header is at line 382.
    # We need to insert 135 between them.
    # Let's verify context lines.
    
    # Fix Arabic Numeral 5
    if "5" in line and "not 5" not in line: # Simple safety
        # Specific fix for Line 669: ไม่น้อยกว่า 5 เมตร
        if "ไม่น้อยกว่า 5 เมตร" in line:
            line = line.replace("5", "๕")
            print("Fixed Arabic 5")

    new_lines.append(line)

# 2. Insert Page 135 Header
# We need to find the split point.
# Let's search for the text that ends Page 134 and starts Page 135.
# Based on MD inspection:
# Line 380: TRUST footer.
# Line 381: (Empty)
# Line 382: 136 Header.
# This implies Page 135 is MISSING or MERGED.
# If merged, it would be between 349 and 382.
# But 349-382 is only 33 lines. A full page is usually ~30-40 lines.
# So text between 349 and 382 is likely ONE page (Page 134).
# So Page 135 is MISSING ENTIRELY from MD!
# We must insert it.

# Let's read Page 135 content from PDF Text.
# PDF Text is contiguous. We need to find the text between Page 134 end and Page 136 start.
# Page 134 end text (from MD): "ก่อสร้างอาคารที่พักอาศัยตามคำขอ" (Line 379)
# Page 136 start text (from MD): "ฉบับดังกล่าว โดยแผนผังโครงการกำหนดให้เป็น" (Line 383, header 136 is 382)
# Let's find these snippets in PDF Text.

p134_end_snippet = "ก่อสร้างอาคารที่พักอาศัยตามคำขอ"
p136_start_snippet = "ฉบับดังกล่าว โดยแผนผังโครงการกำหนดให้เป็น"

start_idx = pdf_text.find(p134_end_snippet)
end_idx = pdf_text.find(p136_start_snippet)

missing_content = ""
if start_idx != -1 and end_idx != -1:
    # Extract content between them
    raw_missing = pdf_text[start_idx + len(p134_end_snippet):end_idx]
    # Clean it up (remove Footers/Headers usually present in PDF text layout)
    # The clean method is simple here: just take it all, we can refine format later.
    missing_content = "\n" + "แนวคำวินิจฉัยของศาลปกครอง ๑๓๕" + "\n" + raw_missing.strip() + "\n"
    print(f"Extracted missing Page 135 content ({len(missing_content)} chars)")
else:
    print("CRITICAL: Could not locate missing page content in PDF text.")
    print(f"Start found: {start_idx}, End found: {end_idx}")

# Now insert it into new_lines.
# Insert after Line 380 (TRUST) and before Line 382 (Header 136).
# Actually, insert at the index where we processed Line 380.
final_lines = []
inserted = False
for line in new_lines:
    final_lines.append(line)
    if "ศาลปกครองแห่งความเชื่อมั่น TRUST" in line and not inserted:
        # Check if this is the TRUST before Header 136
        # We need to be careful. There are many TRUST lines.
        # The specific one is around line 380.
        # Let's rely on the next line being Header 136?
        pass

# Better approach for insertion:
# Iterate and check lookahead? No.
# Use index? No, lines change.
# Match context: previous line TRUST, next line Header 136.
# Since we are building final_lines, we can check.

adjusted_lines = []
for i in range(len(new_lines)):
    line = new_lines[i]
    adjusted_lines.append(line)
    
    # Check if we are at the gap
    # Line is TRUST. Next line (i+1) is empty. Next (i+2) is Header 136.
    if "ศาลปกครองแห่งความเชื่อมั่น TRUST" in line:
        # Check if next substantial line is Header 136
        # Look ahead 1-3 lines
        is_gap = False
        for offset in range(1, 5):
            if i + offset < len(new_lines):
                next_l = new_lines[i+offset]
                if "๑๓๖ แนวคำวินิจฉัยของศาลปกครอง" in next_l:
                    is_gap = True
                    break
        
        if is_gap and missing_content:
            print("Inserting Page 135...")
            adjusted_lines.append(missing_content)
            inserted = True

# 3. Footnote Formatting
formatted_lines = []
# Regex for References: (Text)(ThaiNum) -> Text<sup>ThaiNum</sup>
# Be careful of date years (พ.ศ. ๒๕๔๘) -> Don't touch.
# Be careful of numbers with commas (๑,๐๐๐) -> Don't touch.
# Be careful of section numbers (ข้อ ๑) -> Don't touch.
# Pattern: Word character followed immediately by Number.
# Exclude: "ที่ ๑", "ข้อ ๑", "พ.ศ. ๒", "ปี ๒"
# Include: "ข้อความ๑"

# Regex for Thai numerals: [\u0e50-\u0e59]
thai_digit = r"[\u0e50-\u0e59]"

def format_ref(match):
    # Check context.
    # Group 1: Preceding char
    # Group 2: The number
    pre = match.group(1)
    num = match.group(2)
    
    # Exclusion list (preceding words)
    exclusions = ["ที่", "ข้อ", "ศ.", "ลา", "ม่", "มู่", "ขต", "าพ", "่"] 
    # "ศ." for พ.ศ., "ที่" for No., "ข้อ" for Clause.
    # "ม่" -> ไม่ (e.g. ไม่ ๑) unlikely.
    # "ลา" -> เวลา ๑ ?
    
    # Better: explicit ignore.
    if pre in ["ที่", "ข้อ", "ศ."]: 
         return match.group(0) # No change
    
    # Check if number is a YEAR (4 digits starting with 25..)
    if len(num) == 4 and num.startswith("๒๕"):
        return match.group(0)
    
    # Check if number is comma separated (e.g. 1,000) - handled by regex structure usually?
    # Our regex captures digit sequence. If followed by comma, it's fine.
    
    return f"{pre}<sup>{num}</sup>"

# Regex: (?<=[^\s])([๑-๙]+)(?=[\s\.\)\]]|$|[a-zA-Z])
# Only match if preceded by non-space.
# Be careful of "พ.ศ. ๒๕๔๙" -> Space exists, so regex won't match "๒๕๔๙". Good.
# But "ข้อ ๑" -> Space exists. Regex won't match "๑". Good.
# "วรรคหนึ่ง๔" -> No space. Regex MATCHES "๔". Good.
# "มาตรา ๘ (๙)" -> Space. No match.
# "๑,๐๐๐" -> "๑" followed by comma.
# Wait, "๑,๐๐๐". "๑" is attached to nothing? or space?
# If "จำนวน ๑,๐๐๐", space before ๑. No match. Good.
# So, matching "Non-space then Digit" handles most "attached" footnotes.

ref_regex = re.compile(f"([^\s\d\u0e50-\u0e59])({thai_digit}+)(?=[\s\.\)\]]|$)")
# Preceded by non-digit, non-space.
# Followed by space, dot, paren, quote, or end of line.

for line in adjusted_lines:
    # 1. Format References
    # Apply regex
    if "<sup>" not in line: # Don't double format
        new_line = ref_regex.sub(lambda m: f"{m.group(1)}<sup>{m.group(2)}</sup>", line)
    else:
        new_line = line
    
    # 2. Format Definitions (Line starts with number)
    # Pattern: ^\s*([๑-๙]+)\s+(.*)
    # Only if line length is short-ish or looks like footer? No, definitions are long.
    # But checking if the number matches checking footnote sequences?
    # Let's just format lines starting with a small number (1-3 digits).
    
    def_match = re.match(r"^\s*([๑-๙]{1,2})\s+(.*)", new_line)
    if def_match:
        num = def_match.group(1)
        content = def_match.group(2)
        # Verify it's not a Header "๑๒๓ แนว..." (Headers usually have text first or specific format)
        # Headers: "๑๒๖ แนวคำวินิจฉัย..." matches.
        if "แนวคำวินิจฉัย" in content:
            formatted_lines.append(new_line)
            continue
            
        # Verify it's not a List Item "๑. ..." (Usually has dot)
        # If no dot, it looks like a definition.
        # Exclude "๑" in content?
        # Part 07 definitions were just "๑  กฎกระทรวง...".
        new_line = f"<sup>{num}</sup> {content}\n"
        print(f"Formatted Definition: {num}")
        
    formatted_lines.append(new_line)

with open(out_path, 'w', encoding='utf-8') as f:
    f.writelines(formatted_lines)

print("Done.")
