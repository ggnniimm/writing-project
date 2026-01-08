
import os
import sys
import time
import google.generativeai as genai

def load_api_keys():
    api_keys = []
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
            api_keys.append(value)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k_val: api_keys.append(k_val)
    return list(set(api_keys))

def convert_single(pdf_path, output_path):
    api_keys = load_api_keys()
    if not api_keys:
        print("No API keys found.")
        return

    genai.configure(api_key=api_keys[0]) # Use first key
    
    print(f"Uploading {pdf_path}...")
    uploaded_file = genai.upload_file(pdf_path, mime_type="application/pdf")
    
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(1)
        uploaded_file = genai.get_file(uploaded_file.name)
        
    if uploaded_file.state.name == "FAILED":
        print("Upload failed.")
        return

    print("Generating...")
    # Using 1.5 Pro for better quality on re-check
    model = genai.GenerativeModel('models/gemini-flash-latest')
    prompt = """
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
    
    response = model.generate_content([prompt, uploaded_file], stream=False)
    
    md_text = response.text
    # Cleanup markdown fences
    if md_text.startswith("```"):
        lines = md_text.splitlines()
        if lines[0].startswith("```"): lines = lines[1:]
        if lines and lines[-1].strip() == "```": lines = lines[:-1]
        md_text = "\n".join(lines)
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    
    print(f"Saved to {output_path}")

    try:
        uploaded_file.delete()
    except:
        pass

if __name__ == "__main__":
    pdf_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07/part_33.pdf"
    md_path = "/Users/mingsaksaengwilaipon/.gemini/antigravity/scratch/writing_project/etc/split_vol07/part_33.md"
    convert_single(pdf_path, md_path)
