import os
import glob
import time
import sys
import google.generativeai as genai
from google.api_core import exceptions

# Config - Volume 9
input_dir = "etc/Academic_281019_141643_parts"
model_name = "models/gemini-2.5-flash"

def get_api_keys():
    api_keys = []
    # Env vars
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
            api_keys.append(value)
    # .env
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    k = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k: api_keys.append(k)
    return list(set(api_keys))

def extract_part(pdf_path, api_keys, start_key_idx):
    current_key_idx = start_key_idx
    
    while True: # Keep trying until success
        keys_failed_count = 0
        
        # Try all keys
        for attempt_key in range(len(api_keys)):
            idx = (current_key_idx + attempt_key) % len(api_keys)
            key = api_keys[idx]
            genai.configure(api_key=key)
            
            try:
                print(f"   Processing {os.path.basename(pdf_path)} with Key {idx+1} (Mask: ...{key[-5:]})")
                
                # Upload
                uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
                
                # Wait
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(1)
                    uploaded_file = genai.get_file(uploaded_file.name)
                
                if uploaded_file.state.name == "FAILED":
                    raise Exception("Upload failed state")
                    
                # Generate
                model = genai.GenerativeModel(model_name)
                prompt = """
                You are an expert OCR engine.
                Convert this PDF document into Markdown.
                
                Rules:
                1. Extract ALL text verbatim. No summarization.
                2. PRESERVE THE VISUAL STRUCTURE and LAYOUT as much as possible using Markdown.
                3. FORCE TOC ALIGNMENT: For Table of Contents, ALWAYS keep the topic and its page number on the SAME LINE.
                4. PRESERVE ALL PAGE NUMBERS, even if they appear in headers or footers. Do not remove them.
                5. Do NOT wrap result in ```markdown. Just return text.
                """
                
                response = model.generate_content([prompt, uploaded_file], stream=True)
                text = ""
                for chunk in response:
                    if chunk.text: text += chunk.text
                
                # Cleanup
                try: uploaded_file.delete()
                except: pass
                
                # Validate Text (basic check)
                if not text:
                    raise Exception("Empty response text")

                return text, idx # Return success and last used key index
                
            except Exception as e:
                print(f"   Error: {e}")
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    print("   Quota exceeded. Rotating key...")
                    time.sleep(2)
                else:
                    print("   Other error. Rotating key...")
                    time.sleep(5)
                keys_failed_count += 1
                
        # If loop finishes, all keys failed
        print("   ⚠️ All keys exhausted/failed. Sleeping 60s before retrying this file...")
        time.sleep(60)
        # Shift start key to distribute load
        current_key_idx = (current_key_idx + 1) % len(api_keys)

def main():
    api_keys = get_api_keys()
    if not api_keys:
        print("No API Keys found!")
        return
        
    print(f"Loaded {len(api_keys)} keys.")
    
    parts = sorted(glob.glob(os.path.join(input_dir, "Academic_281019_141643_part_*.pdf")))
    current_key_idx = 0
    
    print(f"Found {len(parts)} parts to process.")
    
    for pdf_path in parts:
        md_path = pdf_path.replace(".pdf", ".md")
        if os.path.exists(md_path):
            print(f"Skipping {os.path.basename(pdf_path)} (MD exists)")
            continue
            
        print(f"Starting {os.path.basename(pdf_path)}...")
        content, used_key_idx = extract_part(pdf_path, api_keys, current_key_idx)
        
        if content:
            with open(md_path, "w", encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Saved {os.path.basename(md_path)}")
            current_key_idx = used_key_idx # Update preference to working key
        else:
            print(f"❌ Failed to extract {os.path.basename(pdf_path)}")
            time.sleep(10) # Cool down a bit
            continue
    
    print("\n✨ Extraction complete!")

if __name__ == "__main__":
    main()
