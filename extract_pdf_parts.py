#!/usr/bin/env python3
"""
Script to split a large PDF into parts, extract each part using Gemini,
and combine the results into a single markdown file.
"""

import os
import sys
import math
import time
import pypdf
import google.generativeai as genai

def load_api_keys():
    """Load all GEMINI API keys from environment and .env file."""
    api_keys = []
    
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
            api_keys.append(value)
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k_val:
                        api_keys.append(k_val)
    
    return list(set(api_keys))

def split_pdf(input_path, num_parts, output_dir):
    """Split a PDF into multiple parts."""
    reader = pypdf.PdfReader(input_path)
    total_pages = len(reader.pages)
    pages_per_part = math.ceil(total_pages / num_parts)
    
    print(f"📄 Total pages: {total_pages}")
    print(f"📦 Splitting into {num_parts} parts (~{pages_per_part} pages each)")
    
    part_files = []
    
    for i in range(num_parts):
        start_page = i * pages_per_part
        end_page = min((i + 1) * pages_per_part, total_pages)
        
        if start_page >= total_pages:
            break
            
        writer = pypdf.PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        part_filename = os.path.join(output_dir, f"part_{i+1:02d}.pdf")
        with open(part_filename, "wb") as f:
            writer.write(f)
        
        part_files.append({
            'path': part_filename,
            'start': start_page + 1,  # 1-indexed for display
            'end': end_page,
            'pages': end_page - start_page
        })
        print(f"   ✅ Part {i+1}: pages {start_page+1}-{end_page} ({end_page - start_page} pages)")
    
    return part_files

def extract_part(part_info, api_keys, current_key_index):
    """Extract content from a single PDF part using Gemini."""
    filepath = part_info['path']
    
    for i in range(len(api_keys)):
        key_index = (current_key_index + i) % len(api_keys)
        api_key = api_keys[key_index]
        
        print(f"   🔑 Using Key #{key_index + 1}")
        genai.configure(api_key=api_key)
        
        try:
            # Upload file
            print(f"   📤 Uploading...", end=" ", flush=True)
            uploaded_file = genai.upload_file(filepath, mime_type="application/pdf")
            
            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception("File processing failed")
            
            print("✅")
            
            # Generate content
            print(f"   🧠 Extracting...", end=" ", flush=True)
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt_text = """
            คุณเป็น OCR expert สำหรับภาษาไทย
            แปลง PDF นี้เป็น Markdown
            
            กฏ:
            1. Extract ข้อความทั้งหมดตามต้นฉบับ ห้าม summarize
            2. รักษาโครงสร้าง (headers, ตาราง, รายการ) 
            3. อย่าใส่ ```markdown หรือ code blocks ใดๆ ให้ output เป็น raw markdown
            4. ถ้ามีตาราง ให้ทำเป็น Markdown table
            5. ละเลข page ที่อยู่ header/footer แต่เก็บ heading ของเอกสาร
            """
            
            response = model.generate_content(
                [prompt_text, uploaded_file],
                stream=True
            )
            
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    print(".", end="", flush=True)
            
            print(" ✅")
            
            # Cleanup
            try:
                uploaded_file.delete()
            except:
                pass
            
            # Clean up markdown wrappers
            result = full_text.strip()
            if result.startswith("```"):
                lines = result.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                result = "\n".join(lines)
            
            return result, key_index
            
        except Exception as e:
            print(f" ❌ Error: {e}")
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str:
                print("   ⏳ Rate limit. Waiting & switching key...")
                time.sleep(30)
            elif "401" in err_str:
                print("   ⛔ Invalid key. Switching...")
            else:
                print(f"   ⚠️ Trying next key...")
                time.sleep(5)
            continue
    
    return None, current_key_index

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract_pdf_parts.py <pdf_path> [num_parts]")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    num_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    if not os.path.exists(input_pdf):
        print(f"❌ File not found: {input_pdf}")
        sys.exit(1)
    
    # Load API keys
    api_keys = load_api_keys()
    if not api_keys:
        print("❌ No GEMINI_API_KEY found")
        sys.exit(1)
    print(f"🔑 Loaded {len(api_keys)} API key(s)")
    
    # Create temp directory for parts
    base_name = os.path.splitext(os.path.basename(input_pdf))[0]
    temp_dir = os.path.join(os.path.dirname(input_pdf), f"_temp_{base_name}")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"📁 Temp dir: {temp_dir}")
    
    # Split PDF
    print("\n--- STEP 1: Splitting PDF ---")
    part_files = split_pdf(input_pdf, num_parts, temp_dir)
    
    # Extract each part
    print("\n--- STEP 2: Extracting Parts ---")
    all_content = []
    current_key_index = 0
    
    for idx, part_info in enumerate(part_files):
        print(f"\n📖 Part {idx+1}/{len(part_files)} (pages {part_info['start']}-{part_info['end']})")
        
        content, current_key_index = extract_part(part_info, api_keys, current_key_index)
        
        if content:
            all_content.append({
                'part': idx + 1,
                'start': part_info['start'],
                'end': part_info['end'],
                'content': content
            })
            print(f"   ✅ Extracted {len(content)} characters")
        else:
            print(f"   ❌ Failed to extract part {idx+1}")
            all_content.append({
                'part': idx + 1,
                'start': part_info['start'],
                'end': part_info['end'],
                'content': f"[EXTRACTION FAILED FOR PAGES {part_info['start']}-{part_info['end']}]"
            })
        
        # Small delay between parts to avoid rate limits
        time.sleep(3)
    
    # Combine results
    print("\n--- STEP 3: Combining Results ---")
    combined_markdown = ""
    
    for item in all_content:
        combined_markdown += f"\n\n<!-- Part {item['part']} - Pages {item['start']}-{item['end']} -->\n\n"
        combined_markdown += item['content']
    
    # Save combined result
    output_path = input_pdf.replace(".pdf", ".md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined_markdown.strip())
    
    print(f"\n✅ Combined output saved to: {output_path}")
    print(f"   Total characters: {len(combined_markdown)}")
    
    # Cleanup temp files
    print("\n🗑️ Cleaning up temp files...")
    for part_info in part_files:
        try:
            os.remove(part_info['path'])
        except:
            pass
    try:
        os.rmdir(temp_dir)
    except:
        pass
    
    print("✨ Done!")

if __name__ == "__main__":
    main()
