import google.generativeai as genai
import os
import time
from pypdf import PdfReader, PdfWriter

def load_api_keys():
    api_keys = []
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
            api_keys.append(value)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
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
    raise ValueError("No GEMINI_API_KEY found in environment or .env file")

genai.configure(api_key=api_keys[0])

# Path to PDF
pdf_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_04.pdf"
output_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol08/part_04_new.md"

def extract_chunk(chunk_path, chunk_index):
    print(f"Uploading {chunk_path} to Gemini...")
    sample_file = genai.upload_file(path=chunk_path, display_name=f"part_04_chunk_{chunk_index}")
    
    print(f"Waiting for file processing for chunk {chunk_index}...")
    while sample_file.state.name == "PROCESSING":
        time.sleep(2)
        sample_file = genai.get_file(sample_file.name)
    
    if sample_file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {sample_file.state}")
        
    print(f"Chunk {chunk_index} ready. Extracting...")
    
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    
    prompt = """กรุณาถอดข้อความจากเอกสาร PDF นี้ออกมาเป็น Markdown
    
    กรุณาปฏิบัติตามกฎเหล่านี้อย่างเคร่งครัด:
    1. ถอดข้อความ "ทุกตัวอักษร" จากหน้าแรกจนถึงหน้าสุดท้าย
    2. "ห้าม" ตัดประโยคเริ่มต้นออก แม้จะเป็นประโยคที่ไม่สมบูรณ์ (sentence fragment) ให้ถอดออกมาทั้งหมด
    3. "เก็บเลขหน้าไว้" (เช่น ๒๐, ๒๑) โดยให้วางไว้บรรทัดเดียวกับต้นฉบับ หรือบรรทัดแยกต่างหากที่เหมาะสม
    4. ใช้ตัวเลขไทย (๐-๙) ทั้งหมด
    5. จัดรูปแบบด้วย Markdown headers ตามความเหมาะสม
    6. ห้ามตัดเนื้อหาใดๆ ออกเด็ดขาด
    
    เริ่มถอดข้อความ:"""
    
    from google.api_core.exceptions import ResourceExhausted
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = model.generate_content([sample_file, prompt])
            break
        except ResourceExhausted as e:
            print(f"Rate limit exceeded (429). Waiting before retry {attempt+1}/{max_retries}...")
            time.sleep(60) # Wait 60 seconds
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limit exceeded (429). Waiting before retry {attempt+1}/{max_retries}...")
                time.sleep(60)
            else:
                raise e
    else:
        raise Exception("Max retries exceeded")
    text = response.text
    
    genai.delete_file(sample_file.name)
    print(f"Chunk {chunk_index} completed. Length: {len(text)}")
    return text

# Main logic
reader = PdfReader(pdf_path)
total_pages = len(reader.pages)
print(f"Total pages: {total_pages}")

chunk_size = 10
extracted_texts = []

for i in range(0, total_pages, chunk_size):
    writer = PdfWriter()
    end_page = min(i + chunk_size, total_pages)
    for page_num in range(i, end_page):
        writer.add_page(reader.pages[page_num])
    
    chunk_filename = f"temp_chunk_{i}.pdf"
    with open(chunk_filename, "wb") as f:
        writer.write(f)
    
    try:
        text = extract_chunk(chunk_filename, i)
        extracted_texts.append(text)
    finally:
        if os.path.exists(chunk_filename):
            os.remove(chunk_filename)

full_text = "\n\n".join(extracted_texts)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_text)

print(f"Successfully wrote extracted content to {output_path}")
print(f"Total characters: {len(full_text)}")
