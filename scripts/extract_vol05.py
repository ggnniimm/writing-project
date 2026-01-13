
import os
import sys
import time
import google.generativeai as genai
from google.api_core import exceptions
import re
import multiprocessing
import glob
import concurrent.futures

# Global lock for printing is not useful across processes, need a different approach or just accept mixed output.
# We will just print natively, it might mix but that's fine for now.

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

def process_file_full(pdf_path, output_path, api_key, worker_id):
    # Setup for this process
    genai.configure(api_key=api_key)
    
    try:
        print(f"🚀 [Worker {worker_id} - {os.path.basename(pdf_path)}] Uploading...")
        uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
        
        # Wait for processing
        attempt_count = 0
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
            attempt_count += 1
            if attempt_count > 30: 
                 break

        if uploaded_file.state.name == "FAILED":
            raise Exception("File processing failed on Google Server.")

        print(f"🧠 [Worker {worker_id} - {os.path.basename(pdf_path)}] Generating...")
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

        response_stream = model.generate_content(
            [prompt_text, uploaded_file],
            stream=True
        )
        
        full_text = ""
        for chunk in response_stream:
            if chunk.text:
                full_text += chunk.text
        
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
        
        print(f"✅ [Worker {worker_id}] Saved {os.path.basename(output_path)}")
        time.sleep(12) # Throttle to ~5 RPM (12s + processing)
        return True

    except Exception as e:
        print(f"❌ [Worker {worker_id} - {os.path.basename(pdf_path)}] Error: {e}")
        time.sleep(60)
        return False

def worker_entry(args):
    pdf_path, output_path, api_keys, i = args
    # Assign specific key to this worker/task based on round-robin
    # Since we are in a process, we can configure genai safely for this process
    
    # Simple retry logic with key rotation if needed?
    # For now, just pick one key based on Index
    
    # Strategy: Try up to len(api_keys) times with rotation
    
    current_key_idx = i % len(api_keys)
    
    for attempt in range(len(api_keys)):
        idx = (current_key_idx + attempt) % len(api_keys)
        api_key = api_keys[idx]
        
        if process_file_full(pdf_path, output_path, api_key, i):
            return True
        else:
            print(f"   ⚠️ [Worker {i}] Retry with next key...")
            time.sleep(60)
            
    return False

def main():
    base_dir = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_310717_154727-2_parts"
    api_keys = load_api_keys()
    print(f"Loaded {len(api_keys)} API keys.")

    if not api_keys:
        print("❌ No API keys found.")
        sys.exit(1)

    pdf_files = sorted(glob.glob(os.path.join(base_dir, "part_*.pdf")))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {base_dir}")
        return

    tasks = []
    # Process Pool for isolation
    # Max workers = number of keys (1 per key) to strictly respect rate limits
    max_workers = len(api_keys)
    if max_workers < 1: max_workers = 1
    
    print(f"🚀 Starting parallel extraction with {max_workers} processes (Conservative Mode)...")

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        for i, pdf_path in enumerate(pdf_files):
            filename = os.path.basename(pdf_path)
            md_filename = filename.replace(".pdf", ".md")
            output_path = os.path.join(base_dir, md_filename)

            if os.path.exists(output_path):
                 file_size = os.path.getsize(output_path)
                 if file_size > 1000:
                     print(f"ℹ️ {md_filename} exists ({file_size} bytes). Skipping.")
                     continue
                 else:
                     print(f"⚠️ {md_filename} exists but too small. Overwriting.")

            tasks.append(executor.submit(worker_entry, (pdf_path, output_path, api_keys, i)))

        for future in concurrent.futures.as_completed(tasks):
             pass

    print("🏁 Batch processing complete.")

if __name__ == "__main__":
    main()
