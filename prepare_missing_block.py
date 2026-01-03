
import re

def clean_text(text):
    # Remove artifact lines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if "ข้อมูลฉับไว" in line or "สายด่วนศาลปกครอง" in line:
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def normalize_thai(text):
    # Basic normalization for common PDF weirdness
    # 1. Combine detached vowels (simplified approach)
    # This might not be perfect but better than spaces
    text = text.replace(" ่", "่").replace(" ้", "้").replace(" ๊", "๊").replace(" ๋", "๋")
    text = text.replace(" ิ", "ิ").replace(" ี", "ี").replace(" ึ", "ึ").replace(" ื", "ื")
    text = text.replace(" ุ", "ุ").replace(" ู", "ู")
    text = text.replace("าํ", "ำ")
    return text

with open("debug_clean_pdf.txt", "r", encoding="utf-8") as f:
    content = f.readlines()

# Extract lines 427 to 551 (0-indexed: 426 to 551)
# Note: extracted_lines indices
start_idx = 426
end_idx = 551
extracted_lines = content[start_idx:end_idx] # Python slicing excludes end_idx, so 426 to 550.
# Check extraction accuracy
# Line 427 in file is content[426]
# Line 551 in file is content[550]

raw_text = "".join(extracted_lines)
clean_text_block = clean_text(raw_text)
norm_text_block = normalize_thai(clean_text_block)

print("--- START EXTRACT ---")
print(norm_text_block)
print("--- END EXTRACT ---")

with open("missing_block.txt", "w", encoding="utf-8") as f:
    f.write(norm_text_block)
