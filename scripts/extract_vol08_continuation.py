import os
import sys
import time
import google.generativeai as genai
from google.api_core import exceptions
import re
from concurrent.futures import ThreadPoolExecutor
import threading

# Global lock for printing to avoid mixed output
print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

def load_api_keys():
    api_keys = []
    # Check environment variables
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
            api_keys.append(value)
    
    # Check .env file in parent directory
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k_val:
                        api_keys.append(k_val)
    return list(set(api_keys))

def generate_markdown_from_pdf(pdf_path, output_path, api_keys, worker_id):
    if not api_keys:
        safe_print("❌ Error: No API keys found.")
        return False

    success = False
    current_key_index = worker_id % len(api_keys)

    for i in range(len(api_keys)):
        key_index = (current_key_index + i) % len(api_keys)
        api_key = api_keys[key_index]
        
        genai.configure(api_key=api_key)

        try:
            safe_print(f"🚀 [Worker {worker_id} - {os.path.basename(pdf_path)}] Uploading...")
            uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
            
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception("File processing failed.")

            safe_print(f"🧠 [Worker {worker_id} - {os.path.basename(pdf_path)}] Generating using Gemini 2.5 Flash (Preview)...")
            model = genai.GenerativeModel('models/gemini-2.5-flash-preview-09-2025')
            
            prompt_text = """
            You are an expert OCR engine for Thai Administrative Court documents.
            Convert this PDF document into high-quality Markdown.
            
            Rules:
            1. Extract ALL text verbatim. No summarization.
            2. PRESERVE THE VISUAL STRUCTURE and LAYOUT (headers, footers, section numbers).
            3. FORCE TOC ALIGNMENT: For Table of Contents, keep the topic and its page number on the SAME LINE.
            4. Do NOT wrap the result in JSON or code blocks.
            5. Format tables as Markdown tables.
            6. Handle Thai numerals and script accurately.
            7. If a page is blank, mention [Blank Page].
            """

            response = model.generate_content(
                [prompt_text, uploaded_file],
                stream=False
            )
            
            full_text = response.text
            
            try:
                uploaded_file.delete()
            except:
                pass

            final_markdown = full_text.strip()
            # Clean up potential markdown code block wrapping
            if final_markdown.startswith("```"):
                lines = final_markdown.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].strip() == "```": lines = lines[:-1]
                final_markdown = "\n".join(lines)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_markdown)
            
            safe_print(f"✅ [Worker {worker_id}] Saved {os.path.basename(output_path)}")
            return True

        except Exception as e:
            safe_print(f"❌ [Worker {worker_id} - {os.path.basename(pdf_path)}] Error: {e}")
            if "429" in str(e) or "ResourceExhausted" in str(e):
                wait_time = 15 + (worker_id * 2) # Staggered longer wait
                safe_print(f"   ⏳ [Worker {worker_id}] Quota exceeded. Waiting {wait_time}s and switching key...")
                time.sleep(wait_time)
                continue
            else:
                time.sleep(10)
                continue

    safe_print(f"❌ [Worker {worker_id}] All keys failed for {os.path.basename(pdf_path)}")
    return False

def process_part(args):
    part_num, base_dir, api_keys, worker_id = args
    pdf_filename = f"part_{part_num:02d}.pdf"
    md_filename = f"part_{part_num:02d}.md"
    pdf_path = os.path.join(base_dir, pdf_filename)
    output_path = os.path.join(base_dir, md_filename)

    if not os.path.exists(pdf_path):
        safe_print(f"⚠️ {pdf_filename} not found. Skipping.")
        return

    if os.path.exists(output_path):
        safe_print(f"ℹ️ {md_filename} already exists. Skipping.")
        return

    generate_markdown_from_pdf(pdf_path, output_path, api_keys, worker_id)

def main():
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "etc", "split_vol08")
    api_keys = load_api_keys()
    
    if not api_keys:
        print("❌ Error: No API keys found! Please check your .env file or environment variables.")
        return

    print(f"Loaded {len(api_keys)} API keys.")

    # Target Parts 40 to 55 for Volume 8
    tasks = []
    for i, part_num in enumerate(range(40, 56)):
        tasks.append((part_num, base_dir, api_keys, i))

    # Number of parallel workers
    max_workers = 2 # Very conservative to avoid further rate/security flags
    
    print(f"🚀 Starting extraction for Volume 08 (Parts 40-55) with {max_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_part, tasks)
    
    print("\n🏁 Volume 08 Continuation process finished.")

if __name__ == "__main__":
    main()
