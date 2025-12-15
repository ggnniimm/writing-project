
import os
import sys
import json
import time
import google.generativeai as genai
from google.api_core import exceptions
from dotenv import load_dotenv

def extract_and_name_with_gemini(filepath):
    # 0. Load .env
    load_dotenv()

    # 1. Get ALL API Keys
    api_keys = []
    
    # Check environment variables first
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
             api_keys.append(value)
    
    # If not found in env vars, check .env file
    if not api_keys:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY") and "=" in line:
                        k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if k_val:
                            api_keys.append(k_val)
    
    # Deduplicate
    api_keys = list(set(api_keys))

    if not api_keys:
        print("❌ Error: GEMINI_API_KEY not found (checked env vars and .env).")
        sys.exit(1)

    print(f"🔑 Loaded {len(api_keys)} API Key(s).")
    
    # Target the specific new key provided by user
    target_key = "AIzaSyA6B76kpY0wHUxreOJAQljI-7tvhWDjIu0"
    found_key_index = -1
    for i, k in enumerate(api_keys):
        if k.strip() == target_key:
            found_key_index = i
            break
            
    if found_key_index != -1:
        current_key_index = found_key_index
        print(f"🔑 Found specific USER key at index {current_key_index}")
    else:
        # If not in list (e.g. env not reloaded), just use it directly
        print(f"⚠️ Specific key not found in loaded list. Using directly.")
        api_keys.append(target_key)
        current_key_index = len(api_keys) - 1

    print(f"🔑 DEBUG: Active Key Mask: ...{api_keys[current_key_index][-5:]}")
    genai.configure(api_key=api_keys[current_key_index])

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    print(f"🚀 Processing: {os.path.basename(filepath)}")

    # 1. Read file as inline data
    if os.path.getsize(filepath) > 20 * 1024 * 1024:
        print("❌ Error: File too large for inline processing (>20MB).")
        return

    with open(filepath, "rb") as f:
        file_data = f.read()

    # Create the content part for inline data
    # (Assuming PDF, but could detect mime type if needed)
    mime_type = "application/pdf"
    if filepath.lower().endswith(".jpg") or filepath.lower().endswith(".jpeg"):
        mime_type = "image/jpeg"
    elif filepath.lower().endswith(".png"):
        mime_type = "image/png"

    inline_data = {
        "mime_type": mime_type,
        "data": file_data
    }
    
    # 3. Generate Content
    # Using 'models/gemini-2.5-flash' as it is confirmed working with new key
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    prompt_text = """
    You are an expert OCR engine.
    Document to Markdown.
    Extract all text verbatim. No summary. No analysis.
    Output JSON: {"filename": "suggested_name.md", "content": "# Header\\nText..."}
    """

    retry_delay = 5
    max_retries = 15 # Increased retries for large tasks

    for attempt in range(max_retries):
        try:
            print(f"🤖 Generating content (Attempt {attempt+1}/{max_retries})... using Key #{current_key_index + 1}")
            # Use stream=True to detect if it's starting to work
            response_stream = model.generate_content(
                [prompt_text, inline_data],
                generation_config={"response_mime_type": "application/json"},
                stream=True
            )
            
            full_text = ""
            print("⏳ Receiving stream...", end="", flush=True)
            for chunk in response_stream:
                print(".", end="", flush=True)
                try:
                    full_text += chunk.text
                except Exception:
                    # sometimes last chunk has no text, just finish reason
                    pass
            print(" Done.")
            
            # 4. Parse & Save
            try:
                raw_text = full_text
                # Simple cleanup for markdown fences
                if raw_text.strip().startswith("```"):
                     import re
                     # Remove first occurring ```json (or just ```) and last ```
                     # This regex finds content between fences
                     match = re.search(r"```(?:json)?\s*(.*)\s*```", raw_text, re.DOTALL)
                     if match:
                         raw_text = match.group(1).strip()
                
                result_json = json.loads(raw_text)
                md_filename = result_json.get("filename", "extracted.md")
                md_content = result_json.get("content", "")

                if not md_content:
                    print("⚠️ Warning: Empty content returned.")
                    return

                # Save logic
                output_dir = os.path.dirname(filepath)
                output_path = os.path.join(output_dir, md_filename)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                print(f"✅ Success! Extracted to: {output_path}")

                # 5. Auto-Classification & Move
                target_subfolder = "references/raw_pdfs" # Default fallback
                
                # Simple keyword heuristics for Thai legal documents
                content_sample = md_content[:2000] # Check first 2000 chars
                if "อัยการสูงสุด" in content_sample or "อสส" in content_sample or "OAG" in content_sample:
                    target_subfolder = "references/rulings_attorney_general"
                elif "คณะกรรมการวินิจฉัย" in content_sample or "กวจ" in content_sample or "กรมบัญชีกลาง" in content_sample:
                    target_subfolder = "references/rulings_committee"
                elif "ศาลปกครอง" in content_sample or "คำพิพากษา" in content_sample:
                    target_subfolder = "references/rulings_court"
                
                # Construct final path
                # Assuming script is running from project root or references are relative to script
                project_root = os.path.dirname(os.path.abspath(__file__))
                final_dir = os.path.join(project_root, target_subfolder)
                
                if not os.path.exists(final_dir):
                    print(f"⚠️ Target folder {target_subfolder} does not exist. Creating...")
                    os.makedirs(final_dir, exist_ok=True)
                
                final_path = os.path.join(final_dir, md_filename)
                
                # Move the file
                try:
                    os.rename(output_path, final_path)
                    print(f"🚚 Auto-Classified & Moved to: {target_subfolder}/{md_filename}")
                except Exception as move_err:
                     print(f"⚠️ Could not move file: {move_err}")

                # Cleanup (No remote file to delete)
                # pass

                return

            except json.JSONDecodeError as json_err:
                print(f"❌ JSON Error: {json_err}")
                print(f"Raw text start: {full_text[:100]}...")
                with open("debug_failed_json.txt", "w", encoding="utf-8") as f:
                    f.write(full_text)
                print("📝 Saved full raw text to debug_failed_json.txt")
                # Retry if JSON is bad? Usually better to fail or try again.
            
        except exceptions.ResourceExhausted as e:
            print(f"⏳ Rate limit hit on Key #{current_key_index + 1}. Error: {e}")
            
            # Switch Key Strategy
            if len(api_keys) > 1:
                current_key_index = (current_key_index + 1) % len(api_keys)
                print(f"🔄 Switching to Key #{current_key_index + 1}...")
                genai.configure(api_key=api_keys[current_key_index])
                
                # Even when switching, wait a bit to avoid rapid-fire failures if both are limited
                # Increase delay if we are cycling through keys rapidly
                wait_time = max(retry_delay, 5) 
                print(f"⏳ Waiting {wait_time}s to let quotas cool down...")
                time.sleep(wait_time)
                
                # Increase retry delay for next time, in case we just hit it again
                retry_delay = min(retry_delay * 1.5, 60) # Cap at 60s
            else:
                # No backup key, must wait
                print(f"⏳ No backup key. Waiting {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                
        except Exception as e:
            print(f"❌ Generation Error: {e}")
            # If it's a 500 error, maybe retry.
            if "500" in str(e) or "503" in str(e):
                 time.sleep(5)
                 continue
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gemini_pdf_to_md.py <filepath>")
        sys.exit(1)
    
    extract_and_name_with_gemini(sys.argv[1])
