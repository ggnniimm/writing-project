import os
import sys
import json
import time
import traceback
import google.generativeai as genai
from google.api_core import exceptions
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
    # 1. Supreme Administrative Court (ศาลปกครอง)
    if "ศาลปกครอง" in content_sample:
        # Pattern: คดีหมายเลขแดงที่ อ. 104/2563 or similar
        # Regex: Look for "คดีหมายเลขแดงที่" then optional "อ." then Number then Year
        # Capture groups: 1=(Prefix e.g. อ.), 2=(Number with separators), 3=(Year)
        match = re.search(r"คดีหมายเลขแดงที่\s*(?:(อ\.|อ)\s*)?([\d.,]+)\s*/\s*(\d+)", normalized_sample)
        
        # Also check for Black Case Number (คดีหมายเลขดำที่) to infer prefix if missing in Red Case
        black_case_match = re.search(r"คดีหมายเลขดำที่\s*(?:(อ\.|อ)\s*)?([\d.,]+)\s*/\s*(\d+)", normalized_sample)
        has_black_case_prefix = False
        if black_case_match:
             bc_prefix = black_case_match.group(1)
             if bc_prefix and "อ" in bc_prefix:
                 has_black_case_prefix = True

        if match:
             prefix_raw = match.group(1)
             number_raw = match.group(2)
             year = match.group(3)
             
             # Handle Prefix
             prefix_str = ""
             if prefix_raw and "อ" in prefix_raw:
                 prefix_str = "o_"
             
             # Heuristic: If number starts with "1." (e.g. 1.104) and we have no prefix,
             # it is likely a mis-OCR of "อ." (which looks like 1 in some fonts/contexts or regex ambiguity)
             # User confirmed "1.104" -> "อ. 104" -> "o_104"
             if not prefix_str and number_raw.startswith("1."):
                 prefix_str = "o_"
                 number_raw = number_raw[2:] # Strip "1."
             
             # Heuristic 2: If we still have no prefix, but the Black Case Number had "อ.", assume it's an "o_" case.
             if not prefix_str and has_black_case_prefix:
                 prefix_str = "o_"

             number_clean = re.sub(r"[^\d]", "", number_raw)
             
             # Standardize prefix to 'o' for rulings (matches user request to follow folder convention)
             return f"ref_sac_o_{number_clean}_{year}.md", "references/rulings_court"
             
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
    # load_dotenv() # Removed to avoid dependency

    # 1. Get ALL API Keys
    api_keys = []
    
    # Check environment variables first
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
             api_keys.append(value)
    
    # Always check .env file as well to gather more keys
    # Process specific file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "raw_pdfs", "sac_o_558_2562.pdf")
    if os.path.exists(pdf_path):
        print(f"Processing single file: {pdf_path}")
        # Assuming process_pdf is the function that calls extract_and_name_with_gemini
        # This block seems to be intended for a main execution context, not inside this function.
        # For now, I'll just add the path definition as requested, but the `process_pdf` call
        # would create a recursive loop if `process_pdf` itself calls this function.
        # Given the instruction is "Update the file path in the main block", and this is inside
        # `extract_and_name_with_gemini`, I will only add the path definition.
        # If the intention was to add a main execution block, it should be outside this function.
        pass # Placeholder, as `process_pdf` is not defined here and would cause recursion.
    else:
        print(f"File not found: {pdf_path}")
    if True:
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

    # import pypdf removed (no longer needed)
    
    # 2. Check File Size & Strategy -> Switch to File API for ALL files (cleaner context)
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"📦 File size: {file_size_mb:.2f} MB")
    
    final_combined_markdown = ""

    # Reuse the retry logic but adapted for File API
    # We need to iterate keys at this level because File Upload + Generation are linked to the key.
    
    success = False
    
    for i in range(len(api_keys)):
        # Calculate index with offset based on start (rotation)
        key_index = (current_key_index + i) % len(api_keys)
        api_key = api_keys[key_index]
        
        print(f"🔑 Attempting with Key #{key_index + 1} (Mask: ...{api_key[-5:]})")
        genai.configure(api_key=api_key)
        
        try:
            # --- STEP 1: UPLOAD ---
            print("🚀 Uploading to Gemini File API...")
            if file_size_mb > 10:
                print("   (This is a large file, upload might take a moment...)")
                
            uploaded_file = genai.upload_file(filepath, mime_type="application/pdf")
            print(f"   Uploaded: {uploaded_file.display_name} ({uploaded_file.uri})")
            
            # --- STEP 2: WAIT FOR PROCESSING ---
            # Some files require processing (pdf usually quick, but video/large files need wait)
            while uploaded_file.state.name == "PROCESSING":
                print("   ⏳ Processing file on server...", end="\r")
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
                
            if uploaded_file.state.name == "FAILED":
                raise Exception("File processing failed on Google Server.")
                
            print(f"   ✅ File Ready: {uploaded_file.state.name}")

            # --- STEP 3: GENERATE ---
            print("🧠 Generating content...")
            
            model = genai.GenerativeModel('models/gemini-2.0-flash-lite-preview-02-05')
            
            prompt_text = """
            You are an expert OCR engine.
            Convert this entire PDF document into Markdown.
            
            Rules:
            1. Extract ALL text verbatim. No summarization.
            2. Preserve the structure (headers, tables, lists) as best as possible.
            3. Do NOT wrap the result in JSON or code blocks (like ```markdown). Just return raw markdown text.
            4. If there are tables, format them as Markdown tables.
            5. Ignore headers/footers that are just page numbers, but keep document headers.
            """

            # Use stream=True for responsiveness
            response = model.generate_content(
                [prompt_text, uploaded_file],
                stream=True
            )
            
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    print(".", end="", flush=True) # Progress indicator
            
            print("\n✅ Generation Complete.")
            
            final_combined_markdown = full_text.strip()
            
            # Cleanup Markdown wrappers if any
            if final_combined_markdown.startswith("```"):
                lines = final_combined_markdown.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].strip() == "```": lines = lines[:-1]
                final_combined_markdown = "\n".join(lines)
            
            # --- STEP 4: CLEANUP FILE ---
            try:
                uploaded_file.delete()
                print("🗑️  Remote file deleted.")
            except:
                pass

            success = True
            break # Exit key loop on success
            
        except Exception as e:
            print(f"\n❌ Catch Error on Key #{key_index + 1}: {e}")
            
            # Error Handling Pattern from original code
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str:
                print("   ⏳ Quota exceeded. Switching key...")
                time.sleep(2)
                continue # Try next key
            elif "401" in err_str or "API_KEY" in err_str:
                print("   ⛔ Invalid Key. Switching...")
                continue
            else:
                # Other errors (network, 500), maybe wait a bit then try next key or just fail?
                # For robustness, try next key if available
                print("   ⚠️ Unknown error. Trying next key just in case...")
                time.sleep(5)
                continue

    if not success:
        print("❌ All API keys failed or max retries reached.")
        return

    # --- SAVE RESULT ---
    if not final_combined_markdown:
        print("❌ Error: No content extracted.")
        return

    # Identify output filename
    # We'll use the Agentic determine_filename_and_path on the CONTENT.
    
    # Save to temp first
    temp_filename = f"extracted_{os.path.basename(filepath)}.md"
    output_dir = os.path.dirname(filepath)
    output_path = os.path.join(output_dir, temp_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_combined_markdown)
    
    print(f"✅ Success! Extracted to: {output_path}")

    # 5. Agentic Auto-Renaming & Classification
    final_filename, target_subfolder = determine_filename_and_path(final_combined_markdown)
    
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
            return # Stop if move failed

    # --- 6. Auto-Rename Source PDF ---
    try:
        new_pdf_filename = final_filename.replace(".md", ".pdf")
        # Use absolute paths to be safe
        abs_source_path = os.path.abspath(filepath)
        source_dir = os.path.dirname(abs_source_path)
        new_pdf_path = os.path.join(source_dir, new_pdf_filename)

        if abs_source_path != new_pdf_path:
            os.rename(abs_source_path, new_pdf_path)
            print(f"✨ Auto-Renamed Source PDF to: {new_pdf_filename}")
        else:
            print(f"✨ Source PDF already correctly named.")
            
    except Exception as pdf_err:
        print(f"⚠️ Could not rename source PDF: {pdf_err}")

