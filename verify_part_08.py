
import subprocess
import re

md_file = "etc/Academic_310717_154727-2_parts/part_08.md"
pdf_file = "etc/Academic_310717_154727-2_parts/part_08.pdf"

print("--- 1. Character Counts ---")
try:
    md_chars = len(open(md_file).read())
    print(f"MD Chars: {md_chars}")
except Exception as e:
    print(f"Error reading MD: {e}")

try:
    pdf_text = subprocess.check_output(["pdftotext", "-layout", pdf_file, "-"]).decode('utf-8')
    pdf_chars = len(pdf_text)
    print(f"PDF Chars: {pdf_chars}")
    print(f"Ratio: {md_chars / pdf_chars:.2f}")
except Exception as e:
    print(f"Error reading PDF: {e}")

print("\n--- 2. Arabic Numeral Check ([0-9] in MD) ---")
try:
    grep_out = subprocess.check_output(["grep", "-n", "[0-9]", md_file]).decode('utf-8')
    print("WARNING: Arabic Numerals Found:")
    print(grep_out[:500]) # Print first 500 chars
except subprocess.CalledProcessError:
    print("PASS: No Arabic Key numerals found.")

print("\n--- 3. Page Headers (125+) ---")
try:
    headers = subprocess.check_output(["grep", "แนวคำวินิจฉัยของศาลปกครอง", md_file]).decode('utf-8').strip().split('\n')
    print(f"Found {len(headers)} headers.")
    for i, h in enumerate(headers[:5]):
        print(f"Header {i+1}: {h.strip()}")
    print("...")
    for i, h in enumerate(headers[-5:]):
         print(f"Header {len(headers)-4+i}: {h.strip()}")
except Exception as e:
    print(f"Error checking headers: {e}")

print("\n--- 4. Footnote Check (<sup> tags) ---")
try:
    sup_count = subprocess.check_output(["grep", "-c", "<sup>", md_file]).decode('utf-8').strip()
    print(f"Found {sup_count} <sup> tags.")
except Exception as e:
    print(f"Error checking footnotes: {e}")
