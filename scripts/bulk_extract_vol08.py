
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
    # Check current dir and parent dir for .env
    possible_paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    ]
    
    for env_path in possible_paths:
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

    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    # safe_print(f"📦 [Worker {worker_id}] Processing {os.path.basename(pdf_path)} ({file_size_mb:.2f} MB)")

    # Simple strategy: worker_id determines starting key to spread load
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

            safe_print(f"🧠 [Worker {worker_id} - {os.path.basename(pdf_path)}] Generating...")
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt_text = """
            You are an expert OCR engine.
            Convert this entire PDF document into Markdown.
            
            Rules:
            1. Extract ALL text verbatim. No summarization.
            2. PRESERVE THE VISUAL STRUCTURE and LAYOUT as much as possible using Markdown.
            3. FORCE TOC ALIGNMENT: For Table of Contents, ALWAYS keep the topic and its page number on the SAME LINE.
            4. Do NOT wrap the result in JSON or code blocks. Just return raw markdown text.
            5. If there are tables, format them as Markdown tables.
            6. PRESERVE ALL PAGE NUMBERS, even if they appear in headers or footers. Do not remove them.
            """

            # Do not use stream=True for parallel to avoid mixed dot output
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
                safe_print(f"   ⏳ [Worker {worker_id}] Quota exceeded. Switching key...")
                time.sleep(5)
                continue
            else:
                time.sleep(5)
                continue

    safe_print(f"❌ [Worker {worker_id}] Failed to process {os.path.basename(pdf_path)}")
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
    print(f"Loaded {len(api_keys)} API keys.")

    if not api_keys:
        print("❌ No API keys found in .env files.")
        sys.exit(1)

    # List of tasks: Parts 1 to 55
    tasks = []
    num_parts = 55 # based on 1088 pages / 20
    for i in range(num_parts):
        part_num = i + 1
        tasks.append((part_num, base_dir, api_keys, i))

    # Use ThreadPoolExecutor
    # 5 workers seems reasonable based on previous usage
    max_workers = 5
    
    # Use ThreadPoolExecutor
    # Sequential execution to avoid 403/429 errors
    max_workers = 1
    
    print(f"Running with {max_workers} workers for {len(tasks)} parts (Sequential Mode)...")
    
    # We can still use ThreadPoolExecutor with 1 worker, or just a loop.
    # Loop is safer for debugging.
    for task in tasks:
        process_part(task)
        time.sleep(2) # Cooldown between files

if __name__ == "__main__":
    main()
