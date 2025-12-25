#!/usr/bin/env python3
import base64
import sys

# Read the base64 data from stdin or from the JavaScript result
# Since we need to get this from the browser, we'll create a placeholder
# The actual data will be passed via a different method

# For now, let's create a script that the browser can call
print("Please provide the base64 PDF data")
print("Paste the data and press Ctrl+D when done")

# Read all input
base64_data = sys.stdin.read().strip()

# Remove the data URL prefix if present
if base64_data.startswith('data:'):
    base64_data = base64_data.split(',', 1)[1]

# Decode base64 to binary
pdf_binary = base64.b64decode(base64_data)

# Write to file
output_path = "raw_pdfs/sac_o_1148_2560.pdf"
with open(output_path, 'wb') as f:
    f.write(pdf_binary)

file_size_mb = len(pdf_binary) / (1024 * 1024)
print(f"\n✅ Successfully wrote PDF to: {output_path}")
print(f"📏 File size: {len(pdf_binary):,} bytes ({file_size_mb:.2f} MB)")

# Verify it's a PDF
if pdf_binary[:4] == b'%PDF':
    print("✓ Valid PDF file confirmed")
else:
    print("⚠️ Warning: File may not be a valid PDF")
