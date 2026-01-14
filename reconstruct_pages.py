
import re

md_path = "etc/Academic_310717_154727-2_parts/part_08.md"
pdf_path = "part_08_pdf.txt"

# 1. Read PDF Text
with open(pdf_path, 'r', encoding='utf-8') as f:
    pdf_text = f.read()

# 2. Extract Blocks
# Find indices of Headers
# "๑๓๔ แนวคำวินิจฉัยของศาลปกครอง" (Note: PDF text might have "แนวคํา..." with differing vowels/tone marks?)
# Let's use flexible regex or just find logical markers.
# PDF text often has different unicode normalization.
# Let's search for "๑๓๔" then "๑๓๕" then "๑๓๖".

idx_134 = pdf_text.find("๑๓๔")
idx_135 = pdf_text.find("๑๓๕")
idx_136 = pdf_text.find("๑๓๖")

if idx_134 == -1 or idx_135 == -1 or idx_136 == -1:
    print(f"CRITICAL: Could not find headers in PDF text. Indices: {idx_134}, {idx_135}, {idx_136}")
    # Fallback search for simpler string
    if idx_134 == -1: idx_134 = pdf_text.find("134")
    if idx_135 == -1: idx_135 = pdf_text.find("135")
    # ...
    exit(1)

# Extract P134 Block (From 134 to 135)
# Ideally include header 134.
# But exclude text *before* 134.
# Block 134 starts at 134 Header.
# Ends before 135 Header.
# Be careful of Footer "TRUST".
# Let's capture everything from Header 134 up to (but not including) Header 135.

block_134 = pdf_text[idx_134:idx_135]

# Extract P135 Block (From 135 to 136)
block_135 = pdf_text[idx_135:idx_136]

# Clean Blocks
# Ensure Headers are clean.
# block_134 likely starts "๑๓๔ แนว...". Good.
# block_135 likely starts "๑๓๕ แนว...". Good.
# Check for extraneous lines?

# 3. Read MD
with open(md_path, 'r', encoding='utf-8') as f:
    md_lines = f.readlines()

# 4. Find Insert Point in MD
# Start: Line after "พิพากษายกฟ้อง" (Page 133 end).
# End: Line before "๑๓๖ แนว..." (Header 136).

start_idx = -1
end_idx = -1

for i, line in enumerate(md_lines):
    if "พิพากษายกฟ้อง" in line and "อ.๔๗๕" in line: # Relaxed search
         start_idx = i + 1
    if "๑๓๖ แนวคำวินิจฉัยของศาลปกครอง" in line:
         end_idx = i
         break

if start_idx == -1 or end_idx == -1:
    print(f"CRITICAL: Could not find insert points in MD. Start: {start_idx}, End: {end_idx}")
    exit(1)

# Cleanup: Removing False Positive Footnotes (Years 25xx)
# Pattern: <sup>(๒๕..)</sup> -> \1
year_fix_regex = re.compile(r"<sup>(๒๕[๐-๙]{2})</sup>")

for i in range(len(md_lines)):
    if "<sup>" in md_lines[i]:
         md_lines[i] = year_fix_regex.sub(r"\1", md_lines[i])

print(f"Replacing lines {start_idx} to {end_idx} (count: {end_idx - start_idx})")

# 5. Prepare New Content
# Need to format footnotes in the blocks!
# Using the regex from repair script.

formatted_blocks = []
thai_digit = r"[\u0e50-\u0e59]"
ref_regex = re.compile(f"([^\s\d\u0e50-\u0e59])({thai_digit}+)(?=[\s\.\)\]]|$)")

for block in [block_134, block_135]:
    lines = block.split('\n')
    new_block_lines = []
    for line in lines:
        # Filter empty lines? Keep structure.
        # Clean specific PDF artifacts?
        # Format References
        line_clean = line.strip() # Or keep indentation?
        if not line_clean:
            new_block_lines.append("")
            continue
            
        new_line = ref_regex.sub(lambda m: f"{m.group(1)}<sup>{m.group(2)}</sup>", line_clean)
        
        # Format Definitions
        def_match = re.match(r"^\s*([๑-๙]{1,2})\s+(.*)", new_line)
        if def_match:
             num = def_match.group(1)
             content = def_match.group(2)
             if "แนวคำวินิจฉัย" not in content and "พระราชบัญญัติ" not in content[:20]: # Be careful not to format Headers or Laws as definitions improperly
                 new_line = f"<sup>{num}</sup> {content}"
        
        # Fix Header Formatting
        # If line starts "๑๓๔ แนว..." -> "แนวคำวินิจฉัยของศาลปกครอง ๑๓๔" (Standard format: Text Number)
        # PDF Text often has it reversed or weird.
        # MD standard: "แนวคำวินิจฉัยของศาลปกครอง ๑๓๔"
        # My grep output showed: "๑๓๔ แนว..."
        # So I need to SWAP.
        if re.match(r"\s*๑\s*๓\s*[๔-๕]\s*แนว", new_line): # Loose match
            # Extract number
            num_match = re.search(r"(๑\s*๓\s*[๔-๕])", new_line)
            if num_match:
                n = num_match.group(1).replace(" ", "")
                new_line = f"แนวคำวินิจฉัยของศาลปกครอง {n}"
        
        new_block_lines.append(new_line)
    
    formatted_blocks.append("\n".join(new_block_lines) + "\n")

# 6. Apply Replacement
final_lines = md_lines[:start_idx] + ["\n"] + formatted_blocks + ["\n"] + md_lines[end_idx:]

with open(md_path, 'w', encoding='utf-8') as f:
    f.writelines(final_lines)

print("Done Reconstructing.")
