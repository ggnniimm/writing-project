
import os
import sys
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_api_keys():
    keys = []
    # Check regular GEMINI_API_KEY
    if os.getenv("GEMINI_API_KEY"):
        keys.append(os.getenv("GEMINI_API_KEY"))
    
    # Check numbered keys from env
    i = 1
    while True:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            keys.append(key)
            i += 1
        else:
            break

    # Manual .env parsing (fallback)
    possible_paths = [
        ".env",
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    ]
    
    for env_path in possible_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY") and "=" in line:
                            k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if k_val:
                                keys.append(k_val)
            except Exception as e:
                print(f"⚠️ Error reading {env_path}: {e}")
    
    # Ensure uniqueness and validity
    unique_keys = list(set([k for k in keys if k and k.strip()]))
    return unique_keys

def extract_simple(pdf_path, output_path):
    api_keys = get_api_keys()
    if not api_keys:
        print("❌ No API Keys found!")
        return

    # Try keys in order (or random)
    for i, api_key in enumerate(api_keys):
        print(f"🔑 Attempting with Key #{i+1} (Mask: ...{api_key[-5:]})")
        genai.configure(api_key=api_key)
        
        try:
            print(f"🚀 Uploading {pdf_path}...")
            uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
            print(f"   Uploaded: {uploaded_file.name}")
            
            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                print("❌ File processing failed.")
                continue

            print("\n🧠 Generating content (No Stream)...")
            # Use the model that worked in the other script
            model = genai.GenerativeModel('models/gemini-flash-latest') 
            
            prompt_text = """
            You are an expert OCR engine.
            Convert this entire PDF document into Markdown.
            
            Rules:
            1. Extract ALL text verbatim. No summarization.
            2. PRESERVE THE VISUAL STRUCTURE and LAYOUT as much as possible using Markdown.
            3. FORCE TOC ALIGNMENT: For Table of Contents, ALWAYS keep the topic and its page number on the SAME LINE. If the text extraction naturally splits them, you must MERGE them back. Example: "Topic ... 123" NOT "Topic\n123".
            7. If a line would contain ONLY a number (likely a page number from a TOC), append it to the previous line instead of creating a new line.
            4. Do NOT wrap the result in JSON or code blocks (like ```markdown). Just return raw markdown text.
            5. If there are tables, format them as Markdown tables.
            6. PRESERVE ALL PAGE NUMBERS, even if they appear in headers or footers. Do not remove them.
            7. **FOOTNOTE FORMATTING**:
               - Identify footnote numbers in the text (often appearing as small numbers or Thai numerals like ๑, ๒) and format them as superscripts: <sup>1</sup>, <sup>2</sup>.
               - Format footnote DEFINITIONS (at the bottom of page) on their own line, starting with the superscript number: <sup>1</sup> Content...
               - Do NOT merge footnote definitions into the main text paragraph.
            """

            response = model.generate_content(
                [prompt_text, uploaded_file],
                stream=False  # Key change!
            )
            
            text = response.text
            
            # Cleanup Markdown wrappers
            if text.startswith("```"):
                lines = text.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].strip() == "```": lines = lines[:-1]
                text = "\n".join(lines)

            with open(output_path, "w", encoding='utf-8') as f:
                f.write(text)
                
            print(f"✅ Success! Written to {output_path}")
            
            # Cleanup
            try:
                uploaded_file.delete()
            except:
                pass
                
            return # Done
            
        except Exception as e:
            print(f"❌ Error with key {i+1}: {e}")
            continue

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 simple_extract.py <pdf_path> <output_path>")
        sys.exit(1)
        
    extract_simple(sys.argv[1], sys.argv[2])
