
import os
import sys
import time
import google.generativeai as genai
from google.api_core import exceptions
import re
import multiprocessing
import glob
import concurrent.futures

# ==================================================================================
# ⚙️ CONFIGURATION
# ==================================================================================
# Directory containing the split PDF parts (e.g., "etc/MyBook_parts")
BASE_DIR = "etc/Your_Book_Dir_parts" 

# Model to use (Flash is recommended for speed/cost)
MODEL_NAME = 'models/gemini-2.5-flash'

# Rate Limiting: Sleep time (seconds) after each successful generation to preserve quota
# Free Tier: ~15 RPM. With N workers, sleep should be sufficient to keep total RPM < 15.
# Recommended: 12s for safe buffer if using multiple keys.
SLEEP_PER_REQUEST = 12 
# ==================================================================================

def load_api_keys():
    """Lengths API keys from .env file in current or parent directory."""
    api_keys = []
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
    """
    Processes a single PDF file using the Gemini API.
    Isolated function for use in separate processes.
    """
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
        model = genai.GenerativeModel(MODEL_NAME)
        
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
        # Clean up markdown code block wrappers if present
        if final_markdown.startswith("```"):
            lines = final_markdown.splitlines()
            if lines[0].startswith("```"): lines = lines[1:]
            if lines and lines[-1].strip() == "```": lines = lines[:-1]
            final_markdown = "\n".join(lines)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_markdown)
        
        print(f"✅ [Worker {worker_id}] Saved {os.path.basename(output_path)}")
        time.sleep(SLEEP_PER_REQUEST) # Rate limit throttle
        return True

    except Exception as e:
        print(f"❌ [Worker {worker_id} - {os.path.basename(pdf_path)}] Error: {e}")
        time.sleep(5) # Short cool down on error
        return False

def worker_entry(args):
    """
    Entry point for worker process. 
    Handles logic to rotate keys if needed (though simple 1-1 mapping is preferred for simplicity).
    """
    pdf_path, output_path, api_keys, i = args
    
    # Simple Strategy: Assign one primary key based on worker index
    # If it fails, we could rotate, but for now we just retry with the same or next one.
    
    current_key_idx = i % len(api_keys)
    
    # Try up to len(api_keys) times (rotating through available keys)
    for attempt in range(len(api_keys)):
        idx = (current_key_idx + attempt) % len(api_keys)
        api_key = api_keys[idx]
        
        if process_file_full(pdf_path, output_path, api_key, i):
            return True
        else:
            print(f"   ⚠️ [Worker {i}] Request failed. Retrying with next available key...")
            time.sleep(SLEEP_PER_REQUEST) 
            
    return False

def main():
    # 1. Load Keys
    api_keys = load_api_keys()
    print(f"Loaded {len(api_keys)} API keys.")

    if not api_keys:
        print("❌ No API keys found in .env files.")
        sys.exit(1)

    # 2. Find Files
    if not os.path.exists(BASE_DIR):
        print(f"❌ Directory not found: {BASE_DIR}")
        print("   Please edit the 'BASE_DIR' variable at the top of this script.")
        sys.exit(1)

    pdf_files = sorted(glob.glob(os.path.join(BASE_DIR, "part_*.pdf")))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {BASE_DIR}")
        return

    print(f"Found {len(pdf_files)} parts to process in {BASE_DIR}")

    tasks = []
    
    # 3. Configure Parallel Execution
    # Best Practice: ONE worker per API key to maximize throughput while respecting individual key rate limits.
    max_workers = len(api_keys)
    if max_workers < 1: max_workers = 1
    
    print(f"🚀 Starting parallel extraction with {max_workers} processes...")
    print(f"   (Using ProcessPoolExecutor for isolation + {SLEEP_PER_REQUEST}s sleep per request)")

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        for i, pdf_path in enumerate(pdf_files):
            filename = os.path.basename(pdf_path)
            md_filename = filename.replace(".pdf", ".md")
            output_path = os.path.join(BASE_DIR, md_filename)

            # Resume Capability: Skip existing non-empty files
            if os.path.exists(output_path):
                 file_size = os.path.getsize(output_path)
                 if file_size > 1000:
                     print(f"ℹ️ {md_filename} exists ({file_size} bytes). Skipping.")
                     continue
                 else:
                     print(f"⚠️ {md_filename} exists but likely empty/broken. Overwriting.")

            tasks.append(executor.submit(worker_entry, (pdf_path, output_path, api_keys, i)))

        # Wait for completion
        for future in concurrent.futures.as_completed(tasks):
             pass

    print("🏁 Batch processing complete.")

if __name__ == "__main__":
    main()
