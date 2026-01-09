
import os
import sys
import time
import google.generativeai as genai
from google.api_core import exceptions
import re
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

    current_key_index = worker_id % len(api_keys)
    
    # INFINITE RETRY LOOP until success
    while True:
        # Loop through keys
        for i in range(len(api_keys)):
            key_index = (current_key_index + i) % len(api_keys)
            api_key = api_keys[key_index]
            
            genai.configure(api_key=api_key)

            try:
                safe_print(f"🚀 [Repair-Worker {worker_id} - {os.path.basename(pdf_path)}] Uploading...")
                uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
                
                # Wait for processing
                attempt_count = 0
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(2)
                    uploaded_file = genai.get_file(uploaded_file.name)
                    attempt_count += 1
                    if attempt_count > 30: # 60 seconds max wait for active state
                        break

                if uploaded_file.state.name == "FAILED":
                    raise Exception("File processing failed on Google Server.")

                safe_print(f"🧠 [Repair-Worker {worker_id} - {os.path.basename(pdf_path)}] Generating...")
                
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
                
                safe_print(f"✅ [Repair-Worker {worker_id}] Saved {os.path.basename(output_path)}")
                return True # Success! Break out of everything

            except Exception as e:
                safe_print(f"❌ [Repair-Worker {worker_id} - {os.path.basename(pdf_path)}] Error: {e}")
                if "503" in str(e) or "504" in str(e) or "429" in str(e) or "ResourceExhausted" in str(e):
                    safe_print(f"   ⏳ [Repair-Worker {worker_id}] Quota/Server Limit. Switching key & Sleeping 30s...")
                    time.sleep(30)
                    continue # Try next key
                else:
                    # Non-retriable error (maybe file invalid?)
                    # But actually for bulk operations, better to keep trying or log and skip?
                    # Let's retry anyway in case it's a transient network glitch
                    time.sleep(10)
                    continue

        # If we exhausted ALL keys and still failed, wait longer and restart key loop
        safe_print(f"😴 [Repair-Worker {worker_id}] All keys exhausted. Waiting 60s before retry loop...")
        time.sleep(60)

def main():
    base_dir = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/Academic_230317_084750-2_parts"
    api_keys = load_api_keys()
    print(f"Loaded {len(api_keys)} API keys.")

    # TARGET GAP: 48 to 65
    for i in range(47, 65): # 0-indexed: 47=part_48, 64=part_65
        part_num = i + 1
        pdf_filename = f"part_{part_num:02d}.pdf"
        md_filename = f"part_{part_num:02d}.md"
        pdf_path = os.path.join(base_dir, pdf_filename)
        output_path = os.path.join(base_dir, md_filename)

        print(f"🩹 Checking {md_filename} for Repair...")
        
        # Check for existing completed files to skip
        if os.path.exists(output_path):
             file_size = os.path.getsize(output_path)
             if file_size > 5000: # Increased check size to 5KB to avoid empty/error files
                 print(f"ℹ️ {md_filename} exists ({file_size} bytes). Skipping.")
                 continue
             else:
                 print(f"⚠️ {md_filename} exists but too small/corrupt. Repairing.")

        if os.path.exists(pdf_path):
             success = generate_markdown_from_pdf(pdf_path, output_path, api_keys, i)
        else:
             print(f"⚠️ {pdf_filename} missing. Skipping.")

if __name__ == "__main__":
    main()
