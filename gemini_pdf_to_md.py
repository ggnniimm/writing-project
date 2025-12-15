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

    import pypdf
    
    # 2. Check File Size & Strategy
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"📦 File size: {file_size_mb:.2f} MB")

    # Strategy: 
    # < 5 MB: Inline (Fast)
    # > 5 MB: Split & Chunk (Stable)
    
    final_combined_markdown = ""
    
    if file_size_mb < 5.0:
        # --- STRATEGY A: Small File (Inline) ---
        print("⚡ Using Strategy: Small File (Inline)")
        with open(filepath, "rb") as f:
            file_data = f.read()

        mime_type = "application/pdf"
        inline_data = {"mime_type": mime_type, "data": file_data}
        
        final_combined_markdown = generate_content_with_retry(api_keys, 0, inline_data, is_chunk=False)

    else:
        # --- STRATEGY B: Large File (Split & Chunk) ---
        print("✂️ Using Strategy: Split & Chunk (pypdf)")
        print("   (This avoids timeouts and 'File too large' errors)")
        
        try:
            reader = pypdf.PdfReader(filepath)
            total_pages = len(reader.pages)
            chunk_size = 10  # Process 10 pages at a time
            print(f"📚 Total Pages: {total_pages}. Chunk size: {chunk_size} pages.")
            
            chunks_text = []
            
            for i in range(0, total_pages, chunk_size):
                chunk_start = i
                chunk_end = min(i + chunk_size, total_pages)
                print(f"\n� Processing Chunk {i//chunk_size + 1}/{((total_pages-1)//chunk_size) + 1} (Pages {chunk_start+1}-{chunk_end})...")
                
                # Create Temp Chunk PDF
                writer = pypdf.PdfWriter()
                for page_num in range(chunk_start, chunk_end):
                    writer.add_page(reader.pages[page_num])
                
                temp_chunk_path = f"temp_chunk_{i}.pdf"
                with open(temp_chunk_path, "wb") as f_out:
                    writer.write(f_out)
                
                # Read Temp PDF as Inline Data
                with open(temp_chunk_path, "rb") as f_in:
                    chunk_data = f_in.read()
                
                # Cleanup Temp PDF immediately
                try:
                    os.remove(temp_chunk_path)
                except:
                    pass

                inline_data = {"mime_type": "application/pdf", "data": chunk_data}
                
                # Generate for this chunk
                # Pass current_key_index reference if possible, but for simplicity let retry handle rotation
                # Ideally we want to persist key rotation across chunks
                chunk_md = generate_content_with_retry(api_keys, 0, inline_data, is_chunk=True)
                
                if chunk_md:
                    chunks_text.append(chunk_md)
                else:
                    print(f"⚠️ Warning: Chunk {chunk_start+1}-{chunk_end} returned empty text.")

                # Small cooldown between chunks
                print("💤 Cooling down (2s)...")
                time.sleep(2)
            
            # Combine all chunks
            print("\n🔗 Combining chunks...")
            final_combined_markdown = "\n\n".join(chunks_text)

        except Exception as e:
            print(f"❌ Error during PDF splitting/processing: {e}")
            traceback.print_exc()
            return

    # --- SAVE RESULT ---
    if not final_combined_markdown:
        print("❌ Error: No content extracted.")
        return

    # Try to parse filename from the FIRST chunk or the whole text if small
    # For large split files, 'final_combined_markdown' is just raw text combined.
    # We need to be careful: calculate filename from the first part usually.
    
    # Heuristic: If we used chunks, `final_combined_markdown` is likely just text, not JSON.
    # If we used inline (Strategy A), `generate_content_with_retry` might return JSON string or text?
    # Let's standardize `generate_content_with_retry` to return CLEAN MARKDOWN TEXT.

    # Identify output filename
    # We'll use the Agentic determine_filename_and_path on the CONTENT.
    
    # Save to temp first
    temp_filename = "extracted_full.md"
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
