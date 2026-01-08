
import os
import sys
import google.generativeai as genai

# Manual .env parsing logic
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

    # Manual .env parsing
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
    
    return list(set([k for k in keys if k and k.strip()]))

def convert_text_to_md(input_path, output_path):
    api_keys = get_api_keys()
    if not api_keys:
        print("❌ No API Keys found!")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return

    # Try keys
    for i, api_key in enumerate(api_keys):
        print(f"🔑 Attempting with Key #{i+1} (Mask: ...{api_key[-5:]})")
        genai.configure(api_key=api_key)
        
        try:
            print(f"🧠 formatting text ({len(raw_text)} chars)...")
            model = genai.GenerativeModel('models/gemini-flash-latest')
            
            prompt_text = f"""
            You are an expert OCR cleanup assistant.
            Convert the following RAW TEXT (extracted from a PDF) into clear, well-formatted MARKDOWN.
            
            Input Text:
            {raw_text}
            
            Rules:
            1. PRESERVE ALL CONTENT VERBATIM. Do not summarize or delete text.
            2. Fix line breaks that split sentences unnecessarily (common in PDF extraction).
            3. PRESERVE VISUAL STRUCTURE (headers, paragraphs).
            4. **FOOTNOTES**:
                - Identify footnote references in the text (e.g. 1, ๑) and format as <sup>1</sup>.
                - Place footnote definitions on their own lines at the end of the relevant section/page, formatted as: <sup>1</sup> Definition...
            5. **NUMERALS**:
                - Be careful not to confuse Thai numerals (๑-๙) with symbols. Preserve them as is if they are numbers.
            6. Return ONLY the Markdown content. No ```markdown wrapper.
            """

            response = model.generate_content(
                prompt_text,
                stream=False
            )
            
            md_content = response.text
            
            # Cleanup wrappers
            if md_content.startswith("```"):
                lines = md_content.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].strip() == "```": lines = lines[:-1]
                md_content = "\n".join(lines)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            print(f"✅ Success! Written to {output_path}")
            return
            
        except Exception as e:
            print(f"❌ Error with key {i+1}: {e}")
            continue

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 convert_txt_to_md.py <input_txt> <output_md>")
        sys.exit(1)
        
    convert_text_to_md(sys.argv[1], sys.argv[2])