def generate_content_with_retry(api_keys, start_key_index, inline_data, is_chunk=False):
    """
    Helper to handle API calls with key rotation and retries.
    Returns: extracted Markdown string (not JSON).
    """
    current_key_index = start_key_index
    genai.configure(api_key=api_keys[current_key_index])
    
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Prompt is slightly different for chunks vs full doc
    if is_chunk:
        prompt_text = """
        You are an expert OCR engine.
        Document Chunk to Markdown.
        Extract all text verbatim from this part. No summary. No analysis.
        Start immediately with the text content. Do NOT wrap in JSON. Do NOT use markdown code blocks like ```markdown.
        Just raw text/markdown.
        """
    else:
        prompt_text = """
        You are an expert OCR engine.
        Document to Markdown.
        Extract all text verbatim. No summary. No analysis.
        Start immediately with the text content. Do NOT wrap in JSON. Do NOT use markdown code blocks like ```markdown.
        Just raw text/markdown.
        """

    retry_delay = 5
    max_retries = 10

    for attempt in range(max_retries):
        try:
             # Use stream=True
            response_stream = model.generate_content(
                [prompt_text, inline_data],
                stream=True
            )
            
            full_text = ""
            for chunk in response_stream:
                try:
                    full_text += chunk.text
                except:
                    pass
            
            # Post-processing to ensure clean markdown
            raw_text = full_text.strip()
            
            # Remove ```markdown or ``` if present
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                raw_text = "\n".join(lines)
            
            # Also remove JSON wrapping if it accidentally returns JSON (legacy prompt habit)
            if raw_text.startswith("{") and '"content":' in raw_text:
                 try:
                     j = json.loads(raw_text)
                     return j.get("content", "")
                 except:
                     pass

            return raw_text

        except exceptions.ResourceExhausted as e:
            print(f"⏳ Rate limit hit on Key #{current_key_index + 1}.")
            if len(api_keys) > 1:
                current_key_index = (current_key_index + 1) % len(api_keys)
                print(f"🔄 Switching to Key #{current_key_index + 1}...")
                genai.configure(api_key=api_keys[current_key_index])
                time.sleep(10)
            else:
                time.sleep(20)
        
        except StopIteration:
            print("⚠️ StopIteration. Retrying...")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            if "503" in str(e) or "500" in str(e):
                time.sleep(5)
            else:
                if attempt == max_retries - 1:
                    return "" # Fail gracefully
                time.sleep(5)
    
    return ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gemini_pdf_to_md.py <filepath>")
        sys.exit(1)
    
    extract_and_name_with_gemini(sys.argv[1])
