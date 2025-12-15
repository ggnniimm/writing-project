import os
import sys
import json
import time
import traceback
import google.generativeai as genai
from google.api_core import exceptions
from dotenv import load_dotenv
import re

def normalize_thai_digits(text):
    """Converts Thai digits to Arabic digits."""
    thai_digits = "๐๑๒๓๔๕๖๗๘๙"
    arabic_digits = "0123456789"
    trans = str.maketrans(thai_digits, arabic_digits)
    return text.translate(trans)

def determine_filename_and_path(content):
    """
    Analyzes content to determine the filename and target folder 
    based on document type and regex extraction of IDs.
    """
    content_sample = content[:5000] # Analyze first 5000 chars
    normalized_sample = normalize_thai_digits(content_sample)
    
    # 1. Supreme Administrative Court (ศาลปกครอง)
    if "ศาลปกครอง" in content_sample:
        # Pattern: คดีหมายเลขแดงที่ อ. 2050/2559 or similar
        # Regex: Look for "คดีหมายเลขแดงที่" then capture Number/Year
        match = re.search(r"คดีหมายเลขแดงที่\s*[^\d]*(\d+)/(\d+)", normalized_sample)
        if match:
             red_no = match.group(1)
             year = match.group(2)
             return f"ref_sac_{red_no}_{year}_full.md", "references/rulings_court"
        return "ref_sac_unknown.md", "references/rulings_court"

    # 2. Attorney General (OAG / อสส.)
    if "อัยการสูงสุด" in content_sample or "อสส" in content_sample:
        # Pattern: คำวินิจฉัยที่ 205/2561
        match = re.search(r"(?:คำวินิจฉัยที่|ที่)\s*(\d+)/(\d+)", normalized_sample)
        if match:
            no = match.group(1)
            year = match.group(2)
            return f"ref_oag_{no}_{year}.md", "references/rulings_attorney_general"
        return "ref_oag_unknown.md", "references/rulings_attorney_general"

    # 3. Committee (GWJ / กวจ.)
    if "คณะกรรมการวินิจฉัย" in content_sample or "กวจ" in content_sample or "กรมบัญชีกลาง" in content_sample or "ก.ว.จ." in content_sample:
        # Pattern: ว 123 (Circular)
        match_wo = re.search(r"[/\s]ว\s*(\d+)", normalized_sample)
        if match_wo:
             # Try to find year nearby? For now, just Vo number is often unique enough or append placeholder
             return f"ref_gwj_vo{match_wo.group(1)}.md", "references/rulings_committee"
        
        # Pattern: ที่ กค (กวจ) 0405.2/12345 ... วันที่ ... 2565
        # Extract Number after slash
        match_no = re.search(r"ที่\s*[^/]+/(\d+)", normalized_sample)
        # Extract Year (looking for 4 digits starting with 25xx)
        match_year = re.search(r"(\d{4})", normalized_sample) # First 4 digit usually header or date
        
        # Try to find specific "Dated ... B.E. 25xx" pattern if possible, but simplest is first 25xx
        match_year_25xx = re.search(r"(25\d{2})", normalized_sample)

        if match_no and match_year_25xx:
             return f"ref_gwj_{match_no.group(1)}_{match_year_25xx.group(1)}.md", "references/rulings_committee"
        
        if match_no:
             return f"ref_gwj_{match_no.group(1)}.md", "references/rulings_committee"
             
        return "ref_gwj_unknown.md", "references/rulings_committee"

    # Fallback
    return "suggested_name.md", "references/raw_pdfs"

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
    
    # User-requested Key (Default to 0)
    current_key_index = 0

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
            print("📡 Sending request to Gemini API (Stream mode)...")
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

                
                # 5. Agentic Auto-Renaming & Classification
                final_filename, target_subfolder = determine_filename_and_path(md_content)
                
                # Construct final path
                project_root = os.path.dirname(os.path.abspath(__file__))
                final_dir = os.path.join(project_root, target_subfolder)
                
                if not os.path.exists(final_dir):
                    print(f"⚠️ Target folder {target_subfolder} does not exist. Creating...")
                    os.makedirs(final_dir, exist_ok=True)
                
                final_path = os.path.join(final_dir, final_filename)
                
                # Move the file
                try:
                    os.rename(output_path, final_path)
                    print(f"🚚 Auto-Classified & Moved to: {target_subfolder}/{final_filename}")
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
                
        except StopIteration:
            print(f"⚠️ Generic StopIteration (Empty Stream) on Key #{current_key_index + 1}. Retrying...")
            time.sleep(2)
            continue

        except Exception as e:
            print(f"\n❌ Generation Error: {e}")
            traceback.print_exc()
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
