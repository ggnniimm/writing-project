#!/usr/bin/env python3
"""
Simple Gemini PDF extractor without auto-classification/moving.
For use in multi-part workflows.
"""

import os
import sys
import time
import google.generativeai as genai

def extract_pdf_simple(pdf_path, output_path=None):
    """Extract PDF to MD using Gemini without classification."""

    # Load all unique keys
    api_keys = []
    
    # 1. From env var (priority)
    if os.environ.get('GEMINI_API_KEY'):
        api_keys.append(os.environ['GEMINI_API_KEY'])
        
    # 2. From .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if "GEMINI_API_KEY" in line and "=" in line:
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        k_val = parts[1].strip().strip('"').strip("'")
                        if k_val:
                            api_keys.append(k_val)
    
    # Remove duplicates and ensure we have a list
    unique_keys = []
    seen = set()
    for k in api_keys:
        if k not in seen:
            unique_keys.append(k)
            seen.add(k)
            
    api_keys = unique_keys
    
    if not api_keys:
        print("❌ Error: GEMINI_API_KEY not found")
        return False

    print(f"🔑 Found {len(api_keys)} API keys. Starting rotation strategy...")

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return False
    
    # Determine output path
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = os.path.dirname(pdf_path)
        output_path = os.path.join(output_dir, f"{base_name}.md")

    # Try each key
    for i, key in enumerate(api_keys):
        try:
            print(f"🔑 Attempting with Key #{i+1} ({key[:5]}...)...")
            genai.configure(api_key=key)
            
            # Upload
            print(f"🚀 Uploading: {os.path.basename(pdf_path)}")
            uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
            
            # Wait for processing
            start_wait = time.time()
            while uploaded_file.state.name == "PROCESSING":
                if time.time() - start_wait > 60:
                     raise Exception("Processing timeout")
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception("File processing failed")
            
            print(f"🧠 Generating content...")
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt_text = """
            You are an expert OCR engine.
            Convert this entire PDF document into Markdown.
            
            Rules:
            1. Extract ALL text verbatim. No summarization.
            2. PRESERVE ALL Thai characters exactly as they appear (เลขไทย: ๐-๙).
            3. Maintain document structure using Markdown.
            4. For Table of Contents, keep topic and page number on same line.
            5. Do NOT wrap in JSON or code blocks. Return raw markdown.
            6. Format tables as Markdown tables.
            7. PRESERVE page numbers in headers/footers.
            """
            
            # This is where 429 usually happens
            response = model.generate_content([prompt_text, uploaded_file], stream=True)
            
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    print(".", end="", flush=True)
            
            print("\n✅ Generation complete")
            
            # Cleanup
            try:
                uploaded_file.delete()
            except:
                pass
            
            # Save
            final_text = full_text.strip()
            
            # Remove markdown wrapper if present
            if final_text.startswith("```"):
                lines = final_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                final_text = "\n".join(lines)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            
            print(f"💾 Saved: {output_path}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Error with Key #{i+1}: {error_msg}")
            
            # Check for Rate Limit 429
            if "429" in error_msg or "Quota exceeded" in error_msg:
                print("⚠️  Rate Limit hit. Switching to next key...")
                continue # Try next key
            else:
                # If other error (e.g. network), maybe retry or fail?
                # For robustness in this specific task, let's treat it as failover-able if possible,
                # but usually non-429 errors might be persistent. 
                # Let's try next key anyway just in case it's account specific issues.
                print("⚠️  Error encountered. Trying next key...")
                continue

    print("❌ All API keys failed.")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_pdf_simple.py <pdf_path> [output_path]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = extract_pdf_simple(pdf_path, output_path)
    sys.exit(0 if success else 1)
