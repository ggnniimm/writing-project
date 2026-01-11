#!/usr/bin/env python3
"""
Re-extract Part 42 from PDF using Gemini 2.5 Flash.
Uses existing API key loading pattern from the project.
"""

import os
import time
import google.generativeai as genai

def load_api_keys():
    """Load API keys from environment and .env file."""
    api_keys = []
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
            api_keys.append(value)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k_val: api_keys.append(k_val)
    return list(set(api_keys))

# Load API keys
api_keys = load_api_keys()
if not api_keys:
    raise ValueError("No API key found. Set GEMINI_API_KEY in environment or .env file.")
print(f"🔑 Loaded {len(api_keys)} API Key(s).")
genai.configure(api_key=api_keys[0])

# Model configuration
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-05-20",
    generation_config={
        "temperature": 0.1,
        "max_output_tokens": 65536,
    }
)

# File paths
pdf_path = "etc/Academic_230317_084750-2_parts/part_42.pdf"
output_path = "etc/Academic_230317_084750-2_parts/part_42_new.md"

# Upload PDF
print(f"📤 Uploading PDF: {pdf_path}")
uploaded_file = genai.upload_file(pdf_path)
print(f"✅ Uploaded: {uploaded_file.name}")

# Wait for processing
while uploaded_file.state.name == "PROCESSING":
    print("⏳ Waiting for file to be processed...")
    time.sleep(2)
    uploaded_file = genai.get_file(uploaded_file.name)

if uploaded_file.state.name != "ACTIVE":
    raise Exception(f"File processing failed: {uploaded_file.state.name}")

print("✅ File ready for extraction")

# Extraction prompt
prompt = """
สกัดข้อความทั้งหมดจาก PDF นี้เป็น Markdown โดยปฏิบัติตามกฎดังนี้:

1. **คงรูปแบบเดิมไว้ทั้งหมด**: รักษาโครงสร้างย่อหน้า หัวข้อ และรายการหมายเลข
2. **ใช้เลขไทยเท่านั้น**: ห้ามใช้เลขอารบิก (0-9) ทุกกรณี รวมถึงในเชิงอรรถ หมายเลขข้อ และปี พ.ศ.
3. **เชิงอรรถ (Footnotes)**:
   - ใช้ `<sup>เลขไทย</sup>` สำหรับ reference ในเนื้อหา เช่น `<sup>๗๙</sup>`
   - ใส่ definition ของเชิงอรรถไว้ท้ายเอกสาร โดยขึ้นต้นด้วย `<sup>เลขไทย</sup>` ตามด้วยคำอธิบาย
4. **Page Headers**: คงไว้ในรูปแบบ `๘๐๔ แนวคำวินิจฉัยของศาลปกครอง` หรือ `แนวคำวินิจฉัยของศาลปกครอง ๘๐๕`
5. **ไม่เพิ่ม/ลบ/แก้ไข**: สกัดข้อความตามต้นฉบับอย่างเคร่งครัด
6. **ละเว้น**: Footer "ศาลปกครองแห่งความเชื่อมั่น TRUST" ไม่ต้องใส่

ให้เริ่มสกัดทันที ไม่ต้องมีคำอธิบายก่อนเนื้อหา
"""

# Extract
print("🔄 Extracting content with Gemini 2.5 Flash...")
response = model.generate_content([uploaded_file, prompt])

# Save output
print(f"💾 Saving to: {output_path}")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"✅ Extraction complete! Output saved to {output_path}")
print(f"📊 Output length: {len(response.text)} characters")
